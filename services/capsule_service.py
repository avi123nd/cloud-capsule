"""
Capsule Service using MongoDB for metadata and Cloudinary for file storage.

This service manages time capsules with encrypted files stored primarily in Cloudinary.
GridFS is only used for backward compatibility with OLD capsules (read-only).
NEW CAPSULES: All files are stored in Cloudinary ONLY.
"""

import os
import uuid
import base64
import logging
from datetime import datetime
from bson import ObjectId
from gridfs import GridFS
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class CapsuleService:
    """Service for managing time capsules with Cloudinary storage ONLY."""
    
    def __init__(self, db, encryption_service):
        self.db = db
        self.encryption_service = encryption_service
        self.capsules = db.get_collection('capsules')
        self.allowed_extensions = {
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
            'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'
        }
        
        # Initialize Cloudinary storage (PRIMARY)
        self.cloudinary_storage = None
        cloudinary_config = {
            'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
            'api_key': os.getenv('CLOUDINARY_API_KEY'),
            'api_secret': os.getenv('CLOUDINARY_API_SECRET')
        }
        logger.info(f"Cloudinary config check: cloud_name={cloudinary_config['cloud_name'] is not None}, api_key={cloudinary_config['api_key'] is not None}, api_secret={cloudinary_config['api_secret'] is not None}")
        
        try:
            from services.cloudinary_service import CloudinaryStorageService
            self.cloudinary_storage = CloudinaryStorageService()
            logger.info("✅ Cloudinary storage initialized successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Cloudinary library not installed: {e}")
            self.cloudinary_storage = None
        except ValueError as e:
            logger.warning(f"⚠️ Cloudinary not configured: {e}")
            self.cloudinary_storage = None
        except Exception as e:
            import traceback
            logger.error(f"❌ Failed to initialize Cloudinary: {e}")
            logger.error(f"Cloudinary init traceback: {traceback.format_exc()}")
            self.cloudinary_storage = None
        
        # GridFS for backward compatibility with OLD capsules (read-only)
        # NEW CAPSULES: All files go to Cloudinary only
        self.fs = None
        try:
            self.fs = GridFS(db)
            logger.info("GridFS initialized for backward compatibility with old capsules")
        except ImportError:
            logger.warning("⚠️ gridfs module not available")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize GridFS: {e}")
        
        # Ensure at least one storage backend is available
        if self.cloudinary_storage is None and self.fs is None:
            raise RuntimeError("No storage backend available")
    
    def _allowed_file(self, filename):
        """Check if file extension is allowed."""
        if not filename or '.' not in filename:
            return False
        return filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def _get_file_type(self, filename):
        """Get the file type category from filename."""
        if not filename or '.' not in filename:
            return 'other'
        
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
    
    def _safe_objectid(self, id_value):
        """Safely convert a string to ObjectId, handling errors gracefully."""
        if id_value is None:
            return None
        if isinstance(id_value, ObjectId):
            return id_value
        if isinstance(id_value, str):
            try:
                return ObjectId(id_value)
            except Exception:
                return id_value
        return id_value
    
    def _store_file(self, encrypted_bytes: bytes, capsule_id: str, content_type: str = 'application/octet-stream') -> dict:
        """Store encrypted file - Cloudinary ONLY for NEW capsules.
        
        NEW CAPSULES: All files MUST be stored in Cloudinary.
        GridFS is NOT used for new uploads.
        """
        print(f"\n=== STORAGE DEBUG: capsule_id={capsule_id} ===")
        print(f"Cloudinary storage available: {self.cloudinary_storage is not None}")
        
        if not self.cloudinary_storage:
            raise ValueError("❌ Cloudinary storage is not available. Please configure Cloudinary credentials.")
        
        print(f"Uploading to Cloudinary...")
        try:
            result = self.cloudinary_storage.upload_encrypted_file(
                encrypted_bytes, capsule_id, content_type
            )
            print(f"✅ SUCCESS: Uploaded to Cloudinary: {result.get('public_id')}")
            print(f"URL: {result.get('secure_url')}")
            print("=== END STORAGE DEBUG ===\n")
            return result
        except Exception as e:
            print(f"❌ FAILED: Cloudinary upload failed: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Failed to upload file to Cloudinary: {str(e)}")
    
    def _retrieve_file(self, storage_info: dict) -> bytes:
        """Retrieve encrypted file from Cloudinary OR GridFS (for backward compatibility)."""
        storage_type = storage_info.get('storage_type', 'gridfs')
        
        if storage_type == 'cloudinary':
            public_id = storage_info.get('public_id')
            if not public_id:
                raise ValueError("Cloudinary public_id missing from storage info")
            
            if not self.cloudinary_storage:
                raise ValueError("Cloudinary storage not available")
            
            return self.cloudinary_storage.get_encrypted_file(public_id)
        
        # Legacy GridFS support (for backward compatibility with old capsules)
        # NEW CAPSULES: Always use Cloudinary
        grid_id = storage_info.get('gridfs_id')
        if not grid_id:
            raise ValueError("Storage info missing: no public_id (Cloudinary) or gridfs_id (GridFS)")
        
        grid_oid = self._safe_objectid(grid_id)
        
        if not isinstance(grid_oid, ObjectId):
            raise ValueError(f"Invalid GridFS ID format: {grid_id}")
        
        try:
            data_bytes = self.fs.get(grid_oid).read()
            return data_bytes
        except Exception as e:
            raise ValueError(f"Failed to retrieve file from GridFS: {str(e)}")
    
    def _delete_file(self, storage_info: dict) -> bool:
        """Delete file from Cloudinary OR GridFS (for backward compatibility with old capsules)."""
        storage_type = storage_info.get('storage_type', 'gridfs')
        
        if storage_type == 'cloudinary':
            public_id = storage_info.get('public_id')
            if not public_id:
                logger.warning("Cannot delete Cloudinary file: public_id missing")
                return False
            
            if not self.cloudinary_storage:
                logger.warning("Cannot delete file: Cloudinary storage not available")
                return False
            
            return self.cloudinary_storage.delete_file(public_id)
        
        # Legacy GridFS support
        grid_id = storage_info.get('gridfs_id')
        if not grid_id:
            logger.warning("Cannot delete GridFS file: gridfs_id missing")
            return False
        
        grid_oid = self._safe_objectid(grid_id)
        
        if not isinstance(grid_oid, ObjectId):
            logger.warning(f"Invalid GridFS ID format: {grid_id}")
            return False
        
        try:
            self.fs.delete(grid_oid)
            logger.info(f"Deleted file from GridFS: {grid_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete GridFS file: {e}")
            return False

    def create_capsule(
        self,
        user_id,
        unlock_date,
        description: str | None = None,
        recipient_id: str | None = None,
        file_data: bytes | None = None,
        filename: str | None = None,
        recipient_email: str | None = None,
    ) -> dict:
        """
        Create a new time capsule.
        
        Args:
            user_id: The sender's user ID
            unlock_date: datetime when the capsule should unlock
            description: Optional text description
            recipient_id: Optional registered recipient's user ID
            file_data: Optional file bytes
            filename: Optional filename (required if file_data provided)
            recipient_email: Optional external recipient email
            
        Returns:
            dict with capsule_id, message, unlock_date, storage_type
            
        Raises:
            ValueError: For validation errors (will be caught by route)
            Exception: For storage/encryption errors
        """
        print(f"\n=== CREATE CAPSULE DEBUG ===")
        print(f"user_id: {user_id}")
        print(f"file_data provided: {file_data is not None}")
        print(f"filename: {filename}")
        print(f"Cloudinary storage available: {self.cloudinary_storage is not None}")
        try:
            # ========== VALIDATION ==========
            
            # Validate recipient
            if not recipient_id and not recipient_email:
                raise ValueError("Recipient is required. Provide recipient_id or recipient_email.")
            
            # Validate content (file OR description)
            if not file_data and not description:
                raise ValueError("Either a file or description must be provided.")
            
            # Validate file if provided
            if file_data and not filename:
                raise ValueError("Filename is required when uploading a file.")
            
            if filename and not self._allowed_file(filename):
                raise ValueError(f"File type not allowed: {filename}. Allowed: {', '.join(self.allowed_extensions)}")
            
            # Validate unlock_date type
            if not isinstance(unlock_date, datetime):
                raise ValueError("unlock_date must be a datetime object")
            
            # ========== ENCRYPTION ==========
            
            capsule_id = str(uuid.uuid4())
            
            if file_data and filename:
                # File-based capsule
                capsule_type = self._get_file_type(filename)
                original_size = len(file_data)
                
                # Encrypt file
                encrypted_result = self.encryption_service.encrypt_data(file_data)
                encrypted_b64 = encrypted_result['encrypted_data']
                iv = encrypted_result['iv']
                
            elif description:
                # Description-only capsule
                capsule_type = 'text'
                description_bytes = description.encode('utf-8')
                original_size = len(description_bytes)
                
                # Encrypt description
                encrypted_result = self.encryption_service.encrypt_data(description_bytes)
                encrypted_b64 = encrypted_result['encrypted_data']
                iv = encrypted_result['iv']
                filename = 'description.txt'
            else:
                raise ValueError("Invalid capsule content")
            
            # ========== STORAGE ==========
            
            encrypted_bytes = base64.b64decode(encrypted_b64)
            
            try:
                storage_info = self._store_file(
                    encrypted_bytes, 
                    capsule_id, 
                    content_type='text/plain' if capsule_type == 'text' else 'application/octet-stream'
                )
                storage_type = storage_info.get('storage_type', 'cloudinary')
            except Exception as storage_error:
                logger.error(f"Storage error for capsule {capsule_id}: {storage_error}")
                raise ValueError(f"Failed to store capsule: {str(storage_error)}")
            
            # ========== DATABASE ==========
            
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
                'cloudinary_public_id': storage_info.get('public_id'),
                'cloudinary_url': storage_info.get('secure_url'),
                'gridfs_id': None,  # GridFS no longer used - all files go to Cloudinary
                'encryption_iv': iv,
                'original_size': original_size,
                'description': description,
                'created_at': datetime.utcnow(),
                'is_unlocked': False,
                'unlocked_at': None,
                'status': 'locked'
            }
            
            self.capsules.insert_one(doc)
            
            logger.info(f"Capsule {capsule_id} created successfully by user {user_id}")
            
            return {
                'capsule_id': capsule_id,
                'message': 'Capsule created successfully',
                'unlock_date': unlock_date.isoformat(),
                'storage_type': storage_type,
                'cloudinary_public_id': storage_info.get('public_id') if storage_type == 'cloudinary' else None,
                'cloudinary_url': storage_info.get('secure_url') if storage_type == 'cloudinary' else None
            }
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Failed to create capsule: {e}")
            raise Exception(f"Capsule creation failed: {str(e)}")

    def get_user_capsules(self, user_id, include_locked: bool = True) -> list:
        """Get all capsules for a user."""
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
                
                # Convert ObjectId fields
                if item.get('recipient_id') is not None:
                    try:
                        item['recipient_id'] = str(item['recipient_id']) if item['recipient_id'] is not None else None
                    except Exception:
                        pass
                
                # Convert datetime fields
                if item.get('unlocked_at'):
                    item['unlocked_at'] = item['unlocked_at'].isoformat()
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
                if item.get('unlock_date'):
                    item['unlock_date'] = item['unlock_date'].isoformat()
                
                # Build storage info object
                item['storage_info'] = {
                    'type': item.get('storage_type', 'cloudinary'),
                    'public_id': item.get('cloudinary_public_id'),
                    'url': item.get('cloudinary_url'),
                    'gridfs_id': None  # GridFS no longer used
                }
                
                # Keep storage fields at top level for easy frontend access
                # item.pop('cloudinary_public_id', None)  # Keep for frontend
                # item.pop('cloudinary_url', None)  # Keep for frontend
                # item.pop('gridfs_id', None)  # Keep for frontend
                # item.pop('storage_type', None)  # Keep for frontend
                
                results.append(item)
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve capsules for user {user_id}: {e}")
            raise Exception(f"Failed to retrieve capsules: {str(e)}")

    def get_capsule_metadata(self, capsule_id: str) -> dict:
        """Get capsule metadata by ID."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        item = dict(doc)
        item['_id'] = str(item['_id'])
        
        # Look up sender_name from users collection
        sender_id = item.get('user_id') or item.get('sender_id')
        if sender_id:
            try:
                from bson import ObjectId
                sender_doc = self.db.get_collection('users').find_one({'_id': ObjectId(sender_id)})
                if sender_doc:
                    item['sender_name'] = sender_doc.get('display_name')
                    item['sender_email'] = sender_doc.get('email')
            except Exception:
                pass
        
        # Look up recipient_name from users collection (for owner's view)
        recipient_id = item.get('recipient_id')
        if recipient_id:
            try:
                from bson import ObjectId
                recipient_doc = self.db.get_collection('users').find_one({'_id': ObjectId(recipient_id)})
                if recipient_doc:
                    item['recipient_name'] = recipient_doc.get('display_name')
                    item['recipient_display_email'] = recipient_doc.get('email')
            except Exception:
                pass
        
        # Build storage info
        item['storage_info'] = {
            'type': item.get('storage_type', 'cloudinary'),
            'public_id': item.get('cloudinary_public_id'),
            'url': item.get('cloudinary_url'),
            'gridfs_id': None  # GridFS no longer used
        }
        
        # Convert datetime fields
        if item.get('unlocked_at'):
            item['unlocked_at'] = item['unlocked_at'].isoformat()
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat()
        if item.get('unlock_date'):
            item['unlock_date'] = item['unlock_date'].isoformat()
        
        return item

    def unlock_capsule(self, capsule_id: str) -> dict:
        """Unlock a capsule and return decrypted content."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Build storage info for unlock
        storage_info = {
            'storage_type': doc.get('storage_type', 'cloudinary'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': None  # GridFS no longer used
        }
        
        # Read encrypted bytes
        try:
            data_bytes = self._retrieve_file(storage_info)
            encrypted_b64 = base64.b64encode(data_bytes).decode('utf-8')
            decrypted = self.encryption_service.decrypt_data(encrypted_b64, doc['encryption_iv'])
        except Exception as e:
            logger.error(f"[Capsule {capsule_id}] Failed to decrypt: {e}")
            raise ValueError(f"Failed to decrypt capsule: {str(e)}")

        # Update unlock status
        if not doc.get('is_unlocked'):
            self.capsules.update_one(
                {'_id': doc['_id']}, 
                {'$set': {'is_unlocked': True, 'unlocked_at': datetime.utcnow()}}
            )
            unlocked_at = datetime.utcnow().isoformat()
            message = 'Capsule unlocked successfully'
        else:
            unlocked_at = (doc['unlocked_at'].isoformat() if doc.get('unlocked_at') else None)
            message = 'Capsule already unlocked'

        return {
            'capsule_id': capsule_id,
            'filename': doc['filename'],
            'capsule_type': doc['capsule_type'],
            'data': decrypted.decode('utf-8') if doc['capsule_type'] == 'text' else base64.b64encode(decrypted).decode('utf-8'),
            'unlocked_at': unlocked_at,
            'message': message
        }

    def get_decrypted_file_data(self, capsule_id: str, allow_locked_for_owner: bool = False, user_id: str = None) -> tuple:
        """Get decrypted file data for download."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Check if locked
        if not doc.get('is_unlocked'):
            if allow_locked_for_owner and user_id:
                if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
                    raise ValueError('Capsule is not unlocked yet')
            else:
                raise ValueError('Capsule is not unlocked yet')
        
        # Build storage info for download
        storage_info = {
            'storage_type': doc.get('storage_type', 'cloudinary'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': None  # GridFS no longer used
        }
        
        # Read and decrypt
        data_bytes = self._retrieve_file(storage_info)
        encrypted_b64 = base64.b64encode(data_bytes).decode('utf-8')
        decrypted = self.encryption_service.decrypt_data(encrypted_b64, doc['encryption_iv'])
        
        # Determine content type
        filename = doc['filename']
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        content_types = {
            'txt': 'text/plain', 'pdf': 'application/pdf',
            'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif',
            'mp4': 'video/mp4', 'avi': 'video/x-msvideo', 'mov': 'video/quicktime',
            'mp3': 'audio/mpeg', 'wav': 'audio/wav', 'ogg': 'audio/ogg',
            'm4a': 'audio/mp4', 'aac': 'audio/aac', 'flac': 'audio/flac'
        }
        content_type = content_types.get(extension, 'application/octet-stream')
        
        return decrypted, filename, content_type

    def get_file_preview_for_edit(self, capsule_id: str, user_id: str) -> dict:
        """Get file data as base64 for preview when editing."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        if doc.get('user_id') != user_id and doc.get('sender_id') != user_id:
            raise ValueError('Capsule not found')
        
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

    def update_capsule(self, capsule_id: str, user_id: str, description: str = None, 
                       unlock_date: datetime = None, file_data: bytes = None, 
                       filename: str = None) -> dict:
        """Update capsule metadata and/or file."""
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
            # Users can now set any date (past, present, or future)
            # Past dates make the capsule immediately unlockable
            update_data['unlock_date'] = unlock_date
        
        # Handle file replacement
        if file_data is not None:
            if filename and not self._allowed_file(filename):
                raise ValueError(f"File type not allowed: {filename}")
            
            # Delete old file from Cloudinary
            old_storage_info = {
                'storage_type': doc.get('storage_type', 'cloudinary'),
                'public_id': doc.get('cloudinary_public_id'),
                'gridfs_id': None  # GridFS no longer used
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
            
            # Store new file in Cloudinary
            storage_info = self._store_file(encrypted_bytes, capsule_id, 
                filename or doc.get('filename', 'capsule'))
            storage_type = storage_info.get('storage_type', 'cloudinary')
            
            # Update metadata
            update_data['cloudinary_public_id'] = storage_info.get('public_id')
            update_data['cloudinary_url'] = storage_info.get('secure_url')
            update_data['gridfs_id'] = None  # GridFS no longer used
            update_data['storage_type'] = storage_type
            update_data['encryption_iv'] = iv
            update_data['original_size'] = len(file_data)
            if filename:
                update_data['filename'] = filename
                update_data['capsule_type'] = capsule_type
        
        if not update_data:
            raise ValueError('No update data provided')
        
        # Store old unlock_date for email notification
        old_unlock_date = doc.get('unlock_date')
        
        self.capsules.update_one(
            {'capsule_id': capsule_id},
            {'$set': update_data}
        )
        
        # Get updated metadata
        result = self.get_capsule_metadata(capsule_id)
        
        # Include old_unlock_date in result for email notification
        if old_unlock_date:
            result['old_unlock_date'] = old_unlock_date
        
        return result

    def delete_capsule(self, capsule_id: str, user_id: str) -> bool:
        """Delete a capsule and its stored file."""
        doc = self.capsules.find_one({'capsule_id': capsule_id})
        if not doc:
            raise ValueError('Capsule not found')
        
        # Check ownership
        if doc.get('user_id') != user_id:
            raise ValueError('Capsule not found')
        
        # Delete file from Cloudinary (gracefully handle missing files)
        storage_info = {
            'storage_type': doc.get('storage_type', 'cloudinary'),
            'public_id': doc.get('cloudinary_public_id'),
            'gridfs_id': None  # GridFS no longer used
        }
        try:
            self._delete_file(storage_info)
        except Exception as e:
            logger.warning(f"Could not delete file for capsule {capsule_id}: {e}")
        
        # Delete metadata
        result = self.capsules.delete_one({'capsule_id': capsule_id})
        if result.deleted_count == 0:
            raise ValueError('Failed to delete capsule')
        
        logger.info(f"Capsule {capsule_id} deleted by user {user_id}")
        return True
