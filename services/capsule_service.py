"""
Capsule Service using MongoDB and GridFS
"""

import os
import uuid
import base64
from datetime import datetime
from bson import ObjectId
from gridfs import GridFS
from werkzeug.utils import secure_filename


class CapsuleService:
    """Service for managing time capsules in MongoDB."""

    def __init__(self, db, encryption_service):
        self.db = db
        self.fs = GridFS(db)
        self.encryption_service = encryption_service
        self.capsules = db.get_collection('capsules')
        self.allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'}

    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def _get_file_type(self, filename):
        extension = filename.rsplit('.', 1)[1].lower()
        if extension in {'txt', 'pdf'}:
            return 'text'
        if extension in {'png', 'jpg', 'jpeg', 'gif'}:
            return 'image'
        if extension in {'mp4', 'avi', 'mov'}:
            return 'video'
        if extension in {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'}:
            return 'audio'
        return 'other'

    def create_capsule(
        self,
        user_id,
        unlock_date,
        description=None,
        recipient_id: str | None = None,
        file_data=None,
        filename=None,
        recipient_email: str | None = None,
    ):
        """
        Create a time capsule. Either file_data+filename OR description must be provided.
        recipient_id is mandatory.
        
        Args:
            user_id: User ID creating the capsule
            unlock_date: When the capsule should unlock
            description: Optional description text (required if no file)
            recipient_id: Required recipient user ID
            file_data: Optional file bytes
            filename: Optional filename (required if file_data provided)
        """
        try:
            # Validate recipient is provided
            if not recipient_id and not recipient_email:
                raise ValueError("Recipient is required. You must specify who you are sending the capsule to.")
            
            # Validate that at least one of file or description is provided
            if not file_data and not description:
                raise ValueError("Either a file or description must be provided")
            
            capsule_id = str(uuid.uuid4())
            
            # Handle file-based capsule
            if file_data and filename:
                if not self._allowed_file(filename):
                    raise ValueError(f"File type not allowed: {filename}")
                
                capsule_type = self._get_file_type(filename)
                original_size = len(file_data)
                
                # Encrypt file bytes
                encrypted_result = self.encryption_service.encrypt_data(file_data)
                encrypted_b64 = encrypted_result['encrypted_data']
                iv = encrypted_result['iv']
                
                # Store encrypted bytes in GridFS
                encrypted_bytes = base64.b64decode(encrypted_b64)
                grid_id = self.fs.put(encrypted_bytes, filename=f"{capsule_id}.enc", content_type='application/octet-stream')
            
            # Handle description-only capsule
            else:
                if not description or not description.strip():
                    raise ValueError("Description cannot be empty when no file is provided")
                
                capsule_type = 'text'
                # Encrypt description text
                description_bytes = description.encode('utf-8')
                encrypted_result = self.encryption_service.encrypt_data(description_bytes)
                encrypted_b64 = encrypted_result['encrypted_data']
                iv = encrypted_result['iv']
                
                # Store encrypted description in GridFS
                encrypted_bytes = base64.b64decode(encrypted_b64)
                grid_id = self.fs.put(encrypted_bytes, filename=f"{capsule_id}.enc", content_type='text/plain')
                filename = 'description.txt'  # Default filename for text-only capsules
                original_size = len(description_bytes)

            # Persist metadata
            doc = {
                'capsule_id': capsule_id,
                # For backward compatibility, keep user_id as sender
                'user_id': user_id,
                'sender_id': user_id,
                'recipient_id': recipient_id,
                # Store the email we will notify, even if the recipient is not yet a user
                'recipient_email': recipient_email,
                'filename': filename,
                'capsule_type': capsule_type,
                'unlock_date': unlock_date,
                'gridfs_id': grid_id,
                'encryption_iv': iv,
                'original_size': original_size,
                'description': description,  # Store description in metadata for preview
                'created_at': datetime.utcnow(),
                'is_unlocked': False,
                'unlocked_at': None
            }
            self.capsules.insert_one(doc)

            return {
                'capsule_id': capsule_id,
                'message': 'Capsule created successfully',
                'unlock_date': unlock_date.isoformat()
            }
        except Exception as e:
            raise Exception(f"Capsule creation failed: {str(e)}")

    def get_user_capsules(self, user_id, include_locked=True):
        try:
            # Include both sent and received capsules
            or_clause = [{ 'user_id': user_id }, { 'recipient_id': user_id }]
            query = { '$or': or_clause }
            if not include_locked:
                query['is_unlocked'] = True
            results = []
            for doc in self.capsules.find(query).sort('created_at', -1):
                item = dict(doc)
                item['capsule_id'] = item.get('capsule_id')
                item['_id'] = str(item['_id'])
                if item.get('recipient_id') is not None:
                    # recipient_id can be None or string/ObjectId; normalize to str when present
                    try:
                        item['recipient_id'] = str(item['recipient_id']) if item['recipient_id'] is not None else None
                    except Exception:
                        pass
                if item.get('unlocked_at'):
                    item['unlocked_at'] = item['unlocked_at'].isoformat()
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
                if item.get('unlock_date'):
                    item['unlock_date'] = item['unlock_date'].isoformat()
                item['gridfs_id'] = str(item['gridfs_id'])
                results.append(item)
            return results
        except Exception as e:
            raise Exception(f"Failed to retrieve capsules: {str(e)}")

    def get_capsule_metadata(self, capsule_id: str):
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        item = dict(doc)
        item['_id'] = str(item['_id'])
        item['gridfs_id'] = str(item['gridfs_id'])
        if item.get('unlocked_at'):
            item['unlocked_at'] = item['unlocked_at'].isoformat()
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat()
        if item.get('unlock_date'):
            item['unlock_date'] = item['unlock_date'].isoformat()
        return item

    def unlock_capsule(self, capsule_id: str):
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Read encrypted bytes from GridFS and convert to base64 string for decryptor
        grid_id = doc['gridfs_id']
        # Handle both ObjectId and string
        if isinstance(grid_id, str):
            grid_id = ObjectId(grid_id)
        data_bytes = self.fs.get(grid_id).read()
        encrypted_b64 = base64.b64encode(data_bytes).decode('utf-8')
        decrypted = self.encryption_service.decrypt_data(encrypted_b64, doc['encryption_iv'])

        # Only update unlock status if not already unlocked
        if not doc.get('is_unlocked'):
            self.capsules.update_one({'_id': doc['_id']}, {'$set': {'is_unlocked': True, 'unlocked_at': datetime.utcnow()}})
            unlocked_at = datetime.utcnow().isoformat()
        else:
            unlocked_at = (doc['unlocked_at'].isoformat() if doc.get('unlocked_at') else None)

        return {
            'capsule_id': capsule_id,
            'filename': doc['filename'],
            'capsule_type': doc['capsule_type'],
            'data': decrypted.decode('utf-8') if doc['capsule_type'] == 'text' else base64.b64encode(decrypted).decode('utf-8'),
            'unlocked_at': unlocked_at,
            'message': 'Capsule already unlocked' if doc.get('is_unlocked') else 'Capsule unlocked successfully'
        }

    def get_decrypted_file_data(self, capsule_id: str, allow_locked_for_owner: bool = False, user_id: str = None):
        """
        Get decrypted file data for download.
        Capsule must be unlocked, unless allow_locked_for_owner is True and user is the sender.
        
        Args:
            capsule_id: Capsule ID
            allow_locked_for_owner: If True, allows sender to view locked capsule for editing
            user_id: User ID to check ownership
            
        Returns:
            tuple: (file_data_bytes, filename, content_type)
        """
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Check if locked and if user can view it
        if not doc.get('is_unlocked'):
            if allow_locked_for_owner and user_id:
                # Only allow sender to view their own locked capsules
                if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
                    raise ValueError('Capsule is not unlocked yet')
            else:
                raise ValueError('Capsule is not unlocked yet')
        
        # Read encrypted bytes from GridFS
        grid_id = doc['gridfs_id']
        if isinstance(grid_id, str):
            grid_id = ObjectId(grid_id)
        data_bytes = self.fs.get(grid_id).read()
        encrypted_b64 = base64.b64encode(data_bytes).decode('utf-8')
        
        # Decrypt
        decrypted = self.encryption_service.decrypt_data(encrypted_b64, doc['encryption_iv'])
        
        # Determine content type
        filename = doc['filename']
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        content_types = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'aac': 'audio/aac',
            'flac': 'audio/flac'
        }
        content_type = content_types.get(extension, 'application/octet-stream')
        
        return decrypted, filename, content_type
    
    def get_file_preview_for_edit(self, capsule_id: str, user_id: str):
        """
        Get file data as base64 for preview when editing (allows sender to view locked capsules).
        
        Args:
            capsule_id: Capsule ID
            user_id: User ID (must be the sender)
            
        Returns:
            dict with base64 data and metadata
        """
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Only allow sender to view their own capsules
        if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
            raise ValueError('Capsule not found')
        
        # Get decrypted file data (allows locked for owner)
        file_data, filename, content_type = self.get_decrypted_file_data(
            capsule_id, 
            allow_locked_for_owner=True, 
            user_id=user_id
        )
        
        # Convert to base64 for frontend
        if doc['capsule_type'] == 'text':
            data_base64 = file_data.decode('utf-8')
        else:
            data_base64 = base64.b64encode(file_data).decode('utf-8')
        
        return {
            'data': data_base64,
            'filename': filename,
            'capsule_type': doc['capsule_type'],
            'content_type': content_type
        }

    def update_capsule(self, capsule_id: str, user_id: str, description: str = None, unlock_date: datetime = None, file_data: bytes = None, filename: str = None):
        """Update capsule metadata and/or file. Only allowed if not unlocked."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        if doc['user_id'] != user_id:
            raise ValueError('Capsule not found')
        
        if doc.get('is_unlocked'):
            raise ValueError('Cannot update unlocked capsule')
        
        update_data = {}
        if description is not None:
            update_data['description'] = description
        if unlock_date is not None:
            if unlock_date <= datetime.utcnow():
                raise ValueError('Unlock date must be in the future')
            update_data['unlock_date'] = unlock_date
        
        # Handle file replacement
        if file_data is not None:
            # Validate file if filename provided
            if filename and not self._allowed_file(filename):
                raise ValueError(f"File type not allowed: {filename}")
            
            # Delete old GridFS file
            old_grid_id = doc['gridfs_id']
            if isinstance(old_grid_id, str):
                old_grid_id = ObjectId(old_grid_id)
            try:
                self.fs.delete(old_grid_id)
            except Exception:
                pass  # File might already be deleted
            
            # Encrypt new file
            encrypted_result = self.encryption_service.encrypt_data(file_data)
            encrypted_b64 = encrypted_result['encrypted_data']
            iv = encrypted_result['iv']
            encrypted_bytes = base64.b64decode(encrypted_b64)
            
            # Determine file type
            if filename:
                extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                capsule_type = self._get_file_type(extension)
            else:
                capsule_type = doc.get('capsule_type', 'other')
            
            # Store new encrypted file in GridFS
            grid_id = self.fs.put(encrypted_bytes, filename=filename or doc.get('filename', 'capsule'))
            
            # Update metadata
            update_data['gridfs_id'] = grid_id
            update_data['encryption_iv'] = iv
            update_data['original_size'] = len(file_data)
            if filename:
                update_data['filename'] = filename
                update_data['capsule_type'] = capsule_type
        
        if not update_data:
            raise ValueError('No update data provided')
        
        self.capsules.update_one(
            {'capsule_id': capsule_id},
            {'$set': update_data}
        )
        
        return self.get_capsule_metadata(capsule_id)

    def delete_capsule(self, capsule_id: str, user_id: str):
        """Delete a capsule and its GridFS file."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        if doc['user_id'] != user_id:
            raise ValueError('Capsule not found')
        
        # Delete GridFS file
        grid_id = doc['gridfs_id']
        if isinstance(grid_id, str):
            grid_id = ObjectId(grid_id)
        try:
            self.fs.delete(grid_id)
        except Exception:
            pass  # File may already be deleted
        
        # Delete metadata
        result = self.capsules.delete_one({'capsule_id': capsule_id})
        if result.deleted_count == 0:
            raise ValueError('Failed to delete capsule')
        
        return True
