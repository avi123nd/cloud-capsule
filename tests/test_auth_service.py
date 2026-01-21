"""
Unit tests for AuthService (MongoDB + JWT)
"""

import pytest
from unittest.mock import Mock
from services.auth_service import AuthService


class TestAuthService:
    def setup_method(self):
        self.mock_db = Mock()
        self.users = Mock()
        self.mock_db.get_collection.return_value = self.users
        self.svc = AuthService(self.mock_db, 'test-jwt-secret')

    def test_create_user_success(self):
        self.users.find_one.return_value = None
        self.users.insert_one.return_value = Mock(inserted_id='abc123')
        user = self.svc.create_user('test@example.com', 'Password1!', 'Tester')
        assert user['email'] == 'test@example.com'
        assert user['uid'] == 'abc123'

    def test_create_user_duplicate(self):
        self.users.find_one.return_value = {'email': 'test@example.com'}
        with pytest.raises(Exception, match='Email already registered'):
            self.svc.create_user('test@example.com', 'Password1!')

    def test_login_success(self):
        # Prepare a hashed password
        hashed = self.svc.hash_password('Password1!')
        self.users.find_one.return_value = {'_id': 'abc123', 'email': 'test@example.com', 'password': hashed}
        result = self.svc.login('test@example.com', 'Password1!')
        assert 'token' in result
        assert result['user']['uid'] == 'abc123'

    def test_login_invalid(self):
        self.users.find_one.return_value = None
        with pytest.raises(Exception, match='Invalid credentials'):
            self.svc.login('no@example.com', 'bad')
