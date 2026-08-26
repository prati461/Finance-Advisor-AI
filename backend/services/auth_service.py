from typing import Optional

from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.exceptions import ConflictException, UnauthorizedException
from backend.core.security import (
    decode_token,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise ConflictException("Email already exists")

        hashed_password = hash_password(payload.password)
        user = User(email=payload.email, full_name=payload.full_name, hashed_password=hashed_password)
        return self.user_repository.create(user)

    def authenticate(self, payload: LoginRequest) -> User:
        user = self.user_repository.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")
        return user

    def create_tokens(self, user: User) -> dict:
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except (JWTError, ValidationError):
            raise UnauthorizedException("Invalid refresh token")

        if payload.type != "refresh":
            raise UnauthorizedException("Invalid token type")

        user = self.user_repository.get_by_id(int(payload.sub))
        if not user:
            raise UnauthorizedException("User not found")

        access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
