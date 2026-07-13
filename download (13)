from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from repositories.user import UserRepository
from core.auth import verify_password, create_access_token, create_refresh_token, decode_refresh_token
from schemas.auth import UserLogin, UserRegister, Token
from models.user import User
from core.config import settings


class AuthService:
    """Service for authentication logic"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserRegister) -> User:
        """
        Register a new user

        Args:
            user_data: User registration data

        Returns:
            Created user

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        if self.user_repo.exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = self.user_repo.create(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )

        return user

    def login(self, credentials: UserLogin) -> Token:
        """
        Authenticate user and return tokens
        """
        # Get user by email
        user = self.user_repo.get_by_email(credentials.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )

        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_token(self, refresh_token: str) -> Token:
        """
        Validate refresh token and return new tokens
        """
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )

        return Token(access_token=access_token, refresh_token=new_refresh_token)

    def get_current_user_info(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(UUID(user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    def update_profile(self, user_id: str, full_name: str) -> User:
        full_name = (full_name or "").strip()
        if not full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre no puede estar vacío"
            )
        user = self.get_current_user_info(user_id)
        return self.user_repo.update_full_name(user, full_name)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 8 caracteres"
            )
        user = self.get_current_user_info(user_id)
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        self.user_repo.set_password(user, new_password)
