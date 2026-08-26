"""
Budget Optimizer

Analyzes spending patterns and suggests optimized budget allocations.
Uses historical expense data to recommend realistic budget adjustments.
"""

from datetime import date
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.expense import Expense
from backend.models.budget import Budget


class BudgetOptimizer:
    """Optimizes budget allocations based on spending patterns."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def optimize(self) -> Dict:
        """Analyze spending and suggest optimized budgets."""
        today = date.today()
        current_month = today.month
        current_year = today.year

        # Get current budgets
        current_budgets = (
            self.db.query(Budget)
            .filter(
                Budget.user_id == self.user_id,
                Budget.month == current_month,
                Budget.year == current_year,
            )
            .all()
        )

        # Get average monthly spending by category (last 3 months)
        optimizations = []
        total_current = 0
        total_recommended = 0

        for budget in current_budgets:
            # Get average monthly spend for this category
            avg_spend = self._get_average_category_spend(budget.category)
            current_amount = budget.budget_amount
            total_current += current_amount

            # Recommended: use average spend + 10% buffer, but not more than current
            recommended = min(round(avg_spend * 1.1, 2), current_amount)
            total_recommended += recommended

            # Generate reason
            if recommended < current_amount:
                reason = f"Average spending in {budget.category} is ₹{avg_spend:.0f}. Reducing budget by ₹{current_amount - recommended:.0f}."
            else:
                reason = f"Current budget matches spending patterns in {budget.category}."

            optimizations.append({
                "category": budget.category,
                "current_amount": current_amount,
                "recommended_amount": recommended,
                "difference": round(current_amount - recommended, 2),
                "reason": reason,
            })

        # If no budgets set, suggest based on common categories
        if not current_budgets:
            categories = self._get_recent_categories()
            for cat in categories:
                avg_spend = self._get_average_category_spend(cat)
                if avg_spend > 0:
                    recommended = round(avg_spend * 1.1, 2)
                    total_recommended += recommended
                    optimizations.append({
                        "category": cat,
                        "current_amount": 0,
                        "recommended_amount": recommended,
                        "difference": 0,
                        "reason": f"Suggested budget for {cat} based on average spending of ₹{avg_spend:.0f}.",
                    })

        return {
            "optimizations": optimizations,
            "total_current": total_current,
            "total_recommended": total_recommended,
            "potential_savings": round(total_current - total_recommended, 2),
        }

    def _get_average_category_spend(self, category: str) -> float:
        """Get average monthly spend for a category over last 3 months."""
        today = date.today()
        three_months_ago = date(today.year, today.month - 3, 1) if today.month > 3 else date(today.year - 1, today.month + 9, 1)

        total = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.category == category,
                Expense.spent_at >= three_months_ago,
            )
            .scalar()
        ) or 0

        return total / 3.0

    def _get_recent_categories(self) -> List[str]:
        """Get categories the user has spent on recently."""
        today = date.today()
        three_months_ago = date(today.year, today.month - 3, 1) if today.month > 3 else date(today.year - 1, today.month + 9, 1)

        categories = (
            self.db.query(Expense.category)
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= three_months_ago,
            )
            .distinct()
            .all()
        )

        return [cat[0] for cat in categories]
