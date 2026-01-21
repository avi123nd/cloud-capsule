"""
Capsule Routes (MongoDB + GridFS)
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
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
    try:
        user_id = request.user['uid']
        unlock_date_str = request.form.get('unlock_date')
        if not unlock_date_str:
            return jsonify({'error': 'Unlock date is required'}), 400
        
        # Validate unlock date
        date_valid, date_error, unlock_date = validate_unlock_date(unlock_date_str)
        if not date_valid:
            return jsonify({'error': date_error}), 400
        
        description = request.form.get('description', '').strip()
        recipient_id = request.form.get('recipient_id')
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get('recipient_email')

        # Recipient is mandatory (either an existing user or a raw email address)
        if not recipient_id and not recipient_name and not recipient_email:
            return jsonify({'error': 'Recipient is required. Please specify who you are sending the capsule to.'}), 400

        # Resolve/validate recipient
        recipient_doc = None
        if recipient_id:
            try:
                recipient_obj_id = ObjectId(recipient_id)
            except Exception:
                return jsonify({'error': 'Invalid recipient_id'}), 400
            recipient_doc = _db.get_collection('users').find_one({'_id': recipient_obj_id})
            if not recipient_doc:
                return jsonify({'error': 'Recipient not found'}), 404
            if str(recipient_doc['_id']) == user_id:
                return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
        elif recipient_name:
            recipient_doc = _db.get_collection('users').find_one({'display_name': recipient_name})
            if not recipient_doc:
                return jsonify({'error': 'Recipient not found'}), 404
            if str(recipient_doc['_id']) == user_id:
                return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
            recipient_id = str(recipient_doc['_id'])
        elif recipient_email:
            # If they provided a raw email, ensure it is not the sender's own email
            sender_doc = _db.get_collection('users').find_one({'_id': ObjectId(user_id)})
            if sender_doc and sender_doc.get('email') and sender_doc['email'].lower() == recipient_email.lower():
                return jsonify({'error': 'You cannot send a capsule to yourself'}), 400
        
        # Handle optional file
        file_data = None
        filename = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename and file.filename != '':
                file_data = file.read()
                filename = secure_filename(file.filename)
        
        # Validate that at least file or description is provided
        if not file_data and not description:
            return jsonify({'error': 'Either a file or description must be provided'}), 400
        
        # Determine final email address we will notify (for both existing and external recipients)
        notify_email = None
        if recipient_doc is not None and recipient_doc.get('email'):
            notify_email = recipient_doc.get('email')
        elif recipient_email:
            notify_email = recipient_email

        result = _capsules.create_capsule(
            user_id=user_id,
            unlock_date=unlock_date,
            description=description if description else None,
            recipient_id=recipient_id,
            file_data=file_data,
            filename=filename,
            recipient_email=notify_email,
        )

        # Send email notification to recipient (if any). Do not block on failures.
        try:
            # Load sender info for nicer email text
            sender_doc = _db.get_collection('users').find_one({'_id': ObjectId(user_id)})
            sender_name = sender_doc.get('display_name') if sender_doc else None

            if recipient_doc is not None and recipient_doc.get('email'):
                _email_service.send_capsule_created_notification(
                    recipient_email=recipient_doc.get('email'),
                    recipient_name=recipient_doc.get('display_name'),
                    sender_name=sender_name,
                    unlock_date=unlock_date,
                )
            elif recipient_email:
                # Non-registered recipient: send an invite-style email
                _email_service.send_capsule_created_external_notification(
                    recipient_email=recipient_email,
                    sender_name=sender_name,
                    unlock_date=unlock_date,
                )
        except Exception:
            # Intentionally ignore email errors to avoid breaking capsule creation
            pass

        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/debug/test-email', methods=['GET', 'POST'])
def debug_test_email():
    """
    Simple endpoint to verify SMTP/email configuration.
    Expects JSON: { "to": "recipient@example.com" }
    """
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            to_email = data.get('to')
        else:
            # Allow simple browser testing via query string: /debug/test-email?to=you@example.com
            to_email = request.args.get('to')
        if not to_email:
            return jsonify({'error': 'Missing "to" email address'}), 400

        # Use a simple external-style notification as a test
        _email_service.send_capsule_created_external_notification(
            recipient_email=to_email,
            sender_name="Test Sender",
            unlock_date=datetime.utcnow(),
        )
        return jsonify({'message': f'Test email sent to {to_email}'}), 200
    except Exception as e:
        # Surface the exact error so configuration issues are visible
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules', methods=['GET'])
@require_auth
def get_capsules():
    try:
        user_id = request.user['uid']
        include_locked = request.args.get('include_locked', 'true').lower() == 'true'
        
        # Pagination parameters
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20
        except ValueError:
            page = 1
            limit = 20
        
        skip = (page - 1) * limit
        
        # Get all capsules (for count)
        all_items = _capsules.get_user_capsules(user_id, include_locked)
        total_count = len(all_items)
        
        # Apply pagination
        paginated_items = all_items[skip:skip + limit]
        
        return jsonify({
            'capsules': paginated_items,
            'count': len(paginated_items),
            'total': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit if total_count > 0 else 0,
            'has_next': skip + limit < total_count,
            'has_prev': page > 1
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['GET'])
@require_auth
def get_capsule(capsule_id):
    try:
        user_id = request.user['uid']
        doc = _capsules.get_capsule_metadata(capsule_id)
        if doc['user_id'] != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        return jsonify(doc), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>/unlock', methods=['POST'])
@require_auth
def unlock_capsule(capsule_id):
    try:
        user_id = request.user['uid']
        metadata = _capsules.get_capsule_metadata(capsule_id)
        if metadata['user_id'] != user_id and metadata.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        current_time = datetime.utcnow()
        if metadata['unlock_date'] > current_time:
            return jsonify({'error': 'Capsule is not ready to be unlocked yet', 'unlock_date': metadata['unlock_date'].isoformat(), 'current_time': current_time.isoformat()}), 400
        result = _capsules.unlock_capsule(capsule_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>/metadata', methods=['GET'])
@require_auth
def get_capsule_metadata(capsule_id):
    try:
        user_id = request.user['uid']
        doc = _capsules.get_capsule_metadata(capsule_id)
        if doc['user_id'] != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        return jsonify(doc), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>/preview', methods=['GET'])
@require_auth
def preview_capsule(capsule_id):
    """Get capsule file preview for editing (allows sender to view locked capsules)."""
    try:
        user_id = request.user['uid']
        result = _capsules.get_file_preview_for_edit(capsule_id, user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>/download', methods=['GET'])
@require_auth
def download_capsule(capsule_id):
    """Download an unlocked capsule file."""
    try:
        user_id = request.user['uid']
        # Verify ownership
        doc = _capsules.get_capsule_metadata(capsule_id)
        if doc['user_id'] != user_id and doc.get('recipient_id') != user_id:
            return jsonify({'error': 'Capsule not found'}), 404
        
        # Get decrypted file data
        file_data, filename, content_type = _capsules.get_decrypted_file_data(capsule_id)
        
        # Create file-like object from bytes
        file_obj = BytesIO(file_data)
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['PUT'])
@require_auth
def update_capsule(capsule_id):
    """Update capsule metadata (description, unlock_date, or file)."""
    try:
        user_id = request.user['uid']
        
        # Check if it's multipart/form-data (file upload) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload
            description = request.form.get('description')
            unlock_date_str = request.form.get('unlock_date')
            
            # Handle optional file
            file_data = None
            filename = None
            if 'file' in request.files:
                file = request.files['file']
                if file.filename and file.filename != '':
                    file_data = file.read()
                    filename = secure_filename(file.filename)
        else:
            # Handle JSON request
            data = request.get_json() or {}
            description = data.get('description')
            unlock_date_str = data.get('unlock_date')
            file_data = None
            filename = None
        
        unlock_date = None
        if unlock_date_str:
            date_valid, date_error, unlock_date_obj = validate_unlock_date(unlock_date_str)
            if not date_valid:
                return jsonify({'error': date_error}), 400
            unlock_date = unlock_date_obj
        
        # If description is empty string, treat as None to allow clearing
        if description == '':
            description = None
        
        result = _capsules.update_capsule(
            capsule_id, 
            user_id, 
            description=description, 
            unlock_date=unlock_date,
            file_data=file_data,
            filename=filename
        )
        return jsonify({
            'message': 'Capsule updated successfully',
            'capsule': result
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@capsule_bp.route('/capsules/<capsule_id>', methods=['DELETE'])
@require_auth
def delete_capsule(capsule_id):
    """Delete a capsule and its associated file."""
    try:
        user_id = request.user['uid']
        _capsules.delete_capsule(capsule_id, user_id)
        return jsonify({'message': 'Capsule deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
