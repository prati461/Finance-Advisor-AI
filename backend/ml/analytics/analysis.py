"""
Market Analysis Orchestrator

Combines the metrics engine, technical analyzer, and sector analyzer into
a single comprehensive analysis service used by the API layer.
"""

import logging
from typing import Any, Dict, List

from backend.ml.analytics.metrics import analytics_engine
from backend.ml.analytics.sectors import sector_analyzer
from backend.ml.analytics.technical import technical_analyzer
from backend.market.manager import market_data_manager

logger = logging.getLogger(__name__)


class MarketAnalysisService:
    """High-level market analysis service."""

    def full_analysis(self, query: str) -> Dict[str, Any]:
        """Run the complete 5-year + technical analysis for a symbol."""
        fundamental = analytics_engine.analyze(query, period="5y")
        technical = technical_analyzer.analyze(query)

        if not fundamental.get("available"):
            return fundamental

        return {
            **fundamental,
            "technical": technical if technical.get("available") else None,
        }

    def comparison(self, queries: List[str]) -> Dict[str, Any]:
        """Run comparison analysis for multiple assets."""
        results = {}
        for q in queries:
            analysis = analytics_engine.analyze(q, period="5y")
            if analysis.get("available"):
                results[analysis["name"]] = {
                    "cagr": analysis["cagr"],
                    "annual_return": analysis["annual_return"],
                    "volatility": analysis["volatility"],
                    "sharpe_ratio": analysis["sharpe_ratio"],
                    "max_drawdown": analysis["max_drawdown"],
                    "confidence_score": analysis["confidence_score"],
                }
        return {
            "assets": results,
            "chart_data": market_data_manager.get_comparison(queries, period="5y", interval="1mo"),
        }

    def sector_performance(self) -> List[Dict[str, Any]]:
        """Return sector performance data."""
        return sector_analyzer.analyze(period="5y")

    def top_performing(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return top performing stocks."""
        return sector_analyzer.top_performing(period="5y", limit=limit)

    def market_overview(self) -> Dict[str, Any]:
        """Return a summary market overview for the dashboard."""
        assets = ["NIFTY 50", "SENSEX", "BANK NIFTY", "GOLD", "SILVER"]
        overview = []
        for asset in assets:
            analysis = analytics_engine.analyze(asset, period="5y")
            if analysis.get("available"):
                overview.append(
                    {
                        "name": analysis["name"],
                        "symbol": analysis["symbol"],
                        "current_price": analysis["current_price"],
                        "cagr": analysis["cagr"],
                        "volatility": analysis["volatility"],
                        "max_drawdown": analysis["max_drawdown"],
                        "sharpe_ratio": analysis["sharpe_ratio"],
                        "confidence_score": analysis["confidence_score"],
                    }
                )
        return {
            "assets": overview,
            "top_performing": self.top_performing(5),
            "sectors": self.sector_performance(),
        }


# Singleton
market_analysis_service = MarketAnalysisService()
