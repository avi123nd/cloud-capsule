"""
Authentication Routes (MongoDB + JWT)
"""

from flask import Blueprint, request, jsonify
import os
from pymongo import MongoClient
from bson import ObjectId
from services.auth_service import AuthService, require_auth
from services.email_service import EmailService
from utils.validators import validate_email, validate_password, validate_display_name

auth_bp = Blueprint('auth', __name__)

# Initialize a local service instance using the same DB as app
def get_db():
    uri = os.getenv('MONGO_URI')
    client = MongoClient(uri)
    # Extract db name from URI or use default
    if '/' in uri.rsplit('?', 1)[0]:
        db_name = uri.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return client[db_name]
    return client['timecapsule']

_db = get_db()
_auth_service = AuthService(_db, os.getenv('JWT_SECRET'))
_email_service = EmailService()


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        display_name = data.get('display_name')
        
        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return jsonify({'error': email_error}), 400
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        # Validate display name (required for unique ID name)
        if not display_name:
            return jsonify({'error': 'Display name is required'}), 400
        name_valid, name_error = validate_display_name(display_name)
        if not name_valid:
            return jsonify({'error': name_error}), 400

        # Pre-check duplicate display name to return 409 semantics
        if _db.get_collection('users').find_one({'display_name': display_name}):
            return jsonify({'error': 'Display name already in use. Please choose another name.'}), 409

        user = _auth_service.create_user(email, password, display_name)
        token = _auth_service.generate_token(user['uid'], user['email'])
        return jsonify({'message': 'User registered successfully', 'user': user, 'token': token}), 201
    except Exception as e:
        msg = str(e)
        if 'Display name already in use' in msg:
            return jsonify({'error': 'Display name already in use. Please choose another name.'}), 409
        if 'Email already registered' in msg:
            return jsonify({'error': 'An account with this email already exists. Please use a different email or sign in.'}), 409
        return jsonify({'error': msg}), 400


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        result = _auth_service.login(email, password)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user_id = request.user['uid']
        user_info = _auth_service.get_user_by_uid(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user_info}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile."""
    try:
        user_id = request.user['uid']
        data = request.get_json() or {}
        display_name = data.get('display_name')
        
        if display_name is None:
            return jsonify({'error': 'No update data provided'}), 400
        
        # Validate display name
        name_valid, name_error = validate_display_name(display_name)
        if not name_valid:
            return jsonify({'error': name_error}), 400
        
        # Pre-check duplicate to set 409
        if _db.get_collection('users').find_one({'display_name': display_name, '_id': {'$ne': ObjectId(user_id)}}):
            return jsonify({'error': 'Display name already in use. Please choose another name.'}), 409

        updated_user = _auth_service.update_user(user_id, display_name)
        return jsonify({
            'message': 'Profile updated successfully',
            'user': updated_user
        }), 200
    except Exception as e:
        msg = str(e)
        if 'Display name already in use' in msg:
            return jsonify({'error': 'Display name already in use. Please choose another name.'}), 409
        return jsonify({'error': msg}), 400


@auth_bp.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password."""
    try:
        user_id = request.user['uid']
        data = request.get_json() or {}
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password strength
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        _auth_service.change_password(user_id, current_password, new_password)
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/auth/delete', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete user account and all associated capsules."""
    try:
        user_id = request.user['uid']
        
        # Delete all user's capsules first
        from services.capsule_service import CapsuleService
        from services.encryption_service import EncryptionService
        encryption = EncryptionService()
        capsules = CapsuleService(_db, encryption)
        
        # Get all user capsules
        user_capsules = capsules.get_user_capsules(user_id, include_locked=True)
        
        # Delete each capsule (including GridFS files)
        for capsule in user_capsules:
            try:
                capsules.delete_capsule(capsule['capsule_id'], user_id)
            except Exception:
                pass  # Continue even if some deletions fail
        
        # Delete user account
        success = _auth_service.delete_user(user_id)
        
        if success:
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete account'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/refresh-token', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh JWT token."""
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        new_token = _auth_service.refresh_token(token)
        return jsonify({
            'token': new_token,
            'message': 'Token refreshed successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset. Sends email with reset link."""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email format
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return jsonify({'error': email_error}), 400
        
        # Request password reset (always returns True for security)
        _auth_service.request_password_reset(email)
        
        # Get user to send email (if exists)
        user_doc = _db.get_collection('users').find_one({'email': email.lower()})
        if user_doc:
            # Get reset token from user document
            reset_token = user_doc.get('password_reset_token')
            if reset_token:
                # Send reset email
                try:
                    _email_service.send_password_reset_email(
                        recipient_email=user_doc['email'],
                        recipient_name=user_doc.get('display_name'),
                        reset_token=reset_token
                    )
                except Exception:
                    # Email failure shouldn't break the flow
                    pass
        
        # Always return success (don't reveal if email exists)
        return jsonify({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token."""
    try:
        data = request.get_json() or {}
        reset_token = data.get('token')
        new_password = data.get('new_password')
        
        if not reset_token or not new_password:
            return jsonify({'error': 'Reset token and new password are required'}), 400
        
        # Validate new password strength
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        _auth_service.reset_password(reset_token, new_password)
        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
