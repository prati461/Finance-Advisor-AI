from datetime import date
from typing import Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from backend.models.income import Income


class IncomeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int, income_id: int) -> Optional[Income]:
        return (
            self.db.query(Income)
            .filter(Income.user_id == user_id, Income.id == income_id)
            .first()
        )

    def list(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, list[Income]]:
        query = self.db.query(Income).filter(Income.user_id == user_id)

        if category:
            query = query.filter(Income.category == category)

        if start_date and end_date:
            query = query.filter(Income.received_date >= start_date, Income.received_date < end_date)

        if search:
            query = query.filter(
                func.lower(Income.source).contains(search.lower())
                | func.lower(Income.description).contains(search.lower())
            )

        total = query.count()
        items = query.order_by(Income.received_date.desc()).offset(skip).limit(limit).all()
        return total, items

    def create(self, income: Income) -> Income:
        self.db.add(income)
        self.db.commit()
        self.db.refresh(income)
        return income

    def update(self, income: Income, changes: dict) -> Income:
        for field, value in changes.items():
            if value is not None:
                setattr(income, field, value)
        self.db.commit()
        self.db.refresh(income)
        return income

    def delete(self, income: Income) -> None:
        self.db.delete(income)
        self.db.commit()

    def total_amount(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
        query = self.db.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(Income.user_id == user_id)
        if start_date and end_date:
            query = query.filter(Income.received_date >= start_date, Income.received_date < end_date)
        return query.scalar() or 0.0
