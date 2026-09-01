from typing import Optional

from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.exceptions import ConflictException, UnauthorizedException
from backend.core.logging import logger
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
        logger.debug("AuthService: Initialized")

    def register(self, payload: RegisterRequest) -> User:
        logger.info("AuthService.register: Starting for email=%s", payload.email)
        
        logger.info("AuthService.register: Checking for existing user")
        existing_user = self.user_repository.get_by_email(payload.email)
        logger.info("AuthService.register: Existing user check complete")
        
        if existing_user:
            logger.warning("AuthService.register: Email already exists - %s", payload.email)
            raise ConflictException("Email already exists")

        logger.info("AuthService.register: Hashing password")
        hashed_password = hash_password(payload.password)
        logger.info("AuthService.register: Password hashed")
        
        logger.info("AuthService.register: Creating user model")
        user = User(email=payload.email, full_name=payload.full_name, hashed_password=hashed_password)
        logger.info("AuthService.register: User model created")
        
        logger.info("AuthService.register: Saving to database")
        user = self.user_repository.create(user)
        logger.info("AuthService.register: User saved successfully, user_id=%s", user.id)
        
        return user

    def authenticate(self, payload: LoginRequest) -> User:
        logger.info("AuthService.authenticate: Starting for email=%s", payload.email)
        user = self.user_repository.get_by_email(payload.email)
        logger.info("AuthService.authenticate: User lookup complete")
        
        if not user or not verify_password(payload.password, user.hashed_password):
            logger.warning("AuthService.authenticate: Invalid credentials for email=%s", payload.email)
            raise UnauthorizedException("Invalid credentials")
        
        logger.info("AuthService.authenticate: Authentication successful, user_id=%s", user.id)
        return user

    def create_tokens(self, user: User) -> dict:
        logger.info("AuthService.create_tokens: Starting for user_id=%s", user.id)
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        logger.info("AuthService.create_tokens: Tokens created successfully")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str) -> dict:
        logger.info("AuthService.refresh: Starting")
        try:
            payload = decode_token(refresh_token)
            logger.info("AuthService.refresh: Token decoded successfully")
        except (JWTError, ValidationError):
            logger.warning("AuthService.refresh: Invalid refresh token")
            raise UnauthorizedException("Invalid refresh token")

        if payload.type != "refresh":
            logger.warning("AuthService.refresh: Invalid token type=%s", payload.type)
            raise UnauthorizedException("Invalid token type")

        logger.info("AuthService.refresh: Looking up user")
        user = self.user_repository.get_by_id(int(payload.sub))
        if not user:
            logger.warning("AuthService.refresh: User not found")
            raise UnauthorizedException("User not found")

        logger.info("AuthService.refresh: Creating new tokens for user_id=%s", user.id)
        access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))
        logger.info("AuthService.refresh: New tokens created successfully")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
