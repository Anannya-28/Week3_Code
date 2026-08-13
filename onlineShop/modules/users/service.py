
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import AppError
from core.utils import hash_password
from modules.users.model import User
from modules.users.repository import UserRepository
from modules.users.schema import UserCreate

logger = logging.getLogger("online_shopping.users")


class UserService:
    @staticmethod
    def register(data: UserCreate, db: Session) -> User:
        name = data.name.strip()
        email = str(data.email).lower()

        if not name:
            raise AppError(400, "Name cannot be empty")

        if UserRepository.get_by_email(db, email):
            raise AppError(409, "Email is already registered")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(data.password),
            mobile=data.mobile,
            role=data.role,
        )

        try:
            result = UserRepository.create(db, user)
            logger.info(
                "USER REGISTERED | id=%s | email=%s | role=%s",
                result.id, email, data.role,
            )
            return result
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "Email is already registered") from exc
