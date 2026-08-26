from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.core.exceptions import NotFoundException
from backend.schemas.common import PaginatedResponse
from backend.schemas.finance import IncomeCreate, IncomeRead, IncomeUpdate
from backend.services.income_service import IncomeService

router = APIRouter(prefix="/incomes", tags=["incomes"])


@router.post("", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
def create_income(
    payload: IncomeCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> IncomeRead:
    service = IncomeService(db)
    income = service.create_income(current_user.id, payload)
    return IncomeRead.model_validate(income)


@router.get("", response_model=PaginatedResponse[IncomeRead])
def list_incomes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[IncomeRead]:
    service = IncomeService(db)
    skip = (page - 1) * page_size
    total, incomes = service.list_incomes(
        current_user.id,
        skip,
        page_size,
        category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=[IncomeRead.model_validate(item) for item in incomes])


@router.get("/{income_id}", response_model=IncomeRead)
def get_income(
    income_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> IncomeRead:
    service = IncomeService(db)
    try:
        income = service.get_income(current_user.id, income_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return IncomeRead.model_validate(income)


@router.put("/{income_id}", response_model=IncomeRead)
def update_income(
    income_id: int,
    payload: IncomeUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> IncomeRead:
    service = IncomeService(db)
    try:
        income = service.update_income(current_user.id, income_id, payload)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return IncomeRead.model_validate(income)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = IncomeService(db)
    try:
        service.delete_income(current_user.id, income_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
