"""
Capsule Routes (MongoDB + GridFS/Cloudinary)

All capsule operations including creation, retrieval, update, delete, and unlock.
"""

import os
import traceback
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from io import BytesIO
from services.auth_service import require_auth
from services.encryption_service import EncryptionService
from services.capsule_service import CapsuleService
from services.email_service import EmailService
from pymongo import MongoClient
from bson import ObjectId
from utils.validators import validate_unlock_date

capsule_bp = Blueprint('capsule', __name__)

def get_db():
    """Get MongoDB database instance."""
    uri = os.getenv('MONGO_URI')
    client = MongoClient(uri)
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']

_db = get_db()
_encryption = EncryptionService()
_capsules = CapsuleService(_db, _encryption)
_email_service = EmailService()


@capsule_bp.route('/capsules', methods=['POST'])
@require_auth
def create_capsule():
    """
    Create a new time capsule.
    
    Expected form fields:
    - unlock_date (required): ISO 8601 datetime string
    - description (optional): Text description
    - recipient_id (optional): MongoDB ObjectId as string
    - recipient_name (optional): User display name
    - recipient_email (optional): Email address
    - file (optional): File to upload
    
    Must provide either description OR file, and one of recipient_id/recipient_name/recipient_email.
    """
    try:
        user_id = request.user['uid']
        
        # ========== VALIDATION ==========
        
        # 1. Validate unlock_date
        unlock_date_str = request.form.get('unlock_date')
        if not unlock_date_str:
            return jsonify({'error': 'Unlock date is required'}), 400
        
        try:
            unlock_date = datetime.fromisoformat(unlock_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid unlock_date format. Use ISO 8601 format (e.g., 2026-12-31T23:59:59)'}), 400
        
        # User can set ANY unlock date (past, present, or future)
        # Capsules with past dates will be immediately unlockable
        
        # 2. Validate recipient (at least one of the three)
        recipient_id = request.form.get('recipient_id')
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get('recipient_email')
        
        if not recipient_id and not recipient_name and not recipient_email:
            return jsonify({'error': 'Recipient is required. Provide recipient_id, recipient_name, or recipient_email.'}), 400
        
        # 4. Resolve recipient (for registered users)
        recipient_doc = None
        resolved_recipient_id = None
        
        if recipient_id:
            try:
                recipient_obj_id = ObjectId(recipient_id)
            except Exception:
                return jsonify({'error': 'Invalid recipient_id format'}), 400
            recipient_doc = _db.get_collection('users').find_one({'_id': recipient_obj_id})
            if not recipient_doc:
                return jsonify({'error': 'Recipient not found. User may have been deleted.'}), 404
            resolved_recipient_id = str(recipient_doc['_id'])
            
            # Prevent self-sending
            if resolved_recipient_id == user_id:
                return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
                
        elif recipient_name:
            recipient_doc = _db.get_collection('users').find_one({'display_name': recipient_name})
            if not recipient_doc:
                return jsonify({'error': 'No user found with that display name'}), 404
            resolved_recipient_id = str(recipient_doc['_id'])
            
            if resolved_recipient_id == user_id:
                return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
                
        elif recipient_email:
            # For external recipients, validate it's not the sender's own email
            try:
                sender_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            except Exception:
                sender_obj_id = user_id
            sender_doc = _db.get_collection('users').find_one({'_id': sender_obj_id})
            if sender_doc and sender_doc.get('email'):
                if sender_doc['email'].lower() == recipient_email.lower():
                    return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
        
        # 5. Validate description vs file
        description = request.form.get('description', '').strip() or None
        file_data = None
        filename = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename and file.filename != '':
                file_data = file.read()
                filename = secure_filename(file.filename)
        
        # At least one of description or file must be provided
        if not file_data and not description:
            return jsonify({'error': 'Either a file or description must be provided'}), 400
        
        # ========== CREATE CAPSULE ==========
        
        try:
            result = _capsules.create_capsule(
                user_id=user_id,
                unlock_date=unlock_date,
                description=description,
                recipient_id=resolved_recipient_id,
                file_data=file_data,
                filename=filename,
                recipient_email=recipient_email,
            )
        except ValueError as ve:
            # Re-raise validation errors from service
            return jsonify({'error': str(ve)}), 400
        except Exception as svc_error:
            current_app.logger.error(f"Capsule service error: {svc_error}")
            return jsonify({'error': f'Failed to create capsule: {str(svc_error)}'}), 500
        
        # ========== SEND NOTIFICATION EMAIL ==========
        
        try:
            # Get sender info
            sender_doc = _db.get_collection('users').find_one({'_id': ObjectId(user_id)})
            sender_name = sender_doc.get('display_name') if sender_doc else None
            
            # Send to registered user
            if recipient_doc and recipient_doc.get('email'):
                _email_service.send_capsule_created_notification(
                    recipient_email=recipient_doc['email'],
                    recipient_name=recipient_doc.get('display_name'),
                    sender_name=sender_name,
                    unlock_date=unlock_date,
                )
            # Send to external recipient
            elif recipient_email:
                _email_service.send_capsule_created_external_notification(
                    recipient_email=recipient_email,
                    sender_name=sender_name,
                    unlock_date=unlock_date,
                )
        except Exception as email_error:
            current_app.logger.warning(f"Failed to send creation email: {email_error}")
            # Don't fail capsule creation for email errors
        
        return jsonify(result), 201
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in create_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules', methods=['GET'])
@require_auth
def get_capsules():
    """
    Get all capsules for the current user.
    
    Query params:
    - include_locked (default: true): Include locked capsules
    - page (default: 1): Page number
    - limit (default: 20): Items per page (max: 100)
    """
    try:
        user_id = request.user['uid']
        
        # Parse and validate pagination params
        try:
            page = max(1, int(request.args.get('page', 1)))
            limit = min(100, max(1, int(request.args.get('limit', 20))))
        except ValueError:
            page = 1
            limit = 20
        
        include_locked = request.args.get('include_locked', 'true').lower() == 'true'
        
        # Get capsules
        try:
            all_items = _capsules.get_user_capsules(user_id, include_locked=include_locked)
        except Exception as svc_error:
            current_app.logger.error(f"Failed to get capsules: {svc_error}")
            return jsonify({'error': 'Failed to retrieve capsules'}), 500
        
        # Paginate
        total_count = len(all_items)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        skip = (page - 1) * limit
        paginated_items = all_items[skip:skip + limit]
        
        return jsonify({
            'capsules': paginated_items,
            'count': len(paginated_items),
            'total': total_count,
            'page': page,
            'limit': limit,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in get_capsules")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['GET'])
@require_auth
def get_capsule(capsule_id):
    """Get a specific capsule by ID."""
    try:
        user_id = request.user['uid']
        
        # Validate capsule_id format (UUID)
        try:
            capsule_uuid = str(capsule_id)  # Should be valid UUID
        except Exception:
            return jsonify({'error': 'Invalid capsule ID format'}), 400
        
        try:
            doc = _capsules.get_capsule_metadata(capsule_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to get capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to retrieve capsule'}), 500
        
        # Check access
        if doc.get('user_id') != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        
        return jsonify(doc), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in get_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>/unlock', methods=['POST'])
@require_auth
def unlock_capsule(capsule_id):
    """Unlock a capsule."""
    try:
        user_id = request.user['uid']
        current_time = datetime.utcnow()
        
        # Get metadata first
        try:
            metadata = _capsules.get_capsule_metadata(capsule_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to get capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to retrieve capsule'}), 500
        
        # Check access - only recipient can unlock (not the sender/owner)
        if metadata.get('recipient_id') != user_id:
            return jsonify({'error': 'Only the recipient can unlock this capsule'}), 403
        
        # Check unlock date
        unlock_date = metadata.get('unlock_date')
        if isinstance(unlock_date, str):
            unlock_date = datetime.fromisoformat(unlock_date.replace('Z', '+00:00'))
        
        if unlock_date > current_time:
            return jsonify({
                'error': 'Capsule is not ready to be unlocked yet',
                'unlock_date': unlock_date.isoformat(),
                'current_time': current_time.isoformat()
            }), 400
        
        # Unlock
        try:
            result = _capsules.unlock_capsule(capsule_id)
        except Exception as svc_error:
            current_app.logger.error(f"Failed to unlock capsule {capsule_id}: {svc_error}")
            return jsonify({'error': f'Failed to unlock capsule: {str(svc_error)}'}), 500
        
        # Send email notification to recipient if this is a recipient unlocking
        is_recipient = metadata.get('recipient_id') == user_id
        if is_recipient:
            try:
                # Get recipient info
                recipient_email = metadata.get('recipient_email')
                recipient_name = None
                sender_name = metadata.get('sender_name')
                
                if not recipient_email:
                    # Look up recipient in users
                    if metadata.get('recipient_id'):
                        recipient_doc = _db.users.find_one({'uid': metadata['recipient_id']})
                        if recipient_doc:
                            recipient_email = recipient_doc.get('email')
                            recipient_name = recipient_doc.get('display_name')
                
                # Get sender info
                if metadata.get('user_id') and not sender_name:
                    sender_doc = _db.users.find_one({'uid': metadata['user_id']})
                    if sender_doc:
                        sender_name = sender_doc.get('display_name')
                
                # Send email
                if recipient_email:
                    _email_service.send_capsule_unlocked_notification(
                        recipient_email=recipient_email,
                        recipient_name=recipient_name,
                        sender_name=sender_name,
                        unlock_date=unlock_date,
                    )
                    current_app.logger.info(f"Unlock notification email sent to {recipient_email}")
            except Exception as email_error:
                current_app.logger.error(f"Failed to send unlock email: {email_error}")
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in unlock_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['PUT'])
@require_auth
def update_capsule(capsule_id):
    """Update capsule metadata or file."""
    try:
        user_id = request.user['uid']
        
        # Check if it's multipart/form-data (file upload) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            description = request.form.get('description')
            unlock_date_str = request.form.get('unlock_date')
            
            file_data = None
            filename = None
            if 'file' in request.files:
                file = request.files['file']
                if file.filename and file.filename != '':
                    file_data = file.read()
                    filename = secure_filename(file.filename)
        else:
            data = request.get_json() or {}
            description = data.get('description')
            unlock_date_str = data.get('unlock_date')
            file_data = None
            filename = None
        
        # Parse unlock date if provided
        unlock_date = None
        if unlock_date_str:
            try:
                unlock_date = datetime.fromisoformat(unlock_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid unlock_date format'}), 400
        
        # Validate description
        if description == '':
            description = None
        
        try:
            result = _capsules.update_capsule(
                capsule_id=capsule_id,
                user_id=user_id,
                description=description,
                unlock_date=unlock_date,
                file_data=file_data,
                filename=filename
            )
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as svc_error:
            current_app.logger.error(f"Failed to update capsule {capsule_id}: {svc_error}")
            return jsonify({'error': f'Failed to update capsule: {str(svc_error)}'}), 500
        
        # Send email notification if unlock date was updated
        old_unlock_date = result.get('old_unlock_date')
        current_app.logger.info(f"DEBUG: Update capsule {capsule_id}: old_date={old_unlock_date}, new_date={unlock_date}")
        
        if unlock_date and old_unlock_date and old_unlock_date != unlock_date:
            try:
                # Get capsule info for email
                capsule_doc = _db.capsules.find_one({'capsule_id': capsule_id})
                recipient_email = capsule_doc.get('recipient_email')
                recipient_id = capsule_doc.get('recipient_id')
                
                current_app.logger.info(f"DEBUG: recipient_email={recipient_email}, recipient_id={recipient_id}")
                
                if recipient_email:
                    # Get sender name from users collection
                    sender_name = None
                    if recipient_id:
                        sender_doc = _db.users.find_one({'uid': user_id})
                        sender_name = sender_doc.get('name') if sender_doc else None
                    
                    # Get recipient name if registered
                    recipient_name = None
                    if recipient_id:
                        recipient_doc = _db.users.find_one({'uid': recipient_id})
                        recipient_name = recipient_doc.get('name') if recipient_doc else None
                    
                    current_app.logger.info(f"DEBUG: Sending email to {recipient_email}, old={old_unlock_date}, new={unlock_date}")
                    
                    # Send email notification
                    _email_service.send_capsule_date_updated_notification(
                        recipient_email=recipient_email,
                        recipient_name=recipient_name,
                        sender_name=sender_name,
                        old_unlock_date=old_unlock_date,
                        new_unlock_date=unlock_date
                    )
                    current_app.logger.info(f"Date update notification sent for capsule {capsule_id}")
                else:
                    current_app.logger.warning(f"No recipient_email found for capsule {capsule_id}, skipping email")
            except Exception as email_error:
                current_app.logger.error(f"Failed to send date update email: {email_error}")
                # Don't fail the update if email fails
        else:
            current_app.logger.info(f"No date change detected or no old date, skipping email")
        
        return jsonify({
            'message': 'Capsule updated successfully',
            'capsule': result
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in update_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['DELETE'])
@require_auth
def delete_capsule(capsule_id):
    """Delete a capsule."""
    try:
        user_id = request.user['uid']
        
        try:
            _capsules.delete_capsule(capsule_id, user_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to delete capsule {capsule_id}: {svc_error}")
            return jsonify({'error': f'Failed to delete capsule: {str(svc_error)}'}), 500
        
        return jsonify({'message': 'Capsule deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in delete_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>/metadata', methods=['GET'])
@require_auth
def get_capsule_metadata(capsule_id):
    """Get capsule metadata without the file content."""
    try:
        user_id = request.user['uid']
        
        try:
            doc = _capsules.get_capsule_metadata(capsule_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to get capsule metadata {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to retrieve capsule metadata'}), 500
        
        if doc.get('user_id') != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        
        return jsonify(doc), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in get_capsule_metadata")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>/preview', methods=['GET'])
@require_auth
def preview_capsule(capsule_id):
    """
    Preview a locked capsule (returns metadata only, not file content).
    This is used to show the capsule preview before unlocking.
    """
    try:
        user_id = request.user['uid']
        
        try:
            doc = _capsules.get_capsule_metadata(capsule_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to preview capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to preview capsule'}), 500
        
        # Check access
        if doc.get('user_id') != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        
        # Return preview info (no file content)
        preview_data = {
            'capsule_id': doc.get('capsule_id'),
            'description': doc.get('description'),
            'filename': doc.get('filename'),
            'capsule_type': doc.get('capsule_type'),
            'unlock_date': doc.get('unlock_date'),
            'is_unlocked': doc.get('is_unlocked'),
            'sender_id': doc.get('user_id'),
            'created_at': doc.get('created_at'),
        }
        
        return jsonify(preview_data), 200
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in preview_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>/preview-edit', methods=['GET'])
@require_auth
def preview_edit_capsule(capsule_id):
    """
    Preview a capsule for editing - returns file content as base64.
    Owner can view locked capsules.
    """
    try:
        user_id = request.user['uid']
        
        try:
            preview_data = _capsules.get_file_preview_for_edit(capsule_id, user_id)
            return jsonify(preview_data), 200
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as svc_error:
            current_app.logger.error(f"Failed to preview edit capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to preview capsule'}), 500
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in preview_edit_capsule")
        return jsonify({'error': 'Internal server error'}), 500


@capsule_bp.route('/capsules/<capsule_id>/download', methods=['GET'])
@require_auth
def download_capsule(capsule_id):
    """Download a capsule file. Owner can download locked capsules for editing."""
    try:
        user_id = request.user['uid']
        
        # Verify ownership
        try:
            doc = _capsules.get_capsule_metadata(capsule_id)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 404
        except Exception as svc_error:
            current_app.logger.error(f"Failed to get capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to retrieve capsule'}), 500
        
        # Check if user is owner or sender (can download locked capsules for editing)
        is_owner = doc.get('user_id') == user_id or doc.get('sender_id') == user_id
        
        if not is_owner and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        
        # Get decrypted file data (allow owner to download locked capsules)
        try:
            file_data, filename, content_type = _capsules.get_decrypted_file_data(
                capsule_id,
                allow_locked_for_owner=is_owner,
                user_id=user_id
            )
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as svc_error:
            current_app.logger.error(f"Failed to decrypt capsule {capsule_id}: {svc_error}")
            return jsonify({'error': 'Failed to decrypt capsule'}), 500
        
        # Create file-like object from bytes
        file_obj = BytesIO(file_data)
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.exception("Unexpected error in download_capsule")
        return jsonify({'error': 'Internal server error'}), 500


# ========== DEBUG ENDPOINTS ==========

@capsule_bp.route('/debug/services', methods=['GET'])
def debug_services():
    """Debug endpoint to check all services."""
    results = {}
    
    # Test encryption
    try:
        enc = EncryptionService()
        results['encryption'] = {'status': 'ok', 'key_length': len(enc.key)}
    except Exception as e:
        results['encryption'] = {'status': 'error', 'message': str(e)}
    
    # Test capsule service
    try:
        cap = CapsuleService(_db, enc)
        results['capsule'] = {
            'status': 'ok',
            'cloudinary_available': cap.cloudinary_storage is not None,
            'gridfs_available': hasattr(cap, 'fs')
        }
    except Exception as e:
        results['capsule'] = {'status': 'error', 'message': str(e)}
    
    # Test MongoDB
    try:
        _db.command('ping')
        results['mongodb'] = {'status': 'ok'}
    except Exception as e:
        results['mongodb'] = {'status': 'error', 'message': str(e)}
    
    return jsonify(results)


@capsule_bp.route('/debug/test-create', methods=['POST'])
def debug_test_create():
    """Debug endpoint to test encryption."""
    try:
        enc = EncryptionService()
        test_data = b"Hello World"
        encrypted = enc.encrypt_data(test_data)
        decrypted = enc.decrypt_data(encrypted['encrypted_data'], encrypted['iv'])
        
        return jsonify({
            'status': 'ok',
            'encryption_test': 'passed',
            'decrypted_match': test_data == decrypted
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@capsule_bp.route('/debug/create-capsule', methods=['POST'])
def debug_create_capsule():
    """Debug endpoint to test capsule creation with file upload."""
    try:
        # Test with file data
        test_file_data = b"This is test content for Cloudinary upload - " + datetime.utcnow().isoformat().encode()
        result = _capsules.create_capsule(
            user_id='test_user',
            unlock_date=datetime.utcnow(),
            description='Test capsule with file - testing Cloudinary',
            recipient_id=None,
            file_data=test_file_data,
            filename='debug_test.txt',
            recipient_email=None,
        )
        return jsonify({'status': 'ok', 'result': result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
