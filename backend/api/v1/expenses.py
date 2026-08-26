from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.v1.dependencies import get_current_user, get_db_session
from backend.core.exceptions import NotFoundException
from backend.schemas.common import PaginatedResponse
from backend.schemas.finance import ExpenseCreate, ExpenseRead, ExpenseUpdate
from backend.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExpenseRead:
    service = ExpenseService(db)
    expense = service.create_expense(current_user.id, payload)
    return ExpenseRead.model_validate(expense)


@router.get("", response_model=PaginatedResponse[ExpenseRead])
def list_expenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[ExpenseRead]:
    service = ExpenseService(db)
    skip = (page - 1) * page_size
    total, expenses = service.list_expenses(
        current_user.id,
        skip,
        page_size,
        category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=[ExpenseRead.model_validate(item) for item in expenses])


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExpenseRead:
    service = ExpenseService(db)
    try:
        expense = service.get_expense(current_user.id, expense_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return ExpenseRead.model_validate(expense)


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ExpenseRead:
    service = ExpenseService(db)
    try:
        expense = service.update_expense(current_user.id, expense_id, payload)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return ExpenseRead.model_validate(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    service = ExpenseService(db)
    try:
        service.delete_expense(current_user.id, expense_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
