import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.exceptions import AppError
from core.security import decode_token
from modules.users.repository import UserRepository
from modules.catalog.repository import ProductRepository  # adjust if needed

logger = logging.getLogger("online_shopping.auth")

OAuth2_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(OAuth2_schema),
    db: Session = Depends(get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise credential_exception

    except AppError:
        raise credential_exception

    user = UserRepository.get_by_id(db, int(user_id))

    if user is None:
        logger.warning("TOKEN VALID but USER NOT FOUND | user_id=%s", user_id)
        raise credential_exception

    return user


def require_roles(*allowed_roles: str):
    def role_dependency(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )
        return current_user
    return role_dependency


def can_manage_product(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product = ProductRepository.get_by_id(db, id)  # adjust if needed

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    is_admin = current_user.role == "admin"
    is_owner = (
        current_user.role == "seller"
        and product.user_id == current_user.id
    )

    if is_admin or is_owner:
        return product

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You can manage only your own products"
    )

