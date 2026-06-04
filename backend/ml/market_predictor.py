"""
Market Price Prediction using ML Models
=======================================
Uses XGBoost, Random Forest, and Linear Regression for price forecasting.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import os


# Convert numpy types to Python native types for JSON serialization
def convert_numpy(obj):
    """Convert numpy types to native Python types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    return obj


try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class MarketPricePredictor:
    """
    ML-based market price prediction using multiple algorithms.
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.crop_models = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize and train models for each crop"""
        if not SKLEARN_AVAILABLE:
            print("Warning: sklearn not available, using simplified model")
            return

        # Train models for each crop with historical data patterns
        crops = ["wheat", "rice", "cotton", "maize", "soybean", "sugarcane"]

        for crop in crops:
            self.crop_models[crop] = self._train_crop_model(crop)

    def _generate_historical_data(self, crop: str, n_days: int = 365) -> np.ndarray:
        """Generate realistic historical price data based on crop patterns"""
        np.random.seed(42 + hash(crop) % 100)

        base_prices = {
            "wheat": 2275,
            "rice": 2183,
            "cotton": 6620,
            "maize": 2090,
            "soybean": 4600,
            "sugarcane": 315,
        }
        base = base_prices.get(crop, 2000)

        # Generate features: day_of_year, month, year_trend, season
        X = []
        y = []

        for i in range(n_days):
            date = datetime.now() - timedelta(days=n_days - i)
            day_of_year = date.timetuple().tm_yday
            month = date.month

            # Seasonal variation
            season_factor = np.sin(2 * np.pi * day_of_year / 365) * 0.1

            # Trend factor (slight upward trend)
            trend_factor = i / n_days * 0.15

            # Random noise
            noise = np.random.normal(0, 0.05)

            # Calculate price
            price = base * (1 + season_factor + trend_factor + noise)

            features = [
                day_of_year / 365.0,  # normalized day
                month / 12.0,  # normalized month
                i / n_days,  # trend
                1 if month in [6, 7, 8, 9] else 0,  # monsoon season
                1 if month in [3, 4, 5] else 0,  # summer
                1 if month in [11, 12, 1, 2] else 0,  # winter
                np.sin(2 * np.pi * day_of_year / 365),  # seasonal sine
                np.cos(2 * np.pi * day_of_year / 365),  # seasonal cosine
            ]

            X.append(features)
            y.append(price)

        return np.array(X), np.array(y)

    def _train_crop_model(self, crop: str) -> Dict[str, Any]:
        """Train all models for a specific crop"""
        X, y = self._generate_historical_data(crop, n_days=365)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        models = {}
        results = {}

        # 1. XGBoost
        if XGBOOST_AVAILABLE:
            xgb_model = xgb.XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            )
            xgb_model.fit(X_train_scaled, y_train)
            y_pred = xgb_model.predict(X_test_scaled)
            models["xgboost"] = xgb_model
            results["xgboost"] = {
                "mae": mean_absolute_error(y_test, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                "r2": r2_score(y_test, y_pred),
            }

        # 2. Gradient Boosting
        gb_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )
        gb_model.fit(X_train_scaled, y_train)
        y_pred = gb_model.predict(X_test_scaled)
        models["gradient_boosting"] = gb_model
        results["gradient_boosting"] = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        # 3. Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )
        rf_model.fit(X_train_scaled, y_train)
        y_pred = rf_model.predict(X_test_scaled)
        models["random_forest"] = rf_model
        results["random_forest"] = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        # 4. Ridge Regression
        ridge_model = Ridge(alpha=1.0)
        ridge_model.fit(X_train_scaled, y_train)
        y_pred = ridge_model.predict(X_test_scaled)
        models["ridge"] = ridge_model
        results["ridge"] = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }

        return {
            "models": models,
            "scaler": scaler,
            "results": results,
            "base_price": {
                "wheat": 2275,
                "rice": 2183,
                "cotton": 6620,
                "maize": 2090,
                "soybean": 4600,
                "sugarcane": 315,
            }.get(crop, 2000),
        }

    def predict(self, crop: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate price predictions for the next N days"""
        crop = crop.lower()

        if crop not in self.crop_models:
            crop = "wheat"  # fallback

        model_data = self.crop_models[crop]
        models = model_data["models"]
        scaler = model_data["scaler"]
        base_price = model_data["base_price"]

        predictions = []
        ensemble_predictions = []

        for day in range(1, days_ahead + 1):
            future_date = datetime.now() + timedelta(days=day)
            day_of_year = future_date.timetuple().tm_yday
            month = future_date.month

            # Create features for prediction
            features = np.array(
                [
                    [
                        day_of_year / 365.0,
                        month / 12.0,
                        day / days_ahead,
                        1 if month in [6, 7, 8, 9] else 0,
                        1 if month in [3, 4, 5] else 0,
                        1 if month in [11, 12, 1, 2] else 0,
                        np.sin(2 * np.pi * day_of_year / 365),
                        np.cos(2 * np.pi * day_of_year / 365),
                    ]
                ]
            )

            scaled_features = scaler.transform(features)

            model_preds = {}
            all_preds = []

            # Get predictions from each model
            for model_name, model in models.items():
                pred = float(model.predict(scaled_features)[0])
                model_preds[model_name] = round(pred, 2)
                all_preds.append(pred)

            # Ensemble (weighted average)
            ensemble_pred = np.mean(all_preds)
            ensemble_predictions.append(ensemble_pred)

            predictions.append(
                {
                    "day": day,
                    "date": future_date.strftime("%Y-%m-%d"),
                    "xgboost": float(model_preds.get("xgboost", ensemble_pred)),
                    "gradient_boosting": float(
                        model_preds.get("gradient_boosting", ensemble_pred)
                    ),
                    "random_forest": float(
                        model_preds.get("random_forest", ensemble_pred)
                    ),
                    "ridge": float(model_preds.get("ridge", ensemble_pred)),
                    "ensemble": round(float(ensemble_pred), 2),
                }
            )

        # Calculate trend
        price_change = ensemble_predictions[-1] - ensemble_predictions[0]
        trend_pct = (price_change / ensemble_predictions[0]) * 100

        if trend_pct > 1:
            trend = "rising"
        elif trend_pct < -1:
            trend = "falling"
        else:
            trend = "stable"

        # Find best selling window
        best_day = int(np.argmax(ensemble_predictions)) + 1
        best_price = float(max(ensemble_predictions))

        result = {
            "crop_type": crop,
            "current_price": round(base_price, 2),
            "predictions": predictions,
            "trend": trend,
            "trend_percentage": round(float(trend_pct), 2),
            "best_sell_day": best_day,
            "best_expected_price": round(best_price, 2),
            "model_performance": model_data["results"],
            "algorithm_used": "XGBoost + Gradient Boosting + Random Forest + Ridge Ensemble",
            "training_data_points": 365,
            "forecast_days": days_ahead,
        }

        return convert_numpy(result)

    def get_current_price(self, crop: str) -> float:
        """Get current market price for a crop"""
        crop = crop.lower()
        base_prices = {
            "wheat": 2275,
            "rice": 2183,
            "cotton": 6620,
            "maize": 2090,
            "soybean": 4600,
            "sugarcane": 315,
            "tomato": 1500,
            "potato": 1200,
            "onion": 1800,
        }
        return base_prices.get(crop, 2000)


# Singleton instance
_predictor = None


def get_predictor() -> MarketPricePredictor:
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = MarketPricePredictor()
    return _predictor


def predict_market_prices(crop_type: str = "wheat", days: int = 30) -> Dict[str, Any]:
    """
    Main function to predict market prices using ML.

    Args:
        crop_type: Type of crop (wheat, rice, cotton, etc.)
        days: Number of days to forecast

    Returns:
        Dictionary with predictions from multiple ML models
    """
    predictor = get_predictor()
    return predictor.predict(crop_type, days)


def get_current_market_price(crop_type: str) -> float:
    """Get current market price"""
    predictor = get_predictor()
    return predictor.get_current_price(crop_type)


# Test the models
if __name__ == "__main__":
    print("Testing ML Market Price Prediction...")
    print("=" * 50)

    result = predict_market_prices("wheat", days=10)

    print(f"\nCrop: {result['crop_type'].upper()}")
    print(f"Current Price: ₹{result['current_price']}/quintal")
    print(f"Trend: {result['trend']} ({result['trend_percentage']}%)")
    print(
        f"Best Sell Day: Day {result['best_sell_day']} @ ₹{result['best_expected_price']}"
    )

    print("\n--- Model Performance (on test set) ---")
    for model, metrics in result["model_performance"].items():
        print(
            f"{model}: MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}, R²={metrics['r2']:.3f}"
        )

    print("\n--- 10-Day Forecast ---")
    for p in result["predictions"]:
        print(
            f"Day {p['day']}: XGB={p['xgboost']}, RF={p['random_forest']}, Ensemble={p['ensemble']}"
        )
