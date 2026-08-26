from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_db_session
from backend.core.exceptions import ConflictException, UnauthorizedException
from backend.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)) -> TokenResponse:
    service = AuthService(db)
    try:
        user = service.register(payload)
    except ConflictException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    tokens = service.create_tokens(user)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> TokenResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(payload)
    except UnauthorizedException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    tokens = service.create_tokens(user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db_session)) -> TokenResponse:
    try:
        payload_data = AuthService(db).refresh(payload.refresh_token)
    except UnauthorizedException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return TokenResponse(**payload_data)
