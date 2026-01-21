"""
Unit tests for EncryptionService
"""

import pytest
import os
import tempfile
from services.encryption_service import EncryptionService

class TestEncryptionService:
    """Test cases for EncryptionService."""
    
    def setup_method(self):
        """Set up test environment."""
        # Set a test encryption key
        os.environ['ENCRYPTION_KEY'] = 'test-key-32-characters-long-123'
        self.encryption_service = EncryptionService()
    
    def test_encrypt_decrypt_data(self):
        """Test basic encryption and decryption of data."""
        test_data = b"Hello, Time Capsule Cloud!"
        
        # Encrypt the data
        encrypted_result = self.encryption_service.encrypt_data(test_data)
        
        # Verify encryption result structure
        assert 'encrypted_data' in encrypted_result
        assert 'iv' in encrypted_result
        assert encrypted_result['encrypted_data'] != test_data.decode('utf-8')
        
        # Decrypt the data
        decrypted_data = self.encryption_service.decrypt_data(
            encrypted_result['encrypted_data'],
            encrypted_result['iv']
        )
        
        # Verify decryption
        assert decrypted_data == test_data
    
    def test_encrypt_decrypt_file(self):
        """Test encryption and decryption of files."""
        test_content = b"This is a test file for encryption."
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Encrypt the file
            encrypted_result = self.encryption_service.encrypt_file(temp_file_path)
            
            # Verify encryption result
            assert 'encrypted_data' in encrypted_result
            assert 'iv' in encrypted_result
            assert 'original_size' in encrypted_result
            assert encrypted_result['original_size'] == len(test_content)
            
            # Create output file path
            output_path = temp_file_path + '.decrypted'
            
            # Decrypt the file
            decrypted_path = self.encryption_service.decrypt_file(
                encrypted_result['encrypted_data'],
                encrypted_result['iv'],
                output_path
            )
            
            # Verify decrypted file
            assert decrypted_path == output_path
            with open(decrypted_path, 'rb') as f:
                decrypted_content = f.read()
            assert decrypted_content == test_content
            
            # Clean up
            os.unlink(decrypted_path)
            
        finally:
            # Clean up original file
            os.unlink(temp_file_path)
    
    def test_encryption_key_validation(self):
        """Test encryption key validation."""
        # Test with invalid key length
        os.environ['ENCRYPTION_KEY'] = 'short-key'
        with pytest.raises(ValueError, match="ENCRYPTION_KEY must be exactly 32 characters long"):
            EncryptionService()
        
        # Test with missing key
        del os.environ['ENCRYPTION_KEY']
        with pytest.raises(ValueError, match="ENCRYPTION_KEY environment variable is required"):
            EncryptionService()
    
    def test_different_data_types(self):
        """Test encryption with different types of data."""
        test_cases = [
            b"Simple text",
            b"Text with special characters: !@#$%^&*()",
            b"Multiline\ntext\nwith\nnewlines",
            b"Binary data: \x00\x01\x02\x03",
            b"Large text: " + b"A" * 1000
        ]
        
        for test_data in test_cases:
            # Encrypt
            encrypted_result = self.encryption_service.encrypt_data(test_data)
            
            # Decrypt
            decrypted_data = self.encryption_service.decrypt_data(
                encrypted_result['encrypted_data'],
                encrypted_result['iv']
            )
            
            # Verify
            assert decrypted_data == test_data
    
    def test_encryption_uniqueness(self):
        """Test that encryption produces different results for same input."""
        test_data = b"Same input data"
        
        # Encrypt the same data twice
        encrypted1 = self.encryption_service.encrypt_data(test_data)
        encrypted2 = self.encryption_service.encrypt_data(test_data)
        
        # Verify different encrypted results (due to random IV)
        assert encrypted1['encrypted_data'] != encrypted2['encrypted_data']
        assert encrypted1['iv'] != encrypted2['iv']
        
        # But both should decrypt to the same original data
        decrypted1 = self.encryption_service.decrypt_data(
            encrypted1['encrypted_data'], encrypted1['iv']
        )
        decrypted2 = self.encryption_service.decrypt_data(
            encrypted2['encrypted_data'], encrypted2['iv']
        )
        
        assert decrypted1 == test_data
        assert decrypted2 == test_data
