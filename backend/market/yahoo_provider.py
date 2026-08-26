"""
Yahoo Finance Market Data Provider

Primary provider using the `yfinance` library (free, no API key required).
Fetches real historical OHLCV data and quotes for indices, stocks,
commodities, ETFs, and mutual-fund proxies.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.market.base import MarketDataProvider
from backend.market.cache import market_cache

logger = logging.getLogger(__name__)


class YahooFinanceProvider(MarketDataProvider):
    """Market data provider backed by Yahoo Finance via `yfinance`."""

    name = "yahoo"

    def is_available(self) -> bool:
        try:
            import yfinance  # noqa: F401

            return True
        except Exception:
            return False

    def _get_ticker(self, symbol: str):
        """Lazily import and return a yfinance Ticker object."""
        import yfinance as yf

        return yf.Ticker(symbol)

    def get_history(
        self,
        symbol: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Fetch historical OHLCV data with caching."""
        cache_key = f"yahoo:history:{symbol}:{period}:{interval}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = self._get_ticker(symbol)
            df = ticker.history(period=period, interval=interval, auto_adjust=True)
            if df is None or df.empty:
                logger.warning("No history returned for %s", symbol)
                return []

            records = []
            for idx, row in df.iterrows():
                records.append(
                    {
                        "date": idx.strftime("%Y-%m-%d"),
                        "open": round(float(row.get("Open", 0) or 0), 2),
                        "high": round(float(row.get("High", 0) or 0), 2),
                        "low": round(float(row.get("Low", 0) or 0), 2),
                        "close": round(float(row.get("Close", 0) or 0), 2),
                        "volume": int(row.get("Volume", 0) or 0),
                    }
                )

            # Cache for 24h
            market_cache.set(cache_key, records)
            return records
        except Exception as exc:
            logger.error("YahooFinance history error for %s: %s", symbol, exc)
            return []

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch a real-time quote with fundamentals."""
        cache_key = f"yahoo:quote:{symbol}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = self._get_ticker(symbol)
            fast_info = {}
            try:
                fast_info = ticker.fast_info
            except Exception:
                pass

            price = getattr(fast_info, "last_price", None)
            if price is None:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])

            info = {}
            try:
                info = ticker.info or {}
            except Exception:
                info = {}

            quote = {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "price": round(float(price), 2) if price else 0.0,
                "previous_close": round(float(getattr(fast_info, "previous_close", 0) or 0), 2),
                "open": round(float(getattr(fast_info, "open", 0) or 0), 2),
                "day_high": round(float(getattr(fast_info, "day_high", 0) or 0), 2),
                "day_low": round(float(getattr(fast_info, "day_low", 0) or 0), 2),
                "volume": int(getattr(fast_info, "last_volume", 0) or 0),
                "market_cap": info.get("marketCap") or 0,
                "pe_ratio": round(float(info["trailingPE"]), 2) if info.get("trailingPE") else None,
                "dividend_yield": round(float(info["dividendYield"] * 100), 2) if info.get("dividendYield") else None,
                "fifty_two_week_high": round(float(info["fiftyTwoWeekHigh"]), 2) if info.get("fiftyTwoWeekHigh") else None,
                "fifty_two_week_low": round(float(info["fiftyTwoWeekLow"]), 2) if info.get("fiftyTwoWeekLow") else None,
                "currency": info.get("currency") or "INR",
                "sector": info.get("sector") or "",
                "industry": info.get("industry") or "",
            }

            market_cache.set(cache_key, quote)
            return quote
        except Exception as exc:
            logger.error("YahooFinance quote error for %s: %s", symbol, exc)
            return {
                "symbol": symbol,
                "name": symbol,
                "price": 0.0,
                "previous_close": 0.0,
                "open": 0.0,
                "day_high": 0.0,
                "day_low": 0.0,
                "volume": 0,
                "market_cap": 0,
                "pe_ratio": None,
                "dividend_yield": None,
                "fifty_two_week_high": None,
                "fifty_two_week_low": None,
                "currency": "INR",
                "sector": "",
                "industry": "",
            }
