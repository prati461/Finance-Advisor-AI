"""
Sector Analyzer

Computes sector-level performance by aggregating the individual stock
returns within each sector. Used for sector-performance analysis and
the horizontal bar chart.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List

from backend.market.symbols import MARKET_SYMBOLS
from backend.ml.analytics.metrics import AnalyticsEngine

logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """Aggregates stock performance into sector-level metrics."""

    SECTORS = {
        "Information Technology": ["TCS", "INFY", "WIPRO"],
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
        "Energy": ["RELIANCE"],
        "FMCG": ["ITC", "HINDUNILVR"],
        "Automobile": ["MARUTI", "TATAMOTORS"],
        "Infrastructure": ["LT"],
        "Pharma": ["SUNPHARMA"],
        "Consumer": ["ASIANPAINT"],
        "Cement": ["ULTRACEMCO"],
        "NBFC": ["BAJFINANCE"],
        "Telecom": ["BHARTIARTL"],
    }

    def __init__(self):
        self.engine = AnalyticsEngine()

    def analyze(self, period: str = "5y") -> List[Dict[str, Any]]:
        """Compute performance for each sector."""
        results = []
        for sector, symbols in self.SECTORS.items():
            returns = []
            vols = []
            for sym in symbols:
                df = self.engine.get_history(sym, period)
                if df.empty:
                    continue
                cagr = self.engine.compute_cagr(df)
                vol = self.engine.compute_volatility(df)
                returns.append(cagr)
                vols.append(vol)
            if returns:
                results.append(
                    {
                        "sector": sector,
                        "avg_return": round(sum(returns) / len(returns), 2),
                        "avg_volatility": round(sum(vols) / len(vols), 2),
                        "stocks": symbols,
                    }
                )

        # Sort by return descending
        results.sort(key=lambda r: r["avg_return"], reverse=True)
        return results

    def top_performing(self, period: str = "5y", limit: int = 5) -> List[Dict[str, Any]]:
        """Return the top N performing assets."""
        stocks = [k for k, v in MARKET_SYMBOLS.items() if v["asset_class"] == "stock"]
        scored = []
        for sym in stocks:
            df = self.engine.get_history(sym, period)
            if df.empty:
                continue
            cagr = self.engine.compute_cagr(df)
            vol = self.engine.compute_volatility(df)
            scored.append(
                {
                    "symbol": sym,
                    "name": MARKET_SYMBOLS[sym]["name"],
                    "cagr": round(cagr, 2),
                    "volatility": round(vol, 2),
                }
            )
            # Limit to stocks with valid data
            if len(scored) >= len(stocks) * 2:
                break
        scored.sort(key=lambda r: r["cagr"], reverse=True)
        return scored[:limit]


# Singleton
sector_analyzer = SectorAnalyzer()
