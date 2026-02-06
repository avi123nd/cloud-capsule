"""
Cloudinary Storage Service for Time Capsule Cloud

This service handles uploading and retrieving encrypted capsule files
from Cloudinary cloud storage.
"""

import os
import base64
import uuid
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudinaryStorageService:
    """Service for storing encrypted capsule files in Cloudinary."""
    
    def __init__(self):
        """Initialize Cloudinary with credentials from environment variables."""
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        self.folder = os.getenv('CLOUDINARY_FOLDER', 'time_capsules')
        
        # Validate configuration
        if not self.cloud_name:
            raise ValueError("CLOUDINARY_CLOUD_NAME environment variable is required")
        
        logger.info(f"Cloudinary storage initialized with folder: {self.folder}")
    
    def upload_encrypted_file(self, encrypted_data: bytes, capsule_id: str, content_type: str = 'application/octet-stream') -> dict:
        """
        Upload encrypted file to Cloudinary.
        
        Args:
            encrypted_data: Encrypted file bytes
            capsule_id: Unique capsule identifier
            content_type: MIME type of the original file
            
        Returns:
            dict with upload details including public_id and secure_url
        """
        try:
            # Generate unique public_id for the file
            public_id = f"{self.folder}/{capsule_id}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                base64.b64encode(encrypted_data).decode('utf-8'),
                resource_type='raw',
                public_id=public_id,
                folder=self.folder,
                tags=['encrypted', 'time_capsule', capsule_id],
                context={
                    'capsule_id': capsule_id,
                    'created_at': datetime.utcnow().isoformat(),
                    'encrypted': 'true'
                }
            )
            
            logger.info(f"Uploaded encrypted file to Cloudinary: {public_id}")
            
            return {
                'public_id': result['public_id'],
                'secure_url': result['secure_url'],
                'url': result['url'],
                'resource_type': result['resource_type'],
                'created_at': result['created_at']
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file to Cloudinary: {e}")
            raise Exception(f"Cloudinary upload failed: {str(e)}")
    
    def get_encrypted_file(self, public_id: str) -> bytes:
        """
        Retrieve encrypted file from Cloudinary.
        
        Args:
            public_id: The public_id of the file in Cloudinary
            
        Returns:
            bytes: The encrypted file data
        """
        try:
            # Get file from Cloudinary
            result = cloudinary.api.resource(public_id, resource_type='raw')
            
            # Download the file
            url = result['secure_url']
            
            import requests
            response = requests.get(url)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to retrieve file from Cloudinary: {e}")
            raise Exception(f"Cloudinary retrieval failed: {str(e)}")
    
    def delete_file(self, public_id: str) -> bool:
        """
        Delete file from Cloudinary.
        
        Args:
            public_id: The public_id of the file in Cloudinary
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            cloudinary.uploader.destroy(public_id, resource_type='raw')
            logger.info(f"Deleted file from Cloudinary: {public_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from Cloudinary: {e}")
            return False
    
    def get_file_url(self, public_id: str) -> str:
        """
        Get the URL of a file in Cloudinary.
        
        Args:
            public_id: The public_id of the file
            
        Returns:
            str: The secure URL of the file
        """
        try:
            result = cloudinary.api.resource(public_id, resource_type='raw')
            return result['secure_url']
        except Exception as e:
            logger.error(f"Failed to get file URL from Cloudinary: {e}")
            raise Exception(f"Failed to get file URL: {str(e)}")
    
    def file_exists(self, public_id: str) -> bool:
        """
        Check if a file exists in Cloudinary.
        
        Args:
            public_id: The public_id of the file
            
        Returns:
            bool: True if the file exists
        """
        try:
            cloudinary.api.resource(public_id, resource_type='raw')
            return True
        except Exception:
            return False
