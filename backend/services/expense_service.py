from datetime import date
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException
from backend.models.expense import Expense
from backend.repositories.expense_repository import ExpenseRepository
from backend.schemas.finance import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    def __init__(self, db: Session) -> None:
        self.repository = ExpenseRepository(db)

    def get_expense(self, user_id: int, expense_id: int) -> Expense:
        expense = self.repository.get(user_id, expense_id)
        if not expense:
            raise NotFoundException("Expense record not found")
        return expense

    def list_expenses(
        self,
        user_id: int,
        skip: int,
        limit: int,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, list[Expense]]:
        return self.repository.list(user_id, skip=skip, limit=limit, category=category, start_date=start_date, end_date=end_date, search=search)

    def create_expense(self, user_id: int, payload: ExpenseCreate) -> Expense:
        expense = Expense(user_id=user_id, **payload.model_dump())
        return self.repository.create(expense)

    def update_expense(self, user_id: int, expense_id: int, payload: ExpenseUpdate) -> Expense:
        expense = self.get_expense(user_id, expense_id)
        return self.repository.update(expense, payload.model_dump(exclude_none=True))

    def delete_expense(self, user_id: int, expense_id: int) -> None:
        expense = self.get_expense(user_id, expense_id)
        self.repository.delete(expense)

    def compute_total(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
        return self.repository.total_amount(user_id, start_date=start_date, end_date=end_date)
