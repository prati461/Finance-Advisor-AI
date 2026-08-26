"""
Wealth Projection Service

Projects future wealth based on:
- Monthly SIP amount
- Investment duration (years)
- Expected CAGR (from real market data or user-provided)
- Inflation rate

Uses Monte Carlo simulation for realistic projections with confidence bands.
"""

import logging
import math
from typing import Any, Dict, List

import numpy as np

from backend.ml.analytics.metrics import analytics_engine

logger = logging.getLogger(__name__)

DEFAULT_INFLATION = 6.0  # %
DEFAULT_INTEREST_ON_DEBT = 9.0  # %


class WealthProjector:
    """Projects future wealth using SIP compounding and Monte Carlo simulation."""

    def __init__(self):
        self.engine = analytics_engine

    def project(
        self,
        monthly_sip: float,
        years: int,
        expected_return: float,
        current_amount: float = 0.0,
        inflation_rate: float = DEFAULT_INFLATION,
        simulations: int = 500,
    ) -> Dict[str, Any]:
        """
        Project future wealth from a monthly SIP.

        Args:
            monthly_sip: Monthly systematic investment amount (₹)
            years: Investment duration in years
            expected_return: Expected annual return (%)
            current_amount: Current invested amount (₹)
            inflation_rate: Annual inflation rate (%)
            simulations: Number of Monte Carlo simulations

        Returns:
            Dict with future_value_chart, summary, and statistics.
        """
        monthly_rate = (1 + expected_return / 100) ** (1 / 12) - 1
        months = years * 12

        # Deterministic projection
        timeline = []
        balance = current_amount
        invested = current_amount
        for m in range(0, months + 1):
            if m > 0:
                balance = balance * (1 + monthly_rate) + monthly_sip
                invested += monthly_sip
            timeline.append(
                {
                    "month": m,
                    "year": round(m / 12, 1),
                    "value": round(balance, 2),
                    "invested": round(invested, 2),
                }
            )

        future_value = balance
        total_invested = invested
        total_gain = future_value - total_invested

        # Inflation-adjusted value
        inflation_factor = (1 + inflation_rate / 100) ** years
        inflation_adjusted = future_value / inflation_factor

        # Monte Carlo simulation for confidence bands
        mc_paths = self._monte_carlo(
            monthly_sip, years, expected_return, current_amount, simulations
        )

        # Compute percentile bands
        mc_final = mc_paths[:, -1] if mc_paths.size else np.array([future_value])
        p10 = float(np.percentile(mc_final, 10))
        p50 = float(np.percentile(mc_final, 50))
        p90 = float(np.percentile(mc_final, 90))

        # Build chart with median band
        chart = self._build_band_chart(mc_paths, months)

        return {
            "monthly_sip": round(monthly_sip, 2),
            "years": years,
            "expected_return": expected_return,
            "current_amount": round(current_amount, 2),
            "future_value": round(future_value, 2),
            "total_invested": round(total_invested, 2),
            "total_gain": round(total_gain, 2),
            "inflation_adjusted_value": round(inflation_adjusted, 2),
            "inflation_rate": inflation_rate,
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "timeline": timeline,
            "chart": chart,
        }

    def _monte_carlo(
        self,
        sip: float,
        years: int,
        expected_return: float,
        current: float,
        simulations: int,
    ) -> np.ndarray:
        """Run Monte Carlo simulations with volatile returns."""
        months = years * 12
        mu = expected_return / 100 / 12
        sigma = max((self._estimate_volatility(expected_return) / 100) / math.sqrt(12), 0.005)
        rng = np.random.default_rng(42)
        paths = np.zeros((simulations, months + 1))
        paths[:, 0] = current
        for m in range(1, months + 1):
            shocks = rng.normal(mu, sigma, simulations)
            paths[:, m] = paths[:, m - 1] * (1 + shocks) + sip
        return paths

    def _estimate_volatility(self, expected_return: float) -> float:
        """Estimate volatility from expected return (rough heuristic)."""
        # Use Nifty 50 historical volatility as a reasonable proxy when needed
        df = self.engine.get_history("NIFTY 50", "5y")
        if not df.empty:
            vol = self.engine.compute_volatility(df)
            if vol > 0:
                return vol
        # Fallback heuristic
        return max(15, expected_return * 0.9)

    def _build_band_chart(self, paths: np.ndarray, months: int) -> List[Dict[str, Any]]:
        """Build a chart dataset with median and percentile bands."""
        if paths.size == 0:
            return []
        chart = []
        for m in range(0, months + 1, max(1, months // 24)):
            column = paths[:, m]
            chart.append(
                {
                    "year": round(m / 12, 1),
                    "p10": round(float(np.percentile(column, 10)), 2),
                    "p50": round(float(np.percentile(column, 50)), 2),
                    "p90": round(float(np.percentile(column, 90)), 2),
                }
            )
        return chart


# Singleton
wealth_projector = WealthProjector()
