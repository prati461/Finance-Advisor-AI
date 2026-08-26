"""
Analytics Engine

Computes comprehensive financial metrics from historical market data:
- CAGR (Compound Annual Growth Rate)
- Annual Return
- Maximum Drawdown
- Volatility
- Sharpe Ratio
- Beta
- Correlation
- AI Confidence Score

All metrics are computed from real historical price data.
"""

import logging
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.market.manager import market_data_manager

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Computes financial metrics from historical market data."""

    def __init__(self):
        self.risk_free_rate = 0.065  # ~6.5% (Indian 10-year G-sec proxy)

    def get_history(self, query: str, period: str = "5y") -> pd.DataFrame:
        """Fetch historical data as a DataFrame."""
        return market_data_manager.get_history_df(query, period=period)

    def compute_cagr(self, df: pd.DataFrame) -> float:
        """Compute Compound Annual Growth Rate."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        if len(series) < 2:
            return 0.0
        start = float(series.iloc[0])
        end = float(series.iloc[-1])
        if start <= 0:
            return 0.0
        years = max((df.index[-1] - df.index[0]).days / 365.25, 1 / 365.25)
        return ((end / start) ** (1 / years) - 1) * 100

    def compute_annual_return(self, df: pd.DataFrame) -> float:
        """Compute average annual return (arithmetic)."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        if len(series) < 2:
            return 0.0
        returns = series.pct_change().dropna()
        if returns.empty:
            return 0.0
        return float(returns.mean() * 252 * 100)

    def compute_max_drawdown(self, df: pd.DataFrame) -> float:
        """Compute maximum drawdown (as a positive percentage)."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        if len(series) < 2:
            return 0.0
        rolling_max = series.cummax()
        drawdown = (series - rolling_max) / rolling_max
        return float(abs(drawdown.min()) * 100)

    def compute_volatility(self, df: pd.DataFrame) -> float:
        """Compute annualized volatility (standard deviation of returns)."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        returns = series.pct_change().dropna()
        if returns.empty:
            return 0.0
        return float(returns.std() * math.sqrt(252) * 100)

    def compute_sharpe(self, df: pd.DataFrame) -> float:
        """Compute Sharpe ratio."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        returns = series.pct_change().dropna()
        if returns.empty:
            return 0.0
        excess = returns - self.risk_free_rate / 252
        std = returns.std()
        if std == 0:
            return 0.0
        return float((excess.mean() / std) * math.sqrt(252))

    def compute_beta(self, df: pd.DataFrame, benchmark: str = "NIFTY 50") -> float:
        """Compute beta vs a benchmark index."""
        asset = df["close"].pct_change().dropna() if not df.empty else pd.Series(dtype=float)
        bench = self.get_history(benchmark, "5y")
        if bench.empty or "close" not in bench.columns:
            return 1.0
        bench_returns = bench["close"].pct_change().dropna()
        # Align indices
        common = pd.concat([asset, bench_returns], axis=1, join="inner").dropna()
        if len(common) < 2:
            return 1.0
        cov = common.iloc[:, 0].cov(common.iloc[:, 1])
        var = common.iloc[:, 1].var()
        if var == 0:
            return 1.0
        return round(float(cov / var), 2)

    def compute_correlation(
        self, query_a: str, query_b: str, period: str = "5y"
    ) -> float:
        """Compute correlation between two assets."""
        df_a = self.get_history(query_a, period)
        df_b = self.get_history(query_b, period)
        if df_a.empty or df_b.empty:
            return 0.0
        ra = df_a["close"].pct_change().dropna()
        rb = df_b["close"].pct_change().dropna()
        common = pd.concat([ra, rb], axis=1, join="inner").dropna()
        if len(common) < 2:
            return 0.0
        return round(float(common.iloc[:, 0].corr(common.iloc[:, 1])), 3)

    def compute_confidence_score(self, df: pd.DataFrame) -> float:
        """Compute an AI confidence score (0-1) based on data quality & consistency."""
        if df.empty or "close" not in df.columns:
            return 0.0
        series = df["close"].dropna()
        n = len(series)
        if n < 30:  # Less than ~1.5 months of data
            return max(0.3, n / 250)
        # More data -> higher confidence, capped
        data_score = min(n / 1500, 1.0)
        # Volatility penalizes confidence slightly
        vol = self.compute_volatility(df)
        vol_score = max(0, 1 - (vol - 15) / 80)
        # Combine
        return round(min(data_score * 0.6 + vol_score * 0.4, 0.98), 2)

    def analyze(self, query: str, period: str = "5y") -> Dict[str, Any]:
        """Run the full 5-year analysis for a symbol."""
        df = self.get_history(query, period)
        if df.empty:
            return {
                "symbol": query,
                "available": False,
                "message": "No historical data available",
            }

        info = market_data_manager.resolve(query)
        quote = market_data_manager.get_quote(query)

        # Compute year-by-year returns
        yearly_returns = self._compute_yearly_returns(df)

        return {
            "symbol": info["symbol"],
            "name": info["name"],
            "asset_class": info["asset_class"],
            "available": True,
            "current_price": round(float(df["close"].iloc[-1]), 2),
            "cagr": round(self.compute_cagr(df), 2),
            "annual_return": round(self.compute_annual_return(df), 2),
            "max_drawdown": round(self.compute_max_drawdown(df), 2),
            "volatility": round(self.compute_volatility(df), 2),
            "sharpe_ratio": round(self.compute_sharpe(df), 2),
            "beta": self.compute_beta(df),
            "pe_ratio": quote.get("pe_ratio"),
            "dividend_yield": quote.get("dividend_yield"),
            "market_cap": quote.get("market_cap"),
            "fifty_two_week_high": quote.get("fifty_two_week_high"),
            "fifty_two_week_low": quote.get("fifty_two_week_low"),
            "confidence_score": self.compute_confidence_score(df),
            "yearly_returns": yearly_returns,
            "data_points": int(len(df)),
            "start_date": df.index[0].strftime("%Y-%m-%d"),
            "end_date": df.index[-1].strftime("%Y-%m-%d"),
        }

    def _compute_yearly_returns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Compute returns for each calendar year."""
        if df.empty or "close" not in df.columns:
            return []
        series = df["close"]
        years = sorted(set(series.index.year))
        result = []
        for year in years:
            year_series = series[series.index.year == year]
            if len(year_series) < 2:
                continue
            start = float(year_series.iloc[0])
            end = float(year_series.iloc[-1])
            if start <= 0:
                continue
            result.append(
                {"year": int(year), "return": round((end / start - 1) * 100, 2)}
            )
        return result

    def get_asset_returns(self, queries: List[str], period: str = "5y") -> Dict[str, float]:
        """Compute CAGR for a list of assets (used by investment advisor)."""
        result = {}
        for q in queries:
            df = self.get_history(q, period)
            if df.empty:
                result[q] = 0.0
            else:
                result[q] = round(self.compute_cagr(df), 2)
        return result


# Singleton
analytics_engine = AnalyticsEngine()
