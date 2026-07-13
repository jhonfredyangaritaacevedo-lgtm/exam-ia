from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from models.user import User
from core.auth import hash_password


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password: str, full_name: str) -> User:
        password_hash = hash_password(password)
        db_user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

    def update_full_name(self, user: User, full_name: str) -> User:
        user.full_name = full_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_password(self, user: User, new_password: str) -> User:
        user.password_hash = hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user
