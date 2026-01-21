"""
Unit tests for CapsuleService (MongoDB + GridFS)
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from services.capsule_service import CapsuleService
from services.encryption_service import EncryptionService


class TestCapsuleService:
    def setup_method(self):
        self.mock_db = Mock()
        self.mock_capsules = Mock()
        self.mock_db.get_collection.return_value = self.mock_capsules
        self.mock_fs = Mock()
        # Patch GridFS inside service by assigning attribute after init
        self.enc = EncryptionService()
        self.svc = CapsuleService(self.mock_db, self.enc)
        self.svc.fs = self.mock_fs

    def test_allowed_file_extensions(self):
        assert self.svc._allowed_file('a.txt')
        assert not self.svc._allowed_file('a.exe')

    def test_file_type_detection(self):
        assert self.svc._get_file_type('a.txt') == 'text'
        assert self.svc._get_file_type('a.png') == 'image'
        assert self.svc._get_file_type('a.mp4') == 'video'

    def test_create_capsule_success(self):
        self.mock_fs.put.return_value = 'grid-id'
        self.mock_capsules.insert_one.return_value = Mock(inserted_id='docid')
        future = datetime.utcnow() + timedelta(days=1)
        data = b'hello world'
        result = self.svc.create_capsule('u1', data, 'note.txt', future, 'desc')
        assert result['message'] == 'Capsule created successfully'

    def test_create_capsule_invalid_type(self):
        future = datetime.utcnow() + timedelta(days=1)
        with pytest.raises(ValueError):
            self.svc.create_capsule('u1', b'data', 'bad.exe', future)
