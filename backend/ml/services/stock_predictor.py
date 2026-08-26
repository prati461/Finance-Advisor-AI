"""
Stock Price Predictor Service

Predicts stock prices using XGBoost / Random Forest trained on REAL
historical market data. Also computes technical indicators, support/
resistance, and a Buy/Hold/Sell recommendation with explanation.

The model is trained on-demand from live market data (falling back to
cached data when offline).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.ml.analytics.metrics import analytics_engine
from backend.ml.analytics.technical import technical_analyzer
from backend.market.manager import market_data_manager

logger = logging.getLogger(__name__)


class StockPredictor:
    """Stock price prediction using ML models trained on real data."""

    def __init__(self):
        self.model = None
        self.scaler = None

    def _train_model(self, df: pd.DataFrame) -> bool:
        """Train an XGBoost model on the given price history."""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler

            if df.empty or len(df) < 30:
                return False

            data = df.copy()
            data["returns"] = data["close"].pct_change()
            data["high_low"] = data["high"] / data["low"].replace(0, np.nan)
            data["close_open"] = data["close"] / data["open"].replace(0, np.nan)
            data["ma5"] = data["close"].rolling(5).mean()
            data["ma10"] = data["close"].rolling(10).mean()
            data["ma20"] = data["close"].rolling(20).mean()
            data["vol_ma"] = data["volume"].rolling(5).mean()
            data = data.dropna()

            if len(data) < 30:
                return False

            feature_cols = [
                "open", "high", "low", "close", "volume",
                "returns", "high_low", "close_open", "ma5", "ma10", "ma20", "vol_ma",
            ]
            X = data[feature_cols].values
            y = data["close"].shift(-1).dropna().values
            X = X[: len(y)]

            if len(X) < 30:
                return False

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Try XGBoost first, fall back to RandomForest
            try:
                from xgboost import XGBRegressor

                self.model = XGBRegressor(
                    n_estimators=200, max_depth=6, learning_rate=0.05,
                    random_state=42, n_jobs=-1,
                )
            except Exception:
                self.model = RandomForestRegressor(
                    n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
                )
            self.model.fit(X_scaled, y)
            return True
        except Exception as exc:
            logger.error("Model training failed: %s", exc)
            return False

    def _prepare_features(self, row: pd.Series) -> np.ndarray:
        """Prepare a feature vector from the latest data row."""
        close = float(row.get("close", 0))
        open_ = float(row.get("open", close))
        high = float(row.get("high", close))
        low = float(row.get("low", close))
        volume = float(row.get("volume", 0))
        returns = float(row.get("returns", 0))
        high_low = (high / low) if low else 1.0
        close_open = (close / open_) if open_ else 1.0
        ma5 = float(row.get("ma5", close))
        ma10 = float(row.get("ma10", close))
        ma20 = float(row.get("ma20", close))
        vol_ma = float(row.get("vol_ma", volume))
        return np.array(
            [open_, high, low, close, volume, returns, high_low, close_open, ma5, ma10, ma20, vol_ma]
        ).reshape(1, -1)

    def predict(self, symbol: str) -> Dict[str, Any]:
        """Predict stock prices and generate a full analysis."""
        info = market_data_manager.resolve(symbol)
        yahoo_symbol = info["symbol"]

        # Fetch 2 years of data for training
        df = market_data_manager.get_history_df(yahoo_symbol, "2y")
        if df.empty:
            raise ValueError(
                f"No market history is available for {symbol}. "
                "Try again later or choose a supported symbol."
            )

        # Technical analysis
        tech = technical_analyzer.analyze(yahoo_symbol)
        quote = market_data_manager.get_quote(yahoo_symbol)

        # Train model
        trained = self._train_model(df)

        # Prepare latest row with features
        data = df.copy()
        data["returns"] = data["close"].pct_change()
        data["high_low"] = data["high"] / data["low"].replace(0, np.nan)
        data["close_open"] = data["close"] / data["open"].replace(0, np.nan)
        data["ma5"] = data["close"].rolling(5).mean()
        data["ma10"] = data["close"].rolling(10).mean()
        data["ma20"] = data["close"].rolling(20).mean()
        data["vol_ma"] = data["volume"].rolling(5).mean()
        data = data.dropna()

        last_close = float(df["close"].iloc[-1])
        predictions = []
        tomorrow_price = last_close
        week_avg = last_close
        month_avg = last_close

        if trained and self.model is not None and not data.empty:
            try:
                current_features = self._prepare_features(data.iloc[-1])
                current_features = self.scaler.transform(current_features)
                today = datetime.now()
                for i in range(30):
                    pred = float(self.model.predict(current_features)[0])
                    pred_date = (today + timedelta(days=i + 1)).strftime("%Y-%m-%d")
                    predictions.append({"date": pred_date, "price": round(pred, 2)})
                    # Update features for next step
                    current_features = self._update_features(current_features, pred)

                tomorrow_price = predictions[0]["price"] if predictions else last_close
                week_avg = sum(p["price"] for p in predictions[:7]) / 7 if len(predictions) >= 7 else last_close
                month_avg = sum(p["price"] for p in predictions) / len(predictions) if predictions else last_close
            except Exception as exc:
                logger.warning("Prediction step failed: %s", exc)
                predictions = []

        # Trend & signal
        trend = tech.get("trend", "Neutral") if tech.get("available") else "Neutral"
        signal = tech.get("signal", "Hold") if tech.get("available") else "Hold"
        rsi = tech.get("rsi", 50) if tech.get("available") else 50
        macd = tech.get("macd", {}) if tech.get("available") else {}
        support = tech.get("support", last_close * 0.95) if tech.get("available") else last_close * 0.95
        resistance = tech.get("resistance", last_close * 1.05) if tech.get("available") else last_close * 1.05
        moving_averages = tech.get("moving_averages", {}) if tech.get("available") else {}

        # Confidence
        confidence = analytics_engine.compute_confidence_score(df)
        if not trained:
            confidence = round(confidence * 0.5, 2)

        # Explanation
        explanation = self._generate_explanation(signal, trend, rsi, last_close, tomorrow_price, macd)

        if not predictions:
            raise ValueError(
                f"Insufficient usable historical data to forecast {info['name']}."
            )

        return {
            "symbol": info["name"],
            "ticker": yahoo_symbol,
            "current_price": round(last_close, 2),
            "tomorrow_price": round(tomorrow_price, 2),
            "next_7_days_avg": round(week_avg, 2),
            "next_30_days_avg": round(month_avg, 2),
            "trend": trend,
            "signal": signal,
            "rsi": rsi,
            "macd": macd,
            "moving_averages": moving_averages,
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "confidence_score": confidence,
            "predictions": predictions,
            "explanation": explanation,
            "fifty_two_week_high": quote.get("fifty_two_week_high"),
            "fifty_two_week_low": quote.get("fifty_two_week_low"),
            "market_cap": quote.get("market_cap"),
            "pe_ratio": quote.get("pe_ratio"),
            "dividend_yield": quote.get("dividend_yield"),
        }

    def _update_features(self, features: np.ndarray, new_price: float) -> np.ndarray:
        """Update the feature vector with a new predicted price."""
        updated = features.copy()
        if updated.shape[1] >= 12:
            updated[0, 3] = new_price  # close
            updated[0, 0] = new_price * 0.99  # open
            updated[0, 1] = new_price * 1.01  # high
            updated[0, 2] = new_price * 0.99  # low
        return updated

    def _generate_explanation(
        self,
        signal: str,
        trend: str,
        rsi: float,
        current: float,
        tomorrow: float,
        macd: Dict[str, float],
    ) -> str:
        """Generate an AI explanation for the recommendation."""
        parts = []
        if signal == "Buy":
            parts.append(f"Technical indicators suggest a BUY. RSI of {rsi:.0f} indicates the stock is not overbought")
        elif signal == "Sell":
            parts.append(f"Technical indicators suggest SELL. RSI of {rsi:.0f} indicates overbought conditions")
        else:
            parts.append(f"Technical indicators suggest HOLD. RSI of {rsi:.0f} is in neutral territory")

        if trend == "Bullish":
            parts.append("with a bullish trend (price above key moving averages)")
        elif trend == "Bearish":
            parts.append("with a bearish trend (price below key moving averages)")

        if macd.get("macd", 0) > macd.get("signal", 0):
            parts.append("and MACD is above its signal line (positive momentum)")
        else:
            parts.append("and MACD is below its signal line (negative momentum)")

        change_pct = ((tomorrow - current) / current * 100) if current else 0
        parts.append(f"Model projects a {change_pct:+.1f}% move to ₹{tomorrow:.0f} tomorrow.")
        return " ".join(parts)

    def _fallback(self, symbol: str) -> Dict[str, Any]:
        """Fallback when no data is available."""
        return {
            "symbol": symbol,
            "ticker": symbol,
            "current_price": 0,
            "tomorrow_price": 0,
            "next_7_days_avg": 0,
            "next_30_days_avg": 0,
            "trend": "Unknown",
            "signal": "Hold",
            "rsi": 50,
            "macd": {},
            "moving_averages": {},
            "support": 0,
            "resistance": 0,
            "confidence_score": 0,
            "predictions": [],
            "explanation": "No historical data available for prediction.",
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "market_cap": 0,
            "pe_ratio": None,
            "dividend_yield": None,
        }
