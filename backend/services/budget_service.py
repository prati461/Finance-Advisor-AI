from typing import Optional, Tuple

from sqlalchemy.orm import Session

from backend.core.exceptions import NotFoundException
from backend.models.budget import Budget
from backend.repositories.budget_repository import BudgetRepository
from backend.schemas.finance import BudgetCreate, BudgetUpdate


class BudgetService:
    def __init__(self, db: Session) -> None:
        self.repository = BudgetRepository(db)

    def get_budget(self, user_id: int, budget_id: int) -> Budget:
        budget = self.repository.get(user_id, budget_id)
        if not budget:
            raise NotFoundException("Budget record not found")
        return budget

    def list_budgets(
        self,
        user_id: int,
        skip: int,
        limit: int,
        category: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Tuple[int, list[Budget]]:
        return self.repository.list(user_id=user_id, skip=skip, limit=limit, category=category, month=month, year=year)

    def create_budget(self, user_id: int, payload: BudgetCreate) -> Budget:
        budget = Budget(user_id=user_id, **payload.model_dump())
        return self.repository.create(budget)

    def update_budget(self, user_id: int, budget_id: int, payload: BudgetUpdate) -> Budget:
        budget = self.get_budget(user_id, budget_id)
        return self.repository.update(budget, payload.model_dump(exclude_none=True))

    def delete_budget(self, user_id: int, budget_id: int) -> None:
        budget = self.get_budget(user_id, budget_id)
        self.repository.delete(budget)

    def calculate_budget_amount(self, user_id: int, month: int, year: int, category: Optional[str] = None) -> float:
        return self.repository.get_monthly_budget(user_id, month, year, category)
