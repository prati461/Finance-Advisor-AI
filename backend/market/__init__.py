"""Market data package for fetching real historical financial data."""

from backend.market.manager import MarketDataManager
from backend.market.symbols import MARKET_SYMBOLS, INDIAN_STOCKS

__all__ = ["MarketDataManager", "MARKET_SYMBOLS", "INDIAN_STOCKS"]
