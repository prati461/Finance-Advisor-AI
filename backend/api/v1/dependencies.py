from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.exceptions import UnauthorizedException
from backend.core.security import TokenPayload, decode_token
from backend.database import get_db
from backend.models.user import User
from backend.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)
) -> User:
    try:
        payload = decode_token(token)
        if payload.type != "access":
            raise UnauthorizedException("Invalid token type")
        user_id = int(payload.sub)
    except (JWTError, ValidationError, ValueError):
        raise UnauthorizedException("Could not validate credentials")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User not found")
    return user
