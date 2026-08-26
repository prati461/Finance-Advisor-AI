from typing import Optional

from sqlalchemy.orm import Session

from backend.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from backend.core.security import hash_password, verify_password
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import ChangePasswordRequest, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def update_profile(self, user_id: int, payload: UserUpdate) -> User:
        user = self.get_user(user_id)
        if payload.email and payload.email != user.email:
            existing_user = self.user_repository.get_by_email(payload.email)
            if existing_user:
                raise ConflictException("Email is already in use")
        return self.user_repository.update(user, payload.model_dump(exclude_none=True))

    def change_password(self, user_id: int, payload: ChangePasswordRequest) -> None:
        user = self.get_user(user_id)
        if not verify_password(payload.current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")
        user.hashed_password = hash_password(payload.new_password)
        self.user_repository.update(user, {"hashed_password": user.hashed_password})

    def delete_account(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.user_repository.delete(user)
