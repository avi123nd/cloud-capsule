"""
Capsule Service using MongoDB for metadata and Cloudinary for file storage.

This service manages time capsules with encrypted files stored in Cloudinary
and metadata stored in MongoDB.
"""

import os
import uuid
import base64
from datetime import datetime
from bson import ObjectId
from werkzeug.utils import secure_filename

# Import Cloudinary storage service
from services.cloudinary_service import CloudinaryStorageService


class CapsuleService:
    """Service for managing time capsules with Cloudinary storage."""
    
    def __init__(self, db, encryption_service):
        self.db = db
        self.encryption_service = encryption_service
        self.capsules = db.get_collection('capsules')
        self.allowed_extensions = {
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
            'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'
        }
        
        # Initialize Cloudinary storage
        try:
            self.cloudinary_storage = CloudinaryStorageService()
        except ValueError as e:
            # If Cloudinary is not configured, fall back to None
            # and GridFS will be used if available
            self.cloudinary_storage = None
            print(f"Warning: Cloudinary not configured: {e}")
            # Fall back to GridFS
            from gridfs import GridFS
            self.fs = GridFS(db)
    
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
    
    def _store_file(self, encrypted_bytes: bytes, capsule_id: str, content_type: str = 'application/octet-stream') -> dict:
        """Store encrypted file - uses Cloudinary if available, falls back to GridFS."""
        if self.cloudinary_storage:
            return self.cloudinary_storage.upload_encrypted_file(
                encrypted_bytes, capsule_id, content_type
            )
        else:
            # Fall back to GridFS
            grid_id = self.fs.put(
                encrypted_bytes, 
                filename=f"{capsule_id}.enc", 
                content_type=content_type
            )
            return {
                'storage_type': 'gridfs',
                'gridfs_id': str(grid_id),
                'public_id': f"gridfs_{capsule_id}"
            }
    
    def _retrieve_file(self, storage_info: dict) -> bytes:
        """Retrieve encrypted file based on storage type."""
        storage_type = storage_info.get('storage_type', 'gridfs')
        
        if storage_type == 'cloudinary':
            public_id = storage_info.get('public_id')
            if public_id and self.cloudinary_storage:
                return self.cloudinary_storage.get_encrypted_file(public_id)
            else:
                raise ValueError("Cloudinary storage not available")
        else:
            # GridFS fallback
            grid_id = storage_info.get('gridfs_id')
            if isinstance(grid_id, str):
                grid_id = ObjectId(grid_id)
            data_bytes = self.fs.get(grid_id).read()
            return data_bytes
    
    def _delete_file(self, storage_info: dict) -> bool:
        """Delete file based on storage type."""
        storage_type = storage_info.get('storage_type', 'gridfs')
        
        if storage_type == 'cloudinary':
            public_id = storage_info.get('public_id')
            if public_id and self.cloudinary_storage:
                return self.cloudinary_storage.delete_file(public_id)
            return False
        else:
            # GridFS fallback
            grid_id = storage_info.get('gridfs_id')
            if isinstance(grid_id, str):
                grid_id = ObjectId(grid_id)
            try:
                self.fs.delete(grid_id)
                return True
            except Exception:
                return False

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
            recipient_email: Optional email of non-registered recipient
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
                
                # Store encrypted bytes in Cloudinary (or GridFS fallback)
                encrypted_bytes = base64.b64decode(encrypted_b64)
                storage_info = self._store_file(encrypted_bytes, capsule_id, 'application/octet-stream')
            
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
                
                # Store encrypted description in Cloudinary (or GridFS fallback)
                encrypted_bytes = base64.b64decode(encrypted_b64)
                storage_info = self._store_file(encrypted_bytes, capsule_id, 'text/plain')
                filename = 'description.txt'
                original_size = len(description_bytes)

            # Persist metadata with storage info
            storage_type = storage_info.get('storage_type', 'gridfs')
            doc = {
                'capsule_id': capsule_id,
                'user_id': user_id,
                'sender_id': user_id,
                'recipient_id': recipient_id,
                'recipient_email': recipient_email,
                'filename': filename,
                'capsule_type': capsule_type,
                'unlock_date': unlock_date,
                'storage_type': storage_type,
                'cloudinary_public_id': storage_info.get('public_id') if storage_type == 'cloudinary' else None,
                'cloudinary_url': storage_info.get('secure_url') if storage_type == 'cloudinary' else None,
                'gridfs_id': storage_info.get('gridfs_id') if storage_type == 'gridfs' else None,
                'encryption_iv': iv,
                'original_size': original_size,
                'description': description,
                'created_at': datetime.utcnow(),
                'is_unlocked': False,
                'unlocked_at': None
            }
            self.capsules.insert_one(doc)

            return {
                'capsule_id': capsule_id,
                'message': 'Capsule created successfully',
                'unlock_date': unlock_date.isoformat(),
                'storage_type': storage_type
            }
        except Exception as e:
            raise Exception(f"Capsule creation failed: {str(e)}")

    def get_user_capsules(self, user_id, include_locked=True):
        try:
            # Include both sent and received capsules
            or_clause = [{'user_id': user_id}, {'recipient_id': user_id}]
            query = {'$or': or_clause}
            if not include_locked:
                query['is_unlocked'] = True
            results = []
            for doc in self.capsules.find(query).sort('created_at', -1):
                item = dict(doc)
                item['capsule_id'] = item.get('capsule_id')
                item['_id'] = str(item['_id'])
                if item.get('recipient_id') is not None:
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
                
                # Build storage info object
                item['storage_info'] = {
                    'type': item.get('storage_type', 'gridfs'),
                    'public_id': item.get('cloudinary_public_id'),
                    'url': item.get('cloudinary_url'),
                    'gridfs_id': str(item.get('gridfs_id')) if item.get('gridfs_id') else None
                }
                
                # Remove old fields
                item.pop('cloudinary_public_id', None)
                item.pop('cloudinary_url', None)
                item.pop('gridfs_id', None)
                item.pop('storage_type', None)
                
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
        
        # Build storage info
        item['storage_info'] = {
            'type': item.get('storage_type', 'gridfs'),
            'public_id': item.get('cloudinary_public_id'),
            'url': item.get('cloudinary_url'),
            'gridfs_id': str(item.get('gridfs_id')) if item.get('gridfs_id') else None
        }
        
        # Remove old fields
        item.pop('cloudinary_public_id', None)
        item.pop('cloudinary_url', None)
        item.pop('gridfs_id', None)
        item.pop('storage_type', None)
        
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
        
        # Build storage info to retrieve file
        storage_info = {
            'storage_type': doc.get('storage_type', 'gridfs'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': str(doc.get('gridfs_id')) if doc.get('gridfs_id') else None
        }
        
        # Read encrypted bytes from appropriate storage
        data_bytes = self._retrieve_file(storage_info)
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
                if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
                    raise ValueError('Capsule is not unlocked yet')
            else:
                raise ValueError('Capsule is not unlocked yet')
        
        # Build storage info
        storage_info = {
            'storage_type': doc.get('storage_type', 'gridfs'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': str(doc.get('gridfs_id')) if doc.get('gridfs_id') else None
        }
        
        # Read encrypted bytes from appropriate storage
        data_bytes = self._retrieve_file(storage_info)
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
        """
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
            raise ValueError('Capsule not found')
        
        # Get decrypted file data (allows locked for owner)
        file_data, filename, content_type = self.get_decrypted_file_data(
            capsule_id, 
            allow_locked_for_owner=True, 
            user_id=user_id
        )
        
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
            if filename and not self._allowed_file(filename):
                raise ValueError(f"File type not allowed: {filename}")
            
            # Delete old file from storage
            old_storage_info = {
                'storage_type': doc.get('storage_type', 'gridfs'),
                'public_id': doc.get('cloudinary_public_id'),
                'gridfs_id': str(doc.get('gridfs_id')) if doc.get('gridfs_id') else None
            }
            self._delete_file(old_storage_info)
            
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
            
            # Store new encrypted file in Cloudinary (or GridFS fallback)
            storage_info = self._store_file(encrypted_bytes, capsule_id, filename or doc.get('filename', 'capsule'))
            storage_type = storage_info.get('storage_type', 'gridfs')
            
            # Update metadata
            update_data['cloudinary_public_id'] = storage_info.get('public_id') if storage_type == 'cloudinary' else None
            update_data['cloudinary_url'] = storage_info.get('secure_url') if storage_type == 'cloudinary' else None
            update_data['gridfs_id'] = storage_info.get('gridfs_id') if storage_type == 'gridfs' else None
            update_data['storage_type'] = storage_type
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
        """Delete a capsule and its stored file."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        if doc['user_id'] != user_id:
            raise ValueError('Capsule not found')
        
        # Delete file from storage
        storage_info = {
            'storage_type': doc.get('storage_type', 'gridfs'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': str(doc.get('gridfs_id')) if doc.get('gridfs_id') else None
        }
        self._delete_file(storage_info)
        
        # Delete metadata
        result = self.capsules.delete_one({'capsule_id': capsule_id})
        if result.deleted_count == 0:
            raise ValueError('Failed to delete capsule')
        
        return True
