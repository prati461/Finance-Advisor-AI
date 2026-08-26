"""
Portfolio Recommendation Service

Recommends a diversified investment portfolio with risk/return analysis
powered by real market data.
"""

import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from backend.ml.services.investment_advisor import InvestmentAdvisor

logger = logging.getLogger(__name__)


class PortfolioRecommender:
    """Recommends diversified investment portfolios."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.advisor = InvestmentAdvisor(db, user_id)

    def recommend(self) -> Dict:
        """Generate a diversified portfolio recommendation from real data."""
        advice = self.advisor.advise()
        allocation = advice["allocation"]
        total_investment = advice["monthly_investment_capacity"]
        market_returns = advice.get("market_returns", {})

        # Risk-level mapping based on asset class
        risk_level_map = {
            "mutual_funds": "Moderate",
            "stocks": "High",
            "gold": "Low",
            "fixed_deposit": "Very Low",
            "debt_funds": "Low",
            "cash": "Very Low",
        }

        portfolio = []
        for asset, pct in allocation.items():
            if pct > 0 and total_investment > 0:
                exp_return = market_returns.get(asset, 8)
                portfolio.append({
                    "name": asset.replace("_", " ").title(),
                    "allocation": pct,
                    "expected_return": round(exp_return, 2),
                    "risk_level": risk_level_map.get(asset, "Moderate"),
                })

        total_return = sum(
            item["allocation"] * item["expected_return"] / 100
            for item in portfolio
        )

        return {
            "total_investment": round(total_investment, 2),
            "risk_level": advice["risk_profile"],
            "expected_annual_return": round(total_return, 2),
            "portfolio": portfolio,
        }
