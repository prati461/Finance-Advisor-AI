"""
AI Recommendation Engine

Generates personalized financial recommendations based on user's real data.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.income import Income
from backend.models.expense import Expense
from backend.models.budget import Budget


class RecommendationEngine:
    """Generates personalized financial recommendations."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def generate_recommendations(self) -> Dict:
        """Generate comprehensive personalized recommendations."""
        recommendations = {
            "priority_goals": self._get_priority_goals(),
            "spending_tips": self._get_spending_tips(),
            "savings_tips": self._get_savings_tips(),
            "investment_advice": self._get_investment_advice(),
            "budget_tips": self._get_budget_tips(),
            "emergency_fund": self._get_emergency_fund_advice(),
        }
        return recommendations

    def _get_monthly_income(self) -> float:
        """Get total monthly income."""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1)
        else:
            end_of_month = date(today.year, today.month + 1, 1)

        total = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(
                Income.user_id == self.user_id,
                Income.received_date >= start_of_month,
                Income.received_date < end_of_month,
            )
            .scalar()
        ) or 0
        return total

    def _get_monthly_expense(self) -> float:
        """Get total monthly expense."""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1)
        else:
            end_of_month = date(today.year, today.month + 1, 1)

        total = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= start_of_month,
                Expense.spent_at < end_of_month,
            )
            .scalar()
        ) or 0
        return total

    def _get_top_expense_categories(self, limit: int = 3) -> List[Dict]:
        """Get top expense categories by amount."""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        categories = (
            self.db.query(
                Expense.category,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count"),
            )
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= start_of_month,
            )
            .group_by(Expense.category)
            .order_by(func.sum(Expense.amount).desc())
            .limit(limit)
            .all()
        )

        return [
            {"category": cat, "amount": round(amt, 2), "count": cnt}
            for cat, amt, cnt in categories
        ]

    def _get_priority_goals(self) -> List[Dict]:
        """Generate priority financial goals."""
        income = self._get_monthly_income()
        expense = self._get_monthly_expense()
        savings = income - expense
        savings_ratio = savings / income if income > 0 else 0

        goals = []

        if savings <= 0:
            goals.append({
                "priority": "Critical",
                "goal": "Achieve positive cash flow",
                "action": "Reduce expenses to spend less than you earn",
                "timeline": "1-2 months",
            })

        if savings_ratio < 0.1:
            goals.append({
                "priority": "High",
                "goal": "Build emergency fund",
                "action": f"Save at least 10% of income (₹{income * 0.1:.0f}/month) for emergencies",
                "timeline": "3-6 months",
            })
        elif savings_ratio < 0.2:
            goals.append({
                "priority": "Medium",
                "goal": "Increase savings rate to 20%",
                "action": f"Try to save ₹{income * 0.2 - savings:.0f} more per month",
                "timeline": "6 months",
            })

        if savings_ratio >= 0.2:
            goals.append({
                "priority": "Medium",
                "goal": "Start investing",
                "action": "Allocate 50% of savings towards investments",
                "timeline": "Ongoing",
            })

        if not goals:
            goals.append({
                "priority": "Low",
                "goal": "Optimize tax savings",
                "action": "Explore tax-saving investment options under Section 80C",
                "timeline": "Before financial year end",
            })

        return goals

    def _get_spending_tips(self) -> List[Dict]:
        """Generate personalized spending tips."""
        top_categories = self._get_top_expense_categories()
        tips = []

        for cat_info in top_categories:
            category = cat_info["category"]
            amount = cat_info["amount"]

            if category.lower() in ("food", "entertainment", "shopping"):
                tips.append({
                    "category": category,
                    "current_spend": amount,
                    "tip": f"Consider reducing {category.lower()} expenses. Try setting a daily limit.",
                    "potential_savings": round(amount * 0.2, 2),
                })

        if not tips:
            tips.append({
                "category": "General",
                "current_spend": 0,
                "tip": "Track all expenses for a month to identify spending patterns.",
                "potential_savings": 0,
            })

        return tips

    def _get_savings_tips(self) -> List[Dict]:
        """Generate savings tips."""
        income = self._get_monthly_income()
        expense = self._get_monthly_expense()
        savings = income - expense
        savings_ratio = savings / income if income > 0 else 0

        tips = []

        if savings_ratio < 0.1:
            tips.append({
                "tip": "Start with small savings - save just 5% of your income and gradually increase",
                "impact": "Builds saving habit",
            })
            tips.append({
                "tip": "Automate your savings by setting up an auto-transfer on payday",
                "impact": "Consistent savings",
            })
        elif savings_ratio < 0.2:
            tips.append({
                "tip": f"Try to save ₹{income * 0.2 - savings:.0f} more each month",
                "impact": "Reach 20% savings rate",
            })
            tips.append({
                "tip": "Consider a 'no-spend' weekend once a month",
                "impact": "Extra savings",
            })
        else:
            tips.append({
                "tip": "Great savings rate! Consider investing your surplus savings",
                "impact": "Wealth creation",
            })

        return tips

    def _get_investment_advice(self) -> List[Dict]:
        """Generate investment advice."""
        income = self._get_monthly_income()
        expense = self._get_monthly_expense()
        savings = income - expense
        savings_ratio = savings / income if income > 0 else 0

        advice = []

        if savings_ratio < 0.1:
            advice.append({
                "advice": "Focus on building an emergency fund before investing",
                "type": "Readiness",
                "action": "Save 3-6 months of expenses in a high-yield savings account",
            })
        elif savings_ratio < 0.2:
            advice.append({
                "advice": "Start with low-risk investments like debt mutual funds or PPF",
                "type": "Beginner",
                "action": f"Start with ₹{savings * 0.3:.0f}/month in a balanced mutual fund",
            })
        else:
            advice.append({
                "advice": "Consider a diversified portfolio with equity mutual funds",
                "type": "Growth",
                "action": f"Invest ₹{savings * 0.6:.0f}/month in equity funds",
            })

        return advice

    def _get_budget_tips(self) -> List[Dict]:
        """Generate budget optimization tips."""
        today = date.today()
        budgets = (
            self.db.query(Budget)
            .filter(
                Budget.user_id == self.user_id,
                Budget.month == today.month,
                Budget.year == today.year,
            )
            .all()
        )

        tips = []

        for budget in budgets:
            spent = (
                self.db.query(func.coalesce(func.sum(Expense.amount), 0))
                .filter(
                    Expense.user_id == self.user_id,
                    Expense.category == budget.category,
                    Expense.spent_at >= date(today.year, today.month, 1),
                )
                .scalar()
            ) or 0

            if spent > budget.budget_amount:
                tips.append({
                    "category": budget.category,
                    "budget": budget.budget_amount,
                    "spent": round(spent, 2),
                    "tip": f"You've exceeded your {budget.category} budget by ₹{spent - budget.budget_amount:.0f}",
                    "over_budget": True,
                })
            elif spent > budget.budget_amount * 0.8:
                tips.append({
                    "category": budget.category,
                    "budget": budget.budget_amount,
                    "spent": round(spent, 2),
                    "tip": f"You're close to your {budget.category} budget limit",
                    "over_budget": False,
                })

        if not tips:
            income = self._get_monthly_income()
            tips.append({
                "category": "General",
                "budget": 0,
                "spent": 0,
                "tip": f"Consider setting budgets for each expense category (50-30-20 rule: 50% needs, 30% wants, 20% savings)",
                "over_budget": False,
            })

        return tips

    def _get_emergency_fund_advice(self) -> Dict:
        """Generate emergency fund advice."""
        monthly_expense = self._get_monthly_expense()
        recommended_fund = monthly_expense * 6

        # Get total savings (income - expenses over last 3 months)
        today = date.today()
        three_months_ago = date(today.year, today.month - 3, 1) if today.month > 3 else date(today.year - 1, today.month + 9, 1)

        total_income_3m = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(
                Income.user_id == self.user_id,
                Income.received_date >= three_months_ago,
            )
            .scalar()
        ) or 0

        total_expense_3m = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= three_months_ago,
            )
            .scalar()
        ) or 0

        current_savings = total_income_3m - total_expense_3m

        return {
            "monthly_expense": monthly_expense,
            "recommended_fund": round(recommended_fund, 2),
            "current_estimate": round(max(current_savings, 0), 2),
            "months_covered": round(current_savings / monthly_expense, 1) if monthly_expense > 0 else 0,
            "status": "Adequate" if current_savings >= recommended_fund else "Needs improvement",
            "advice": (
                "Your emergency fund is adequate!" if current_savings >= recommended_fund
                else f"Build an emergency fund of ₹{recommended_fund:.0f} (6 months of expenses)"
            ),
        }
