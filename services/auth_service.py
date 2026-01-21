"""
Authentication Service using MongoDB, bcrypt, and JWT
"""

import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from bson import ObjectId
import bcrypt
import jwt


class AuthService:
    """MongoDB-backed authentication with bcrypt and JWT."""

    def __init__(self, db, jwt_secret: str):
        self.users = db.get_collection('users')
        self.jwt_secret = jwt_secret or 'dev-jwt-secret'

    def hash_password(self, plain: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain.encode('utf-8'), salt)

    def verify_password(self, plain: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed)

    def create_user(self, email: str, password: str, display_name: str | None = None) -> dict:
        existing = self.users.find_one({'email': email.lower()})
        if existing:
            raise Exception('Email already registered - An account with this email already exists')

        if display_name:
            # Enforce unique display_name
            if self.users.find_one({'display_name': display_name}):
                raise Exception('Display name already in use')

        hashed = self.hash_password(password)
        user_doc = {
            'email': email.lower(),
            'password': hashed,
            'display_name': display_name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        result = self.users.insert_one(user_doc)
        return {
            'uid': str(result.inserted_id),
            'email': email.lower(),
            'display_name': display_name,
        }

    def generate_token(self, uid: str, email: str) -> str:
        payload = {
            'uid': uid,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def login(self, email: str, password: str) -> dict:
        user = self.users.find_one({'email': email.lower()})
        if not user:
            raise Exception('Invalid credentials')
        if not self.verify_password(password, user['password']):
            raise Exception('Invalid credentials')
        token = self.generate_token(str(user['_id']), user['email'])
        return {
            'token': token,
            'user': {
                'uid': str(user['_id']),
                'email': user['email'],
                'display_name': user.get('display_name')
            }
        }

    def get_user_by_uid(self, uid: str) -> dict | None:
        try:
            doc = self.users.find_one({'_id': ObjectId(uid)})
            if not doc:
                return None
            return {
                'uid': str(doc['_id']),
                'email': doc['email'],
                'display_name': doc.get('display_name')
            }
        except Exception:
            return None

    def update_user(self, uid: str, display_name: str = None) -> dict:
        """Update user profile information."""
        update_data = {'updated_at': datetime.utcnow()}
        if display_name is not None:
            # Check uniqueness for display_name if changed
            if self.users.find_one({'display_name': display_name, '_id': {'$ne': ObjectId(uid)}}):
                raise Exception('Display name already in use')
            update_data['display_name'] = display_name
        
        result = self.users.update_one(
            {'_id': ObjectId(uid)},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            raise Exception('User not found or no changes made')
        
        return self.get_user_by_uid(uid)

    def change_password(self, uid: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.users.find_one({'_id': ObjectId(uid)})
        if not user:
            raise Exception('User not found')
        
        if not self.verify_password(current_password, user['password']):
            raise Exception('Current password is incorrect')
        
        new_hashed = self.hash_password(new_password)
        result = self.users.update_one(
            {'_id': ObjectId(uid)},
            {'$set': {'password': new_hashed, 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise Exception('Failed to update password')
        
        return True

    def delete_user(self, uid: str) -> bool:
        """Delete user account."""
        result = self.users.delete_one({'_id': ObjectId(uid)})
        return result.deleted_count > 0

    def verify_token(self, token: str) -> dict | None:
        """Verify and decode JWT token."""
        try:
            decoded = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return decoded
        except Exception:
            return None

    def refresh_token(self, token: str) -> str:
        """Refresh JWT token if valid."""
        decoded = self.verify_token(token)
        if not decoded:
            raise Exception('Invalid or expired token')
        
        # Generate new token with extended expiry
        return self.generate_token(decoded['uid'], decoded['email'])

    def request_password_reset(self, email: str) -> bool:
        """Generate a password reset token and store it. Returns True if email exists."""
        user = self.users.find_one({'email': email.lower()})
        if not user:
            # Don't reveal if email exists or not (security best practice)
            return True
        
        # Generate reset token (expires in 1 hour)
        reset_token = jwt.encode(
            {
                'uid': str(user['_id']),
                'email': user['email'],
                'type': 'password_reset',
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            self.jwt_secret,
            algorithm='HS256'
        )
        
        # Store reset token in user document
        self.users.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password_reset_token': reset_token,
                'password_reset_expires': datetime.utcnow() + timedelta(hours=1),
                'updated_at': datetime.utcnow()
            }}
        )
        
        return True

    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password using a valid reset token."""
        try:
            decoded = jwt.decode(reset_token, self.jwt_secret, algorithms=['HS256'])
            if decoded.get('type') != 'password_reset':
                raise Exception('Invalid reset token')
            
            uid = decoded['uid']
            user = self.users.find_one({'_id': ObjectId(uid)})
            
            if not user:
                raise Exception('User not found')
            
            # Verify token matches stored token
            if user.get('password_reset_token') != reset_token:
                raise Exception('Invalid or expired reset token')
            
            # Check expiration
            if user.get('password_reset_expires') and user['password_reset_expires'] < datetime.utcnow():
                raise Exception('Reset token has expired')
            
            # Update password and clear reset token
            new_hashed = self.hash_password(new_password)
            self.users.update_one(
                {'_id': ObjectId(uid)},
                {'$set': {
                    'password': new_hashed,
                    'password_reset_token': None,
                    'password_reset_expires': None,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            return True
        except jwt.ExpiredSignatureError:
            raise Exception('Reset token has expired')
        except Exception as e:
            raise Exception(f'Invalid reset token: {str(e)}')


def require_auth(f):
    """Decorator to require a valid JWT in Authorization header."""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        token = auth_header.split(' ')[1]
        secret = os.getenv('JWT_SECRET', 'dev-jwt-secret')
        try:
            decoded = jwt.decode(token, secret, algorithms=['HS256'])
            request.user = decoded
        except Exception:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)

    return decorated
