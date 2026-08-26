from datetime import date
from typing import Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from backend.models.budget import Budget


class BudgetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int, budget_id: int) -> Optional[Budget]:
        return (
            self.db.query(Budget)
            .filter(Budget.user_id == user_id, Budget.id == budget_id)
            .first()
        )

    def list(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Tuple[int, list[Budget]]:
        query = self.db.query(Budget).filter(Budget.user_id == user_id)

        if category:
            query = query.filter(Budget.category == category)

        if month is not None:
            query = query.filter(Budget.month == month)

        if year is not None:
            query = query.filter(Budget.year == year)

        total = query.count()
        items = query.order_by(Budget.year.desc(), Budget.month.desc()).offset(skip).limit(limit).all()
        return total, items

    def create(self, budget: Budget) -> Budget:
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def update(self, budget: Budget, changes: dict) -> Budget:
        for field, value in changes.items():
            if value is not None:
                setattr(budget, field, value)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget: Budget) -> None:
        self.db.delete(budget)
        self.db.commit()

    def get_monthly_budget(self, user_id: int, month: int, year: int, category: Optional[str] = None) -> float:
        query = self.db.query(func.coalesce(func.sum(Budget.budget_amount), 0.0)).filter(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year,
        )

        if category:
            query = query.filter(Budget.category == category)

        return query.scalar() or 0.0
