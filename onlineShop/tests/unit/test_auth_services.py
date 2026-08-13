from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from core.exceptions import AppError
from modules.auth.service import AuthService



class TestAuthService:

    def _make_mock_user(self):
        user = MagicMock()
        user.id = 1
        user.role = "customer"
        user.email = "test@test.com"
        user.name = "Test User"      
        user.mobile = "9999999999"   
        user.password_hash = "hashed_password"
        return user

    def test_login_success_returns_tokens(self):
        db = MagicMock()

        with patch("modules.auth.service.UserRepository.get_by_email", return_value=self._make_mock_user()), \
             patch("modules.auth.service.verify_password", return_value=True):
            result = AuthService.login("test@test.com", "securepass1", db)

        assert result.access_token is not None   
        assert result.refresh_token is not None  

    def test_login_wrong_password_raises_401(self):
        db = MagicMock()

        with patch("modules.auth.service.UserRepository.get_by_email", return_value=self._make_mock_user()), \
             patch("modules.auth.service.verify_password", return_value=False):
            with pytest.raises(AppError) as exc:
                AuthService.login("test@test.com", "wrongpass", db)

        assert exc.value.status_code == 401

    def test_login_unknown_email_raises_401(self):
        db = MagicMock()

        with patch("modules.auth.service.UserRepository.get_by_email", return_value=None):
            with pytest.raises(AppError) as exc:
                AuthService.login("ghost@unknown.com", "anypassword", db)

        assert exc.value.status_code == 401