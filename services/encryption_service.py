"""
Encryption Service for Time Capsule Cloud

This module handles AES-256 encryption and decryption of capsule data
using PyCryptodome for secure storage.
"""

import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class EncryptionService:
    """Service for handling encryption and decryption of capsule data."""
    
    def __init__(self):
        """Initialize the encryption service with the encryption key."""
        self.key = self._get_encryption_key()
    
    def _get_encryption_key(self):
        """Get the encryption key from environment variables."""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY environment variable is required. "
                "Generate a 32-character key and add it to your .env file."
            )
        
        # Ensure key is 32 bytes (256 bits) for AES-256
        if len(key) != 32:
            raise ValueError(
                f"ENCRYPTION_KEY must be exactly 32 characters long. "
                f"Current length: {len(key)} characters. "
                f"Please update your .env file."
            )
        
        return key.encode('utf-8')
    
    def encrypt_data(self, data):
        """
        Encrypt data using AES-256 in CBC mode.
        
        Args:
            data (bytes): The data to encrypt
            
        Returns:
            dict: Dictionary containing encrypted data and initialization vector
        """
        try:
            # Generate a random initialization vector
            iv = get_random_bytes(16)
            
            # Create cipher object
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Pad the data to block size
            padded_data = pad(data, AES.block_size)
            
            # Encrypt the data
            encrypted_data = cipher.encrypt(padded_data)
            
            # Encode to base64 for storage
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            
            return {
                'encrypted_data': encrypted_b64,
                'iv': iv_b64
            }
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data, iv):
        """
        Decrypt data using AES-256 in CBC mode.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            iv (str): Base64 encoded initialization vector
            
        Returns:
            bytes: The decrypted data
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            iv_bytes = base64.b64decode(iv)
            
            # Create cipher object
            cipher = AES.new(self.key, AES.MODE_CBC, iv_bytes)
            
            # Decrypt the data
            decrypted_padded = cipher.decrypt(encrypted_bytes)
            
            # Remove padding
            decrypted_data = unpad(decrypted_padded, AES.block_size)
            
            return decrypted_data
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path):
        """
        Encrypt a file and return the encrypted data.
        
        Args:
            file_path (str): Path to the file to encrypt
            
        Returns:
            dict: Dictionary containing encrypted file data and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_result = self.encrypt_data(file_data)
            
            return {
                'encrypted_data': encrypted_result['encrypted_data'],
                'iv': encrypted_result['iv'],
                'original_size': len(file_data)
            }
            
        except Exception as e:
            raise Exception(f"File encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_data, iv, output_path):
        """
        Decrypt file data and save to output path.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data
            iv (str): Base64 encoded initialization vector
            output_path (str): Path where decrypted file should be saved
            
        Returns:
            str: Path to the decrypted file
        """
        try:
            decrypted_data = self.decrypt_data(encrypted_data, iv)
            
            with open(output_path, 'wb') as file:
                file.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"File decryption failed: {str(e)}")
