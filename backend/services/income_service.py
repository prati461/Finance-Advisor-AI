from datetime import date
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException
from backend.models.income import Income
from backend.repositories.income_repository import IncomeRepository
from backend.schemas.finance import IncomeCreate, IncomeUpdate


class IncomeService:
    def __init__(self, db: Session) -> None:
        self.repository = IncomeRepository(db)

    def get_income(self, user_id: int, income_id: int) -> Income:
        income = self.repository.get(user_id, income_id)
        if not income:
            raise NotFoundException("Income record not found")
        return income

    def list_incomes(
        self,
        user_id: int,
        skip: int,
        limit: int,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, list[Income]]:
        return self.repository.list(user_id, skip=skip, limit=limit, category=category, start_date=start_date, end_date=end_date, search=search)

    def create_income(self, user_id: int, payload: IncomeCreate) -> Income:
        income = Income(user_id=user_id, **payload.model_dump())
        return self.repository.create(income)

    def update_income(self, user_id: int, income_id: int, payload: IncomeUpdate) -> Income:
        income = self.get_income(user_id, income_id)
        return self.repository.update(income, payload.model_dump(exclude_none=True))

    def delete_income(self, user_id: int, income_id: int) -> None:
        income = self.get_income(user_id, income_id)
        self.repository.delete(income)

    def compute_total(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
        return self.repository.total_amount(user_id, start_date=start_date, end_date=end_date)
