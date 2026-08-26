"""
Market Data Manager

High-level orchestrator that wraps market data providers and exposes
convenient methods for fetching historical data, quotes, and multi-asset
comparisons. Handles provider fallback and centralized caching.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.core.config import settings
from backend.market.cache import market_cache
from backend.market.symbols import MARKET_SYMBOLS, get_symbol_info
from backend.market.yahoo_provider import YahooFinanceProvider
from backend.market.alpha_vantage_provider import AlphaVantageProvider

logger = logging.getLogger(__name__)


class MarketDataManager:
    """Unified interface for all market data operations."""

    def __init__(self):
        self.providers = []
        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize providers in priority order."""
        if settings.enable_live_market_data:
            yahoo = YahooFinanceProvider()
            if yahoo.is_available():
                self.providers.append(yahoo)
            alpha = AlphaVantageProvider()
            if alpha.is_available():
                self.providers.append(alpha)

        if not self.providers:
            logger.warning("No live market data provider available. Falling back to cached data.")

    def _active_provider(self):
        """Return the first available provider."""
        for provider in self.providers:
            if provider.is_available():
                return provider
        return None

    # ---- Resolution ----
    def resolve(self, query: str) -> Dict[str, str]:
        """Resolve a user query/name to symbol metadata."""
        return get_symbol_info(query)

    def get_symbols(self, asset_class: Optional[str] = None) -> List[Dict[str, str]]:
        """List all supported symbols, optionally filtered by asset class."""
        result = []
        for key, info in MARKET_SYMBOLS.items():
            if asset_class and info["asset_class"] != asset_class:
                continue
            result.append({"key": key, **info})
        return result

    # ---- History ----
    def get_history(
        self,
        query: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Fetch historical OHLCV data for a symbol or named asset."""
        info = self.resolve(query)
        yahoo_symbol = info["symbol"]
        provider = self._active_provider()
        if provider:
            records = provider.get_history(yahoo_symbol, period, interval)
            if records:
                # Resolve asset metadata
                for r in records:
                    r["_symbol"] = info["symbol"]
                    r["_name"] = info["name"]
                    r["_asset_class"] = info["asset_class"]
                return records
        # Fallback to cache
        cached = market_cache.get(f"yahoo:history:{yahoo_symbol}:{period}:{interval}")
        if cached:
            for r in cached:
                r["_symbol"] = info["symbol"]
                r["_name"] = info["name"]
                r["_asset_class"] = info["asset_class"]
        return cached or []

    def get_history_df(
        self,
        query: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Fetch history as a DataFrame with a datetime index."""
        records = self.get_history(query, period, interval)
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        return df

    # ---- Quote ----
    def get_quote(self, query: str) -> Dict[str, Any]:
        """Fetch a quote for a symbol or named asset."""
        info = self.resolve(query)
        provider = self._active_provider()
        if not provider:
            cached = market_cache.get(f"yahoo:quote:{info['symbol']}")
            return cached or {
                "symbol": info["symbol"],
                "name": info["name"],
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
                "currency": info["currency"],
                "sector": info.get("sector", ""),
                "industry": "",
            }
        quote = provider.get_quote(info["symbol"])
        quote.update(
            {
                "_name": info["name"],
                "_asset_class": info["asset_class"],
                "_key": self._find_key(info["symbol"]),
            }
        )
        return quote

    def _find_key(self, yahoo_symbol: str) -> str:
        """Find the friendly key for a yahoo symbol."""
        for key, info in MARKET_SYMBOLS.items():
            if info["symbol"] == yahoo_symbol:
                return key
        return yahoo_symbol

    # ---- Multi-asset comparison ----
    def get_comparison(
        self,
        queries: List[str],
        period: str = "5y",
        interval: str = "1mo",
        normalize: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch normalized historical series for multiple assets to allow
        direct comparison on a single chart.

        Returns:
            {
              "dates": [...],
              "assets": { "NIFTY 50": {...}, "GOLD": {...} }
            }
        """
        series_map: Dict[str, Dict[str, Any]] = {}
        all_dates = set()

        for q in queries:
            df = self.get_history_df(q, period, interval)
            if df.empty:
                continue
            info = self.resolve(q)
            series = df["close"].dropna()
            if series.empty:
                continue
            # Normalize to base 100
            base = float(series.iloc[0]) if normalize and float(series.iloc[0]) != 0 else 1
            values = {d.strftime("%Y-%m-%d"): round(float(v / base) * 100, 2) for d, v in series.items()}
            all_dates.update(values.keys())
            series_map[info["name"]] = {
                "key": self._find_key(info["symbol"]),
                "values": values,
            }

        sorted_dates = sorted(all_dates)
        return {
            "dates": sorted_dates,
            "assets": series_map,
            "normalized": normalize,
        }

    # ---- Preload key assets ----
    def preload(self, queries: Optional[List[str]] = None) -> Dict[str, int]:
        """Pre-fetch and cache 5 years of data for key assets."""
        targets = queries or [
            "NIFTY 50",
            "SENSEX",
            "BANK NIFTY",
            "GOLD",
            "SILVER",
            "RELIANCE",
            "TCS",
            "INFY",
            "HDFCBANK",
            "ICICIBANK",
            "SBIN",
            "ITC",
            "NIFTYBEES",
            "GOLDBEES",
        ]
        loaded = {}
        for q in targets:
            records = self.get_history(q, period="5y", interval="1d")
            loaded[q] = len(records)
        return loaded


# Singleton
market_data_manager = MarketDataManager()
