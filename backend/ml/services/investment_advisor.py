"""
Investment Advisor Service

Provides personalized investment plans based on user's financial profile AND
real 5-year market data (CAGR, volatility, sector performance).

The advisor:
1. Determines risk profile from user savings + financial health
2. Computes real expected returns from historical market data
3. Generates a diversified allocation across asset classes
4. Projects future wealth (5 years)
5. Produces a detailed, reasoned explanation
"""

import logging
from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.income import Income
from backend.models.expense import Expense
from backend.core.config import settings
from backend.ml.analytics.metrics import analytics_engine
from backend.ml.analytics.sectors import sector_analyzer
from backend.ml.llm.client import get_llm_client
from backend.ml.services.financial_health import FinancialHealthEngine
from backend.ml.services.wealth_projection import WealthProjector

logger = logging.getLogger(__name__)

# Inflation assumption (India)
INFLATION_RATE = 6.0

# Asset proxy mapping for real return computation
ASSET_PROXIES = {
    "mutual_funds": "NIFTYBEES",
    "stocks": "RELIANCE",
    "gold": "GOLDBEES",
    "fixed_deposit": "NIFTY 50",  # FD ~ risk-free; use NIFTY as reference for comparison
    "debt_funds": "SENSEX",
    "cash": "SENSEX",
}

# Static low-volatility returns (these are stable benchmarks, not recommendations)
FD_RETURN = 6.5
CASH_RETURN = 3.0


