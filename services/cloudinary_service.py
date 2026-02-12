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
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        
        print("\n=== CLOUDINARY INIT DEBUG ===")
        
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        print(f"cloud_name: {cloud_name}")
        print(f"api_key set: {api_key is not None}")
        print(f"api_secret set: {api_secret is not None}")
        
        # Validate all credentials
        if not cloud_name:
            print("❌ ERROR: CLOUDINARY_CLOUD_NAME is empty or not set")
            print("=== END CLOUDINARY INIT ===\n")
            raise ValueError("CLOUDINARY_CLOUD_NAME is empty or not set")
        if not api_key:
            print("❌ ERROR: CLOUDINARY_API_KEY is empty or not set")
            print("=== END CLOUDINARY INIT ===\n")
            raise ValueError("CLOUDINARY_API_KEY is empty or not set")
        if not api_secret:
            print("❌ ERROR: CLOUDINARY_API_SECRET is empty or not set")
            print("=== END CLOUDINARY INIT ===\n")
            raise ValueError("CLOUDINARY_API_SECRET is empty or not set")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        self.cloud_name = cloud_name
        self.folder = os.getenv('CLOUDINARY_FOLDER', 'time_capsules')
        
        print(f"✅ SUCCESS: Cloudinary configured: cloud_name={self.cloud_name}, folder={self.folder}")
        print("=== END CLOUDINARY INIT ===\n")
    
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
            
            # Convert bytes to base64 string
            b64_data = base64.b64encode(encrypted_data).decode('utf-8')
            
            # Use data URI format for base64 upload
            data_uri = f"data:application/octet-stream;base64,{b64_data}"
            
            # Upload to Cloudinary using file parameter with data URI
            result = cloudinary.uploader.upload(
                data_uri,
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
            
            print(f"✅ Uploaded to Cloudinary: {result.get('public_id')}")
            print(f"URL: {result.get('secure_url')}")
            
            return {
                'public_id': result['public_id'],
                'secure_url': result['secure_url'],
                'url': result['url'],
                'resource_type': result['resource_type'],
                'created_at': result['created_at']
            }
            
        except Exception as e:
            print(f"❌ Failed to upload file to Cloudinary: {e}")
            import traceback
            traceback.print_exc()
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
            # Use Cloudinary's built-in download API
            result = cloudinary.api.resource(public_id, resource_type='raw')
            url = result['secure_url']
            
            # Download using urllib (built into Python)
            import urllib.request
            with urllib.request.urlopen(url) as response:
                return response.read()
            
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
