from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.core.exceptions import NotFoundException
from backend.schemas.common import PaginatedResponse
from backend.schemas.finance import BudgetCreate, BudgetRead, BudgetUpdate
from backend.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BudgetRead:
    service = BudgetService(db)
    budget = service.create_budget(current_user.id, payload)
    return BudgetRead.model_validate(budget)


@router.get("", response_model=PaginatedResponse[BudgetRead])
def list_budgets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[BudgetRead]:
    service = BudgetService(db)
    skip = (page - 1) * page_size
    total, budgets = service.list_budgets(
        current_user.id,
        skip,
        page_size,
        category=category,
        month=month,
        year=year,
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=[BudgetRead.model_validate(item) for item in budgets])


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(
    budget_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BudgetRead:
    service = BudgetService(db)
    try:
        budget = service.get_budget(current_user.id, budget_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return BudgetRead.model_validate(budget)


@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BudgetRead:
    service = BudgetService(db)
    try:
        budget = service.update_budget(current_user.id, budget_id, payload)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return BudgetRead.model_validate(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = BudgetService(db)
    try:
        service.delete_budget(current_user.id, budget_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
