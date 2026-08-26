"""
Market Data Provider Interface

Abstract base class that all market data providers must implement.
Ensures a consistent API for historical data, quotes, and fundamentals.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    name: str = "base"

    @abstractmethod
    def get_history(
        self,
        symbol: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLCV data for a symbol.

        Args:
            symbol: Ticker symbol (e.g., "^NSEI", "RELIANCE.NS")
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
            interval: Bar interval (1m, 5m, 1h, 1d, 1wk, 1mo)

        Returns:
            List of dicts with keys: date, open, high, low, close, volume
        """
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch a real-time quote for a symbol.

        Returns dict with: symbol, name, price, previous_close, open, day_high,
        day_low, volume, change, change_percent, market_cap, pe_ratio,
        dividend_yield, fifty_two_week_high, fifty_two_week_low, currency
        """
        raise NotImplementedError

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Fetch fundamental data (PE, dividend yield, market cap, etc.)."""
        return {}

    def is_available(self) -> bool:
        """Return whether this provider can fetch live data right now."""
        return True