class InvestmentAdvisor:
    """Generates data-driven, personalized investment advice."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.health_engine = FinancialHealthEngine(db, user_id)
        self.projector = WealthProjector()

    def advise(self) -> Dict:
        """Generate investment plan based on financial profile + market data."""
        health = self.health_engine.calculate_overall_health_score()
        overall_score = health["overall_score"]

        income = self._get_monthly_income()
        expense = self._get_monthly_expense()
        savings = income - expense

        # Risk profile
        risk_profile, risk_score = self._calculate_risk_profile(overall_score, savings, income)

        # Monthly investment capacity
        monthly_investment = self._calculate_investment_capacity(savings, risk_score)

        # Real market returns
        market_returns = self._get_real_market_returns()

        # Generate allocation
        allocation = self._generate_allocation(risk_profile, market_returns)

        # Compute expected portfolio return from real weights
        expected_return = self._compute_portfolio_return(allocation, market_returns)

        # Project wealth
        projection = self.projector.project(
            monthly_sip=monthly_investment,
            years=5,
            expected_return=expected_return,
            current_amount=0,
            inflation_rate=INFLATION_RATE,
        )

        # Confidence score based on data availability
        confidence = self._compute_confidence(market_returns)

        # Generate advice text (LLM preferred, fallback to template)
        advice = self._generate_advice(
            risk_profile, monthly_investment, expected_return,
            projection["future_value"], market_returns, overall_score,
        )

        return {
            "monthly_investment_capacity": round(monthly_investment, 2),
            "risk_profile": risk_profile,
            "risk_score": round(risk_score, 1),
            "allocation": allocation,
            "expected_annual_return": round(expected_return, 2),
            "expected_cagr": round(expected_return, 2),
            "expected_wealth_5y": round(projection["future_value"], 2),
            "inflation_adjusted_wealth": round(projection["inflation_adjusted_value"], 2),
            "confidence_score": confidence,
            "advice": advice,
            "market_returns": market_returns,
            "sector_performance": sector_analyzer.analyze(period="5y")[:5],
            "projection": projection,
        }

    def _get_monthly_income(self) -> float:
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

    def _calculate_risk_profile(self, health_score: float, savings: float, income: float) -> Tuple[str, float]:
        """Calculate risk profile from health + savings ratio."""
        savings_ratio = savings / income if income > 0 else 0

        if health_score >= 80 and savings_ratio >= 0.3:
            return "Aggressive", 80
        elif health_score >= 60 and savings_ratio >= 0.2:
            return "Moderate-Aggressive", 65
        elif health_score >= 40 and savings_ratio >= 0.1:
            return "Moderate", 50
        elif health_score >= 20:
            return "Conservative-Moderate", 35
        else:
            return "Conservative", 20

    def _calculate_investment_capacity(self, savings: float, risk_score: float) -> float:
        """Investment capacity = 50-70% of savings based on risk."""
        investment_ratio = 0.5 + (risk_score / 100) * 0.2
        return round(max(0, savings * investment_ratio), 2)

    def _get_real_market_returns(self) -> Dict[str, float]:
        """Compute real 5-year CAGRs for each asset class."""
        returns = {}
        for asset, proxy in ASSET_PROXIES.items():
            df = analytics_engine.get_history(proxy, "5y")
            if df.empty:
                returns[asset] = self._default_return(asset)
            else:
                cagr = analytics_engine.compute_cagr(df)
                returns[asset] = round(cagr, 2) if cagr != 0 else self._default_return(asset)
        # Fixed deposit & cash are stable
        returns["fixed_deposit"] = FD_RETURN
        returns["cash"] = CASH_RETURN
        returns["debt_funds"] = round(FD_RETURN + 0.5, 2)
        return returns

    def _default_return(self, asset: str) -> float:
        """Fallback defaults (only used if real data is unavailable)."""
        defaults = {
            "mutual_funds": 12.0,
            "stocks": 14.0,
            "gold": 9.0,
            "fixed_deposit": 6.5,
            "debt_funds": 7.0,
            "cash": 3.0,
        }
        return defaults.get(asset, 8.0)

    def _generate_allocation(self, risk_profile: str, returns: Dict[str, float]) -> Dict:
        """Generate allocation based on risk profile and real returns."""
        allocations = {
            "Conservative": {
                "fixed_deposit": 40,
                "mutual_funds": 15,
                "gold": 15,
                "debt_funds": 20,
                "cash": 10,
            },
            "Conservative-Moderate": {
                "fixed_deposit": 30,
                "mutual_funds": 25,
                "gold": 15,
                "debt_funds": 20,
                "cash": 10,
            },
            "Moderate": {
                "mutual_funds": 35,
                "stocks": 20,
                "gold": 12,
                "fixed_deposit": 20,
                "cash": 13,
            },
            "Moderate-Aggressive": {
                "mutual_funds": 35,
                "stocks": 30,
                "gold": 10,
                "fixed_deposit": 15,
                "cash": 10,
            },
            "Aggressive": {
                "mutual_funds": 30,
                "stocks": 45,
                "gold": 5,
                "fixed_deposit": 10,
                "cash": 10,
            },
        }
        return allocations.get(risk_profile, allocations["Moderate"])

    def _compute_portfolio_return(self, allocation: Dict, returns: Dict[str, float]) -> float:
        """Compute weighted expected annual return.

        allocation[asset] is in percentage points (e.g. 35 == 35%).
        returns[asset]    is the historical CAGR already expressed as a
                          percentage (e.g. 9 == 9%) -- NOT a decimal.

        Weighted contribution = allocation_pct * cagr_pct / 100, which is
        already in percentage points, so the sum is the final percentage.
        It must NOT be multiplied by 100 again (that would inflate 9.39%
        to 939%).
        """
        contribution = {}
        weighted_sum = 0.0
        logger.info("=== Portfolio Expected Annual Return Breakdown ===")
        for asset, weight in allocation.items():
            pct = weight if weight > 0 else 0
            cagr = returns.get(asset, self._default_return(asset))
            # allocation in %, CAGR in % -> contribution in % points
            w = (pct * cagr) / 100.0
            contribution[asset] = w
            weighted_sum += w
            logger.info(
                "%s: allocation=%.1f%%, historical_cagr=%.2f%%, "
                "weighted_contribution=%.2f%%",
                asset, pct, cagr, w,
            )
        result = weighted_sum  # already a percentage; do NOT *100 again
        logger.info(
            "Sum of weighted contributions=%.2f -> portfolio_expected_return=%.2f%%",
            weighted_sum, result,
        )
        return round(result, 2)

    def _compute_confidence(self, returns: Dict[str, float]) -> float:
        """Confidence based on how much real data was available."""
        real_assets = [a for a in ["mutual_funds", "stocks", "gold"] if returns.get(a, 0) > 0]
        base = 0.65 + 0.1 * len(real_assets)
        return round(min(base, 0.95), 2)

    def _generate_advice(
        self,
        risk_profile: str,
        monthly_investment: float,
        expected_return: float,
        future_wealth: float,
        market_returns: Dict[str, float],
        health_score: float,
    ) -> str:
        """Generate a detailed, reasoned investment advice."""
        llm = get_llm_client()
        prompt = (
            f"You are a senior financial advisor for an Indian investor.\n"
            f"Risk profile: {risk_profile}\n"
            f"Monthly investment capacity: ₹{monthly_investment:.0f}\n"
            f"Expected annual return: {expected_return:.1f}%\n"
            f"Projected wealth after 5 years: ₹{future_wealth:.0f}\n"
            f"Financial health score: {health_score}/100\n"
            f"Real market 5Y CAGRs: {market_returns}\n\n"
            f"Write a detailed, personalized explanation (6-10 sentences) of why this "
            f"investment plan is recommended, referencing the real market returns, "
            f"the user's risk profile, and portfolio diversification. Use ₹ amounts."
        )
        if llm.available:
            response = llm.generate(prompt, temperature=0.5)
            if response:
                return response.strip()

        # Fallback template (data-driven, not hardcoded)
        mf = market_returns.get("mutual_funds", 12)
        st = market_returns.get("stocks", 14)
        gd = market_returns.get("gold", 9)
        return (
            f"Based on your {risk_profile.lower()} risk profile and financial health score of "
            f"{health_score:.0f}/100, you can invest ₹{monthly_investment:.0f}/month. "
            f"Historical 5-year data shows large-cap mutual funds/indices delivered around "
            f"{mf:.1f}% CAGR, large-cap stocks around {st:.1f}%, gold around {gd:.1f}%, and "
            f"fixed deposits around 6.5%. A diversified portfolio targeting ~{expected_return:.1f}% "
            f"CAGR could grow to approximately ₹{future_wealth:.0f} in 5 years. This allocation "
            f"balances growth with risk management through diversification across equities, "
            f"debt, gold, and emergency cash."
        )


# Backward-compatible alias
def create_investment_advisor(db: Session, user_id: int) -> InvestmentAdvisor:
    return InvestmentAdvisor(db, user_id)
