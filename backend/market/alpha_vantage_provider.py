"""
Alpha Vantage Market Data Provider

Optional fallback provider using the Alpha Vantage API.
Requires ALPHA_VANTAGE_API_KEY. Used only when Yahoo Finance is unavailable.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from backend.core.config import settings
from backend.market.base import MarketDataProvider
from backend.market.cache import market_cache

logger = logging.getLogger(__name__)

BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageProvider(MarketDataProvider):
    """Market data provider backed by Alpha Vantage REST API."""

    name = "alpha_vantage"

    def is_available(self) -> bool:
        return bool(settings.alpha_vantage_api_key)

    def _get(self, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make a GET request to Alpha Vantage with the API key."""
        params["apikey"] = settings.alpha_vantage_api_key
        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("AlphaVantage request failed: %s", exc)
            return None

    def get_history(
        self,
        symbol: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Fetch historical daily OHLCV data."""
        cache_key = f"alpha:history:{symbol}:{period}:{interval}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get(
            {"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "full"}
        )
        if not data or "Time Series (Daily)" not in data:
            return []

        series = data["Time Series (Daily)"]
        records = []
        for date_str, values in series.items():
            records.append(
                {
                    "date": date_str,
                    "open": round(float(values.get("1. open", 0)), 2),
                    "high": round(float(values.get("2. high", 0)), 2),
                    "low": round(float(values.get("3. low", 0)), 2),
                    "close": round(float(values.get("4. close", 0)), 2),
                    "volume": int(float(values.get("5. volume", 0))),
                }
            )
        records.sort(key=lambda r: r["date"])
        market_cache.set(cache_key, records)
        return records

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch a quote for a symbol."""
        cache_key = f"alpha:quote:{symbol}"
        cached = market_cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get({"function": "GLOBAL_QUOTE", "symbol": symbol})
        quote_raw = (data or {}).get("Global Quote", {})
        quote = {
            "symbol": symbol,
            "name": symbol,
            "price": float(quote_raw.get("05. price", 0) or 0),
            "previous_close": float(quote_raw.get("08. previous close", 0) or 0),
            "open": float(quote_raw.get("02. open", 0) or 0),
            "day_high": float(quote_raw.get("03. high", 0) or 0),
            "day_low": float(quote_raw.get("04. low", 0) or 0),
            "volume": int(float(quote_raw.get("06. volume", 0) or 0)),
            "market_cap": 0,
            "pe_ratio": None,
            "dividend_yield": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "currency": "USD",
            "sector": "",
            "industry": "",
        }
        market_cache.set(cache_key, quote)
        return quote
