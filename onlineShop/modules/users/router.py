from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user   # ← your JWT dependency
from modules.users.model import User
from modules.users.schema import UserCreate, UserOut
from modules.users.service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


# ── Public ────────────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(request: UserCreate, db: Session = Depends(get_db)):
    return UserService.register(request, db)


# ── Protected — Milestone 1 ───────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current logged-in user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """

    """
    return current_user