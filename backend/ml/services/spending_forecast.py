"""
Spending Forecast Service

Predicts next month's income, expenses, and savings using Linear Regression.
Trains on historical data to provide realistic forecasts with confidence scores.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.income import Income
from backend.models.expense import Expense


class SpendingForecast:
    """Forecasts future spending using ML models."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def forecast(self) -> Dict:
        """Generate spending forecast for next month."""
        # Get monthly aggregates for last 6 months
        monthly_data = self._get_monthly_aggregates()

        if len(monthly_data) < 2:
            # Fallback with current data
            return self._fallback_forecast()

        # Prepare data for forecasting
        income_forecast, income_conf = self._forecast_series(
            [d["income"] for d in monthly_data],
            [d["month_num"] for d in monthly_data],
        )
        expense_forecast, expense_conf = self._forecast_series(
            [d["expense"] for d in monthly_data],
            [d["month_num"] for d in monthly_data],
        )

        next_month_income = round(income_forecast, 2)
        next_month_expense = round(expense_forecast, 2)
        expected_savings = round(next_month_income - next_month_expense, 2)
        confidence = round((income_conf + expense_conf) / 2, 2)

        # Generate forecast points for charting
        income_points = []
        expense_points = []
        for d in monthly_data:
            income_points.append({
                "month": d["label"],
                "predicted_value": round(d["income"], 2),
            })
            expense_points.append({
                "month": d["label"],
                "predicted_value": round(d["expense"], 2),
            })

        # Add next month prediction
        next_label = self._get_next_month_label(monthly_data[-1]["label"])
        income_points.append({
            "month": next_label,
            "predicted_value": next_month_income,
        })
        expense_points.append({
            "month": next_label,
            "predicted_value": next_month_expense,
        })

        return {
            "next_month_income": next_month_income,
            "next_month_expense": next_month_expense,
            "expected_savings": expected_savings,
            "confidence_score": confidence,
            "income_forecast": income_points,
            "expense_forecast": expense_points,
        }

    def _get_monthly_aggregates(self) -> List[Dict]:
        """Get monthly income/expense aggregates for last 6 months."""
        today = date.today()
        data = []

        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1

            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)

            income = (
                self.db.query(func.coalesce(func.sum(Income.amount), 0))
                .filter(
                    Income.user_id == self.user_id,
                    Income.received_date >= start_date,
                    Income.received_date < end_date,
                )
                .scalar()
            ) or 0

            expense = (
                self.db.query(func.coalesce(func.sum(Expense.amount), 0))
                .filter(
                    Expense.user_id == self.user_id,
                    Expense.spent_at >= start_date,
                    Expense.spent_at < end_date,
                )
                .scalar()
            ) or 0

            from backend.utils.helpers import get_month_short_name
            data.append({
                "month_num": year * 12 + month,
                "label": f"{get_month_short_name(month)} {str(year)[2:]}",
                "income": income,
                "expense": expense,
            })

        return data

    def _forecast_series(self, values: List[float], months: List[int]) -> Tuple[float, float]:
        """Forecast next value using linear regression."""
        X = np.array(months).reshape(-1, 1)
        y = np.array(values)

        model = LinearRegression()
        model.fit(X, y)

        next_month = max(months) + 1
        prediction = model.predict([[next_month]])[0]

        # Calculate confidence based on R^2 score
        y_pred = model.predict(X)
        ss_res = sum((y - y_pred) ** 2)
        ss_tot = sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = round(max(0.5, min(r2, 1.0)), 2)

        return max(0, prediction), confidence

    def _get_next_month_label(self, current_label: str) -> str:
        """Get the label for next month."""
        today = date.today()
        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        from backend.utils.helpers import get_month_short_name
        return f"{get_month_short_name(next_month)} {str(next_year)[2:]}"

    def _fallback_forecast(self) -> Dict:
        """Fallback when not enough data."""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1)
        else:
            end_of_month = date(today.year, today.month + 1, 1)

        income = (
            self.db.query(func.coalesce(func.sum(Income.amount), 0))
            .filter(
                Income.user_id == self.user_id,
                Income.received_date >= start_of_month,
                Income.received_date < end_of_month,
            )
            .scalar()
        ) or 0

        expense = (
            self.db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == self.user_id,
                Expense.spent_at >= start_of_month,
                Expense.spent_at < end_of_month,
            )
            .scalar()
        ) or 0

        from backend.utils.helpers import get_month_short_name
        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        next_label = f"{get_month_short_name(next_month)} {str(next_year)[2:]}"

        return {
            "next_month_income": income,
            "next_month_expense": expense,
            "expected_savings": income - expense,
            "confidence_score": 0.5,
            "income_forecast": [{"month": next_label, "predicted_value": income}],
            "expense_forecast": [{"month": next_label, "predicted_value": expense}],
        }
