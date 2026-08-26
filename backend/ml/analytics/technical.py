"""
Technical Analyzer

Computes technical indicators from historical market data:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Moving Averages (SMA 20/50/200, EMA)
- Support & Resistance Levels
- Trend detection
- Buy/Hold/Sell signal
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.market.manager import market_data_manager

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Computes technical indicators from price data."""

    def get_history(self, query: str, period: str = "2y") -> pd.DataFrame:
        return market_data_manager.get_history_df(query, period=period)

    def compute_rsi(self, closes: pd.Series, period: int = 14) -> float:
        """Compute the latest RSI value."""
        if closes.empty or len(closes) < period + 1:
            return 50.0
        delta = closes.diff().dropna()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return round(float(rsi.iloc[-1]), 2)

    def compute_macd(self, closes: pd.Series) -> Dict[str, float]:
        """Compute MACD line, signal, and histogram."""
        if closes.empty or len(closes) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        ema12 = closes.ewm(span=12, adjust=False).mean()
        ema26 = closes.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {
            "macd": round(float(macd.iloc[-1]), 4),
            "signal": round(float(signal.iloc[-1]), 4),
            "histogram": round(float(histogram.iloc[-1]), 4),
        }

    def compute_moving_averages(self, closes: pd.Series) -> Dict[str, float]:
        """Compute SMA(20), SMA(50), SMA(200), and EMA(20)."""
        result = {}
        for period in [20, 50, 200]:
            if len(closes) >= period:
                result[f"sma_{period}"] = round(float(closes.rolling(period).mean().iloc[-1]), 2)
            else:
                result[f"sma_{period}"] = None
        if len(closes) >= 20:
            result["ema_20"] = round(float(closes.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
        else:
            result["ema_20"] = None
        return result

    def compute_support_resistance(
        self, df: pd.DataFrame, lookback: int = 180
    ) -> Dict[str, float]:
        """Estimate support and resistance levels from recent pivots."""
        if df.empty or "close" not in df.columns:
            return {"support": 0.0, "resistance": 0.0}
        recent = df.tail(lookback)
        if recent.empty:
            return {"support": 0.0, "resistance": 0.0}
        highs = recent["high"].dropna()
        lows = recent["low"].dropna()
        if highs.empty or lows.empty:
            return {"support": 0.0, "resistance": 0.0}
        # Resistance: recent local highs (top quantile)
        resistance = float(highs.quantile(0.95))
        # Support: recent local lows (bottom quantile)
        support = float(lows.quantile(0.05))
        return {"support": round(support, 2), "resistance": round(resistance, 2)}

    def detect_trend(self, closes: pd.Series) -> str:
        """Detect the overall trend from moving averages."""
        if closes.empty or len(closes) < 50:
            return "Neutral"
        sma50 = closes.rolling(50).mean().iloc[-1]
        sma200 = closes.rolling(200).mean().iloc[-1]
        last = closes.iloc[-1]
        if np.isnan(sma200):
            if last > sma50:
                return "Bullish"
            return "Bearish"
        if last > sma50 > sma200:
            return "Bullish"
        if last < sma50 < sma200:
            return "Bearish"
        return "Neutral"

    def generate_signal(
        self,
        query: str,
        rsi: float,
        macd: Dict[str, float],
        trend: str,
    ) -> str:
        """Generate a Buy/Hold/Sell signal using technical indicators."""
        current_price = None
        df = self.get_history(query, "1y")
        if not df.empty:
            current_price = float(df["close"].iloc[-1])
        smas = self.compute_moving_averages(df["close"]) if not df.empty else {}

        signals = 0
        # RSI
        if rsi < 30:
            signals += 1  # Oversold -> buy
        elif rsi > 70:
            signals -= 1  # Overbought -> sell
        # MACD
        if macd["macd"] > macd["signal"]:
            signals += 1
        else:
            signals -= 1
        # Trend
        if trend == "Bullish":
            signals += 1
        elif trend == "Bearish":
            signals -= 1
        # Price vs SMA50
        sma50 = smas.get("sma_50")
        if sma50 and current_price:
            if current_price > sma50:
                signals += 1
            else:
                signals -= 1

        if signals >= 2:
            return "Buy"
        if signals <= -2:
            return "Sell"
        return "Hold"

    def analyze(self, query: str) -> Dict[str, Any]:
        """Run full technical analysis for a symbol."""
        df = self.get_history(query, "2y")
        if df.empty or "close" not in df.columns:
            return {
                "symbol": query,
                "available": False,
                "message": "No technical data available",
            }

        closes = df["close"].dropna()
        quote = market_data_manager.get_quote(query)
        current_price = float(closes.iloc[-1])

        rsi = self.compute_rsi(closes)
        macd = self.compute_macd(closes)
        smas = self.compute_moving_averages(closes)
        sr = self.compute_support_resistance(df)
        trend = self.detect_trend(closes)
        signal = self.generate_signal(query, rsi, macd, trend)

        return {
            "symbol": query,
            "name": quote.get("name", query),
            "current_price": round(current_price, 2),
            "rsi": rsi,
            "macd": macd,
            "moving_averages": smas,
            "support": sr["support"],
            "resistance": sr["resistance"],
            "trend": trend,
            "signal": signal,
            "available": True,
        }


# Singleton
technical_analyzer = TechnicalAnalyzer()
