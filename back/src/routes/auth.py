import secrets
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_user, hash_password
from core.config import settings
from services.auth import AuthService
from services.email_service import email_service
from schemas.auth import UserLogin, UserRegister, Token, UserResponse
from models.user import User
from models.password_reset import PasswordResetToken

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    email: str = Form(..., description="Valid email address"),
    password: str = Form(..., description="User password (will be hashed)"),
    full_name: str = Form(..., description="User's full name"),
    db: Session = Depends(get_db)
):
    user_data = UserRegister(email=email, password=password, full_name=full_name)
    auth_service = AuthService(db)
    user = auth_service.register(user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    email: str = Form(..., description="User's email"),
    password: str = Form(..., description="User's password"),
    db: Session = Depends(get_db)
):
    """
    Login and get access and refresh tokens
    """
    credentials = UserLogin(email=email, password=password)
    auth_service = AuthService(db)
    return auth_service.login(credentials)


@router.post("/refresh", response_model=Token)
def refresh(
    refresh_token: str = Form(..., description="Refresh token"),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_token)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    # Siempre responder igual para no exponer si el email existe
    if not user or not user.is_active:
        return {"message": "Si el correo existe, recibirás un enlace de recuperación"}

    # Invalidar tokens anteriores no usados
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})
    db.commit()

    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires))
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    try:
        email_service.send_password_reset(user.email, reset_link, user.full_name)
    except Exception as e:
        logger.error(f"Error enviando email de recuperación: {e}")

    return {"message": "Si el correo existe, recibirás un enlace de recuperación"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")

    now = datetime.now(timezone.utc)
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > now
    ).first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ya expiró")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ya expiró")

    user.password_hash = hash_password(password)
    reset_token.used = True
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user information

    Requires authentication token in header:
    ```
    Authorization: Bearer <token>
    ```
    """
    auth_service = AuthService(db)
    user = auth_service.get_current_user_info(current_user["user_id"])
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(
    full_name: str = Form(..., description="User's full name"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the authenticated user's profile (full name)."""
    auth_service = AuthService(db)
    return auth_service.update_profile(current_user["user_id"], full_name)


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    current_password: str = Form(..., description="Current password"),
    new_password: str = Form(..., description="New password"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the authenticated user's password."""
    auth_service = AuthService(db)
    auth_service.change_password(current_user["user_id"], current_password, new_password)
    return {"message": "Contraseña actualizada correctamente"}
