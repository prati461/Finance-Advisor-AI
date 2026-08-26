"""
Financial Health Engine

Calculates comprehensive financial health score (0-100) using real user data.
Metrics:
- Income Stability
- Expense Ratio
- Savings Ratio
- Budget Utilization
- Investment Readiness
- Overall Financial Health Score
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.income import Income
from backend.models.expense import Expense
from backend.models.budget import Budget


class FinancialHealthEngine:
    """Calculates financial health metrics for a user."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def calculate_income_stability(self) -> Tuple[float, str]:
        """
        Calculate income stability score (0-100).
        Based on income frequency, consistency, and number of sources.
        """
        incomes = (
            self.db.query(Income)
            .filter(Income.user_id == self.user_id)
            .order_by(Income.received_date.desc())
            .limit(12)
            .all()
        )

        if not incomes:
            return 0, "No income records found"

        total_income = sum(i.amount for i in incomes)
        if total_income == 0:
            return 0, "No income recorded"

        # Count unique sources
        unique_sources = len(set(i.source for i in incomes))
        source_score = min(unique_sources * 15, 30)  # Max 30 points for diversification

        # Check frequency - monthly/regular income is more stable
        monthly_count = sum(1 for i in incomes if i.frequency and i.frequency.lower() in ("monthly", "biweekly", "weekly"))
        frequency_score = min((monthly_count / max(len(incomes), 1)) * 30, 30)

        # Check consistency - variance in amounts
        if len(incomes) > 1:
            amounts = [i.amount for i in incomes]
            mean_amount = sum(amounts) / len(amounts)
            if mean_amount > 0:
                variance = sum((a - mean_amount) ** 2 for a in amounts) / len(amounts)
                cv = (variance ** 0.5) / mean_amount  # Coefficient of variation
                consistency_score = max(0, min(40 * (1 - min(cv, 1)), 40))
            else:
                consistency_score = 0
        else:
            consistency_score = 20  # Single income source

        total_score = source_score + frequency_score + consistency_score
        return round(total_score, 1), "Income stability calculated"

    def calculate_expense_ratio(self) -> Tuple[float, str]:
        """
        Calculate expense ratio score (0-100).
        Lower expense-to-income ratio = higher score.
        """
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        total_income = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(
                Income.user_id == self.user_id,
                Income.received_date >= start_of_month,
            )
            .scalar()
        ) or 0

        total_expense = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= start_of_month,
            )
            .scalar()
        ) or 0

        if total_income == 0:
            return 50, "No income data for ratio calculation"  # Neutral score

        ratio = total_expense / total_income

        if ratio <= 0.3:
            score = 100
            label = "Excellent expense management"
        elif ratio <= 0.5:
            score = 80
            label = "Good expense management"
        elif ratio <= 0.7:
            score = 60
            label = "Moderate expense management"
        elif ratio <= 0.9:
            score = 40
            label = "High expense ratio, consider reducing expenses"
        else:
            score = 20
            label = "Critical expense ratio, expenses exceed income"

        return score, label

    def calculate_savings_ratio(self) -> Tuple[float, str]:
        """
        Calculate savings ratio score (0-100).
        Based on income saved over last 3 months.
        """
        today = date.today()
        three_months_ago = date(today.year, today.month - 3, 1) if today.month > 3 else date(today.year - 1, today.month + 9, 1)

        total_income = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(
                Income.user_id == self.user_id,
                Income.received_date >= three_months_ago,
            )
            .scalar()
        ) or 0

        total_expense = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= three_months_ago,
            )
            .scalar()
        ) or 0

        if total_income == 0:
            return 0, "No income data"

        savings = total_income - total_expense
        savings_ratio = savings / total_income if total_income > 0 else 0

        if savings_ratio >= 0.3:
            score = 100
            label = "Excellent savings rate"
        elif savings_ratio >= 0.2:
            score = 80
            label = "Good savings rate"
        elif savings_ratio >= 0.1:
            score = 60
            label = "Moderate savings rate"
        elif savings_ratio >= 0:
            score = 40
            label = "Low savings rate, try to save more"
        else:
            score = 20
            label = "Negative savings, spending exceeds income"

        return score, label

    def calculate_budget_utilization(self) -> Tuple[float, str]:
        """
        Calculate budget utilization score (0-100).
        How well user adheres to budgets.
        """
        today = date.today()
        current_month = today.month
        current_year = today.year

        budgets = (
            self.db.query(Budget)
            .filter(
                Budget.user_id == self.user_id,
                Budget.month == current_month,
                Budget.year == current_year,
            )
            .all()
        )

        if not budgets:
            return 50, "No budgets set for this month"

        total_score = 0
        total_weight = 0

        for budget in budgets:
            category_expense = (
                self.db.query(func.coalesce(func.sum(Expense.amount), 0))
                .filter(
                    Expense.user_id == self.user_id,
                    Expense.category == budget.category,
                    Expense.spent_at >= date(current_year, current_month, 1),
                )
                .scalar()
            ) or 0

            if budget.budget_amount > 0:
                utilization = category_expense / budget.budget_amount
                if utilization <= 0.8:
                    category_score = 100
                elif utilization <= 1.0:
                    category_score = 70
                elif utilization <= 1.2:
                    category_score = 40
                else:
                    category_score = 20

                total_score += category_score * budget.budget_amount
                total_weight += budget.budget_amount

        if total_weight == 0:
            return 50, "No budget data"

        avg_score = total_score / total_weight
        label = "Good budget adherence" if avg_score >= 70 else "Budget improvement needed"
        return round(avg_score, 1), label

    def calculate_investment_readiness(self) -> Tuple[float, str]:
        """
        Calculate investment readiness score (0-100).
        Based on savings, income stability, and expense management.
        """
        income_stability, _ = self.calculate_income_stability()
        savings_ratio, _ = self.calculate_savings_ratio()
        expense_ratio, _ = self.calculate_expense_ratio()

        # Savings ratio is most important
        score = (income_stability * 0.3) + (savings_ratio * 0.5) + (expense_ratio * 0.2)

        if score >= 80:
            label = "Ready for investment"
        elif score >= 60:
            label = "Almost ready, build more savings"
        elif score >= 40:
            label = "Need to improve savings first"
        else:
            label = "Focus on reducing expenses and building emergency fund"

        return round(score, 1), label

    def calculate_overall_health_score(self) -> Dict:
        """
        Calculate overall financial health score (0-100).
        Returns comprehensive breakdown.
        """
        income_stability, income_note = self.calculate_income_stability()
        expense_ratio, expense_note = self.calculate_expense_ratio()
        savings_ratio, savings_note = self.calculate_savings_ratio()
        budget_util, budget_note = self.calculate_budget_utilization()
        investment_readiness, investment_note = self.calculate_investment_readiness()

        # Weighted average
        overall_score = (
            income_stability * 0.20 +
            expense_ratio * 0.25 +
            savings_ratio * 0.30 +
            budget_util * 0.15 +
            investment_readiness * 0.10
        )

        overall_score = round(overall_score, 1)

        # Determine category
        if overall_score >= 80:
            category = "Excellent"
            color = "#10b981"  # Green
            summary = "Your financial health is excellent! Keep up the good work."
        elif overall_score >= 60:
            category = "Good"
            color = "#3b82f6"  # Blue
            summary = "Your financial health is good. There's room for improvement."
        elif overall_score >= 40:
            category = "Fair"
            color = "#f59e0b"  # Yellow
            summary = "Your financial health needs attention. Consider reviewing your spending habits."
        else:
            category = "Critical"
            color = "#ef4444"  # Red
            summary = "Your financial health needs immediate attention. Please review your finances."

        suggestions = self._generate_suggestions(
            income_stability, expense_ratio, savings_ratio,
            budget_util, investment_readiness
        )

        return {
            "overall_score": overall_score,
            "category": category,
            "color": color,
            "summary": summary,
            "components": {
                "income_stability": {"score": income_stability, "note": income_note},
                "expense_ratio": {"score": expense_ratio, "note": expense_note},
                "savings_ratio": {"score": savings_ratio, "note": savings_note},
                "budget_utilization": {"score": budget_util, "note": budget_note},
                "investment_readiness": {"score": investment_readiness, "note": investment_note},
            },
            "suggestions": suggestions,
        }

    def _generate_suggestions(self, income_stability, expense_ratio, savings_ratio, budget_util, investment_readiness) -> List[str]:
        """Generate actionable suggestions based on scores."""
        suggestions = []

        if income_stability < 60:
            suggestions.append("Consider diversifying your income sources for better stability.")
        if expense_ratio < 60:
            suggestions.append("Your expense ratio is high. Try to reduce non-essential spending.")
        if savings_ratio < 60:
            suggestions.append("Aim to save at least 20% of your income. Consider automating savings.")
        if budget_util < 60:
            suggestions.append("Set and follow a monthly budget to track your spending better.")
        if investment_readiness < 60:
            suggestions.append("Build an emergency fund of 3-6 months of expenses before investing.")
        if expense_ratio < 40:
            suggestions.append("Your expenses are critically high. Review and cut down unnecessary costs.")
        if savings_ratio >= 70 and investment_readiness >= 70:
            suggestions.append("You're ready to invest! Consider starting with mutual funds or index funds.")
        if budget_util >= 80:
            suggestions.append("Great job sticking to your budget! Consider increasing savings or investments.")

        if not suggestions:
            suggestions.append("Excellent financial management! Keep monitoring your finances regularly.")

        return suggestions
