from datetime import date
from typing import Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from backend.models.expense import Expense


class ExpenseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int, expense_id: int) -> Optional[Expense]:
        return (
            self.db.query(Expense)
            .filter(Expense.user_id == user_id, Expense.id == expense_id)
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
    ) -> Tuple[int, list[Expense]]:
        query = self.db.query(Expense).filter(Expense.user_id == user_id)

        if category:
            query = query.filter(Expense.category == category)

        if start_date and end_date:
            query = query.filter(Expense.spent_at >= start_date, Expense.spent_at < end_date)

        if search:
            query = query.filter(
                func.lower(Expense.description).contains(search.lower())
                | func.lower(Expense.merchant).contains(search.lower())
            )

        total = query.count()
        items = query.order_by(Expense.spent_at.desc()).offset(skip).limit(limit).all()
        return total, items

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def update(self, expense: Expense, changes: dict) -> Expense:
        for field, value in changes.items():
            if value is not None:
                setattr(expense, field, value)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete(self, expense: Expense) -> None:
        self.db.delete(expense)
        self.db.commit()

    def total_amount(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
        query = self.db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(Expense.user_id == user_id)
        if start_date and end_date:
            query = query.filter(Expense.spent_at >= start_date, Expense.spent_at < end_date)
        return query.scalar() or 0.0
