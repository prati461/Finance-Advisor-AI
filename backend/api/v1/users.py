from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from backend.models.user import User
from backend.schemas.user import ChangePasswordRequest, UserRead, UserUpdate
from backend.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_current_profile(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> UserRead:
    service = UserService(db)
    try:
        user = service.update_profile(current_user.id, payload)
    except ConflictException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return UserRead.model_validate(user)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = UserService(db)
    try:
        service.change_password(current_user.id, payload)
    except UnauthorizedException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = UserService(db)
    service.delete_account(current_user.id)
