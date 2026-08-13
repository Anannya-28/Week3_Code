
from unittest.mock import MagicMock, patch
import pytest

from core.exceptions import AppError
from modules.users.schema import UserCreate
from modules.users.service import UserService


class TestUserService:

    def test_register_success(self):
        db = MagicMock()
        data = UserCreate(
            name="Alice",
            email="alice@test.com",
            password="password123",
            mobile="9876543210",
            role="customer",
        )

        with patch(
            "modules.users.service.UserRepository.get_by_email",
            return_value=None,
        ), patch(
            "modules.users.service.UserRepository.create",
            return_value=MagicMock(id=1, email="alice@test.com"),
        ):
            result = UserService.register(data, db)

        assert result.email == "alice@test.com"

    def test_register_duplicate_email_raises_409(self):
        db = MagicMock()
        data = UserCreate(
            name="Bob",
            email="bob@test.com",
            password="password123",
            mobile="9876543210",
        )

        with patch(
            "modules.users.service.UserRepository.get_by_email",
            return_value=MagicMock(),   # already exists
        ):
            with pytest.raises(AppError) as exc_info:
                UserService.register(data, db)

        assert exc_info.value.status_code == 409

    def test_register_empty_name_raises_400(self):
        db = MagicMock()
        data = UserCreate(
            name="   ",   
            email="user@test.com",
            password="password123",
            mobile="9876543210",
        )

        with patch(
            "modules.users.service.UserRepository.get_by_email",
            return_value=None,
        ):
            with pytest.raises(AppError) as exc_info:
                UserService.register(data, db)

        assert exc_info.value.status_code == 400

    def test_register_assigns_correct_role(self):
        db = MagicMock()
        data = UserCreate(
            name="Admin User",
            email="admin@test.com",
            password="adminpass1",
            mobile="9876543210",
            role="admin",
        )
        created_user = MagicMock(id=2, email="admin@test.com", role="admin")

        with patch(
            "modules.users.service.UserRepository.get_by_email",
            return_value=None,
        ), patch(
            "modules.users.service.UserRepository.create",
            return_value=created_user,
        ):
            result = UserService.register(data, db)

        assert result.role == "admin"
