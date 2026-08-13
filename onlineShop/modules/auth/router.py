from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from modules.auth.schema import LoginResponse, RefreshRequest, TokenResponse
from modules.auth.service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access + refresh tokens.
    Access token expires in 30 min; refresh token valid 7 days.
    """
    return AuthService.login(form_data.username, form_data.password, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Issue a new access token using a valid refresh token."""
    return AuthService.refresh(request, db)