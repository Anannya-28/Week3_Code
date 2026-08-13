import logging

from sqlalchemy.orm import Session

from core.exceptions import AppError
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from core.utils import verify_password
from modules.users.repository import UserRepository
from modules.users.schema import UserOut
from modules.auth.schema import LoginResponse, RefreshRequest, TokenResponse

logger = logging.getLogger("online_shopping.auth")


class AuthService:

    @staticmethod
    def login(username: str, password: str, db: Session) -> LoginResponse:
        # OAuth2PasswordRequestForm sends email in the username field
        email = username.lower()

        user = UserRepository.get_by_email(db, email)

        if not user or not verify_password(password, user.password_hash):
            logger.warning("LOGIN FAILED | email=%s", email)
            raise AppError(401, "Invalid email or password")

        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        logger.info(
            "LOGIN SUCCESS | user_id=%s | role=%s", user.id, user.role
        )

        return LoginResponse(
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserOut.model_validate(user),
        )

    @staticmethod
    def refresh(data: RefreshRequest, db: Session) -> TokenResponse:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise AppError(401, "Invalid token type — use refresh token here")

        user = UserRepository.get_by_id(db, int(payload["sub"]))
        if not user:
            raise AppError(401, "User not found")

        logger.info("TOKEN REFRESHED | user_id=%s", user.id)
        return TokenResponse(
            access_token=create_access_token(user.id, user.role)
        )