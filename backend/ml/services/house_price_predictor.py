"""
House Price Predictor Service

Predicts house prices using trained XGBoost/Random Forest models.
Trains model once and loads from saved file.
"""

import pickle
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from backend.core.config import settings
from backend.ml.dataset_config import dataset_config
from backend.schemas.ai import HousePriceRequest


class HousePricePredictor:
    """House price prediction using trained ML models."""

    def __init__(self):
        self.model = None
        self.model_path = Path(settings.model_storage_path) / "house_price_model.pkl"
        self.location_encoder = {}
        self._load_model()

    def _load_model(self):
        """Load trained model from disk."""
        if self.model_path.exists():
            with open(self.model_path, "rb") as f:
                saved_data = pickle.load(f)
                self.model = saved_data.get("model")
                self.location_encoder = saved_data.get("location_encoder", {})

    def _save_model(self, model, location_encoder: dict):
        """Save trained model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": model, "location_encoder": location_encoder}, f)

    def train(self) -> Dict:
        """Train the house price prediction model."""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler

        # Load dataset
        dataset_path = dataset_config.get_raw_path("real_estate")
        if not dataset_path or not dataset_path.exists():
            return {"status": "error", "message": "House price dataset not found"}

        df = pd.read_csv(dataset_path)

        # Identify columns
        price_col = None
        area_col = None
        bedroom_col = None
        bathroom_col = None
        location_col = None

        for col in df.columns:
            col_lower = col.lower()
            if "price" in col_lower and not price_col:
                price_col = col
            elif "area" in col_lower and not area_col:
                area_col = col
            elif "bedroom" in col_lower and not bedroom_col:
                bedroom_col = col
            elif "bathroom" in col_lower and not bathroom_col:
                bathroom_col = col
            elif "location" in col_lower and not location_col:
                location_col = col

        if not all([price_col, area_col]):
            return {"status": "error", "message": f"Required columns not found. Found: {list(df.columns)}"}

        # Prepare features
        df = df.copy()
        features = [area_col]
        
        if bedroom_col:
            features.append(bedroom_col)
        if bathroom_col:
            features.append(bathroom_col)

        # Handle location
        if location_col:
            df[location_col] = df[location_col].astype(str).str.strip().str.lower()
            # Encode locations
            unique_locations = df[location_col].unique()
            self.location_encoder = {loc: i for i, loc in enumerate(unique_locations)}
            df["location_encoded"] = df[location_col].map(self.location_encoder)
            features.append("location_encoded")

        df = df.dropna(subset=[price_col] + features)

        if len(df) < 10:
            return {"status": "error", "message": "Not enough data after preprocessing"}

        X = df[features].values
        y = df[price_col].values

        # Scale features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Save model with scaler
        self._save_model({"model": self.model, "scaler": scaler}, self.location_encoder)

        return {
            "status": "success",
            "message": "Model trained successfully",
            "train_r2": round(train_score, 4),
            "test_r2": round(test_score, 4),
            "samples": len(X),
            "features": features,
        }

    def predict(self, request: HousePriceRequest) -> Dict:
        """Predict house price for given features."""
        # Auto-train if no model
        if self.model is None:
            train_result = self.train()
            if train_result.get("status") == "error":
                return self._fallback_prediction(request)

        # Prepare features
        try:
            location_encoded = self.location_encoder.get(
                request.location.strip().lower(),
                len(self.location_encoder)  # Unknown location
            )

            features = [request.area, request.bedrooms, request.bathrooms, location_encoded]
            
            # Get scaler from saved model
            if isinstance(self.model, dict):
                scaler = self.model.get("scaler")
                model = self.model.get("model")
            else:
                scaler = None
                model = self.model

            if scaler:
                features_scaled = scaler.transform(np.array(features).reshape(1, -1))
            else:
                features_scaled = np.array(features).reshape(1, -1)

            if model:
                prediction = model.predict(features_scaled)[0]
            else:
                return self._fallback_prediction(request)

            # Calculate price range (±10%)
            price_range = prediction * 0.1

            # Determine investment rating
            if prediction > 0:
                rating = "Good Investment" if request.area > 1000 else "Moderate Investment"
            else:
                rating = "Unknown"

            return {
                "predicted_price": round(prediction, 2),
                "price_range_low": round(prediction - price_range, 2),
                "price_range_high": round(prediction + price_range, 2),
                "investment_rating": rating,
                "confidence_score": 0.8,
            }

        except Exception as e:
            return self._fallback_prediction(request)

    def _fallback_prediction(self, request: HousePriceRequest) -> Dict:
        """Fallback when model is not available."""
        estimated_price = request.area * 5000 + request.bedrooms * 500000 + request.bathrooms * 300000
        return {
            "predicted_price": round(estimated_price, 2),
            "price_range_low": round(estimated_price * 0.9, 2),
            "price_range_high": round(estimated_price * 1.1, 2),
            "investment_rating": "Estimate Only",
            "confidence_score": 0.3,
        }
