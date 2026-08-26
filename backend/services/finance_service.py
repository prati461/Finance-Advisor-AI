from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.budget import Budget
from backend.repositories.budget_repository import BudgetRepository
from backend.repositories.expense_repository import ExpenseRepository
from backend.repositories.income_repository import IncomeRepository


class FinanceService:
    def __init__(self, db: Session) -> None:
        self.income_repo = IncomeRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.budget_repo = BudgetRepository(db)

    def get_monthly_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        income_total = self.income_repo.total_amount(user_id, start_date=start_date, end_date=end_date)
        expense_total = self.expense_repo.total_amount(user_id, start_date=start_date, end_date=end_date)
        summary = {
            "income_total": income_total,
            "expense_total": expense_total,
            "savings_total": income_total - expense_total,
        }
        return summary

    def get_budget_remaining(self, user_id: int, month: int, year: int, category: Optional[str] = None) -> float:
        total_budget = self.budget_repo.get_monthly_budget(user_id, month, year, category)
        total_expense = self.expense_repo.total_amount(user_id, start_date=date(year, month, 1), end_date=self._next_month(year, month))
        return total_budget - total_expense

    @staticmethod
    def _next_month(year: int, month: int) -> date:
        if month == 12:
            return date(year + 1, 1, 1)
        return date(year, month + 1, 1)
