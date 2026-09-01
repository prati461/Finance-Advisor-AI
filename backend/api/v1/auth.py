from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_db_session
from backend.core.exceptions import ConflictException, UnauthorizedException
from backend.core.logging import logger
from backend.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)) -> TokenResponse:
    try:
        logger.info("Register: Starting registration for email=%s", payload.email)
        
        service = AuthService(db)
        logger.info("Register: AuthService created")
        
        logger.info("Register: Calling service.register()")
        user = service.register(payload)
        logger.info("Register: User created successfully, user_id=%s", user.id)
        
    except ConflictException as exc:
        logger.warning("Register: Conflict error - %s", exc.detail)
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as exc:
        logger.exception("Register: Unexpected error during registration: %s", exc)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(exc)}")

    try:
        logger.info("Register: Creating tokens")
        tokens = service.create_tokens(user)
        logger.info("Register: Tokens created successfully")
        return TokenResponse(**tokens)
    except Exception as exc:
        logger.exception("Register: Error creating tokens: %s", exc)
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(exc)}")


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
