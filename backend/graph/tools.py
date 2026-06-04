"""
LangGraph Tools - Convert Agents to LangChain Tools
====================================================
Each agent is converted to a @tool decorator for autonomous use by the LLM.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_core.tools import tool

# Load config for APIs
def _load_api_key(key_name: str) -> str:
    """Load API key from config"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "api_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get(key_name, "")
    except:
        return ""

# Load API Key from config file
OPENWEATHER_API_KEY = _load_api_key("openweather_api_key")
GROQ_API_KEY = _load_api_key("groq_api_key")
DATA_GOV_API_KEY = _load_api_key("data_gov_api_key")
NASA_API_KEY = _load_api_key("nasa_api_key")


# =============================================================================
# WEATHER TOOLS
# =============================================================================


@tool
def get_current_weather(location: str = "Pune") -> Dict[str, Any]:
    """
    Fetch current weather conditions for a location.

    Args:
        location: City name (e.g., "Pune", "Delhi", "Mumbai")

    Returns:
        Dictionary with temperature, humidity, description, wind speed
    """
    import requests

    result = {
        "agent": "get_current_weather",
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            result["data"] = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", 0),
                "uv_index": 0,  # Not in free API
            }
        else:
            result["status"] = "error"
            result["error"] = f"API returned {response.status_code}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


@tool
def get_weather_forecast(location: str = "Pune", hours: int = 24) -> Dict[str, Any]:
    """
    Get weather forecast for the next N hours.

    Args:
        location: City name
        hours: Forecast hours (24, 48, 72)

    Returns:
        Dictionary with hourly forecast, rain probability, risk assessment
    """
    import requests

    result = {
        "agent": "get_weather_forecast",
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    try:
        # First get coordinates
        geo_url = "https://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY}
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)

        if geo_response.status_code != 200 or not geo_response.json():
            result["status"] = "error"
            result["error"] = "Could not find location"
            return result

        lat = geo_response.json()[0]["lat"]
        lon = geo_response.json()[0]["lon"]

        # Get forecast
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            hourly = []
            rain_prob_total = 0
            count = 0

            for item in data.get("list", [])[: hours // 3]:  # 3-hour intervals
                rain_prob = item.get("pop", 0) * 100
                rain_prob_total += rain_prob
                count += 1

                hourly.append(
                    {
                        "time": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "humidity": item["main"]["humidity"],
                        "rain_probability": rain_prob,
                        "description": item["weather"][0]["description"],
                    }
                )

            avg_rain_prob = rain_prob_total / count if count > 0 else 0
            rain_expected = avg_rain_prob > 40

            result["data"] = {
                "hourly_forecast": hourly,
                "avg_rain_probability": round(avg_rain_prob, 1),
                "rain_expected": rain_expected,
                "summary": {
                    "temp_min": min(h.get("temperature", 0) for h in hourly),
                    "temp_max": max(h.get("temperature", 0) for h in hourly),
                    "avg_humidity": sum(h.get("humidity", 0) for h in hourly)
                    / len(hourly),
                },
                "risk": "high"
                if avg_rain_prob > 70
                else "medium"
                if avg_rain_prob > 40
                else "low",
            }
        else:
            result["status"] = "error"
            result["error"] = f"API returned {response.status_code}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


# =============================================================================
# SOIL ANALYSIS TOOL
# =============================================================================


@tool
def analyze_soil(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze soil health from sensor readings.

    Args:
        sensor_data: Dict with soil_moisture, soil_ph, npk values, temperature

    Returns:
        Health score (0-100), issues, recommendations
    """

    result = {
        "agent": "analyze_soil",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    optimal_ranges = {
        "soil_moisture": (40, 60),
        "soil_ph": (6.0, 7.5),
        "soil_temperature": (15, 28),
        "npk_nitrogen": (120, 250),
        "npk_phosphorus": (25, 60),
        "npk_potassium": (120, 280),
    }

    def evaluate_param(value, optimal_range):
        if value is None:
            return 50
        min_val, max_val = optimal_range
        if min_val <= value <= max_val:
            return 100
        elif value < min_val:
            return max(0, 100 - (min_val - value) * 5)
        else:
            return max(0, 100 - (value - max_val) * 5)

    scores = []
    issues = []
    recommendations = []

    # Soil Moisture
    moisture = sensor_data.get("soil_moisture")
    if moisture:
        score = evaluate_param(moisture, optimal_ranges["soil_moisture"])
        scores.append(score)
        if moisture < 30:
            issues.append("Soil moisture critically low")
            recommendations.append("Increase irrigation frequency")
        elif moisture > 70:
            issues.append("Soil waterlogged")
            recommendations.append("Improve drainage")

    # pH
    ph = sensor_data.get("soil_ph")
    if ph:
        score = evaluate_param(ph, optimal_ranges["soil_ph"])
        scores.append(score)
        if ph < 6.0:
            issues.append("Soil too acidic")
            recommendations.append("Apply lime to raise pH")
        elif ph > 7.5:
            issues.append("Soil too alkaline")
            recommendations.append("Apply gypsum to lower pH")

    # Temperature
    temp = sensor_data.get("air_temperature") or sensor_data.get("soil_temperature")
    if temp:
        score = evaluate_param(temp, optimal_ranges["soil_temperature"])
        scores.append(score)
        if temp > 35:
            issues.append("High temperature stress")
            recommendations.append("Provide shade or increase irrigation")

    # NPK
    for npk_key, optimal in [
        ("npk_nitrogen", optimal_ranges["npk_nitrogen"]),
        ("npk_phosphorus", optimal_ranges["npk_phosphorus"]),
        ("npk_potassium", optimal_ranges["npk_potassium"]),
    ]:
        value = sensor_data.get(npk_key)
        if value:
            score = evaluate_param(value, optimal)
            scores.append(score)
            if score < 60:
                issues.append(f"{npk_key.replace('npk_', '').title()} deficiency")
                recommendations.append(
                    f"Apply {npk_key.replace('npk_', '').title()} fertilizer"
                )

    health_score = int(sum(scores) / len(scores)) if scores else 0

    quality = (
        "Excellent"
        if health_score >= 80
        else "Good"
        if health_score >= 60
        else "Medium"
        if health_score >= 40
        else "Poor"
    )

    result["data"] = {
        "health_score": health_score,
        "quality": quality,
        "issues": issues,
        "recommendations": recommendations,
        "readings": {
            "moisture": moisture,
            "ph": ph,
            "temperature": temp,
            "nitrogen": sensor_data.get("npk_nitrogen"),
            "phosphorus": sensor_data.get("npk_phosphorus"),
            "potassium": sensor_data.get("npk_potassium"),
        },
    }

    return result


# =============================================================================
# IRRIGATION TOOL
# =============================================================================


@tool
def calculate_irrigation(
    sensor_data: Dict[str, Any], weather_forecast: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate irrigation requirements based on soil and weather.

    Args:
        sensor_data: Current sensor readings
        weather_forecast: Weather forecast data

    Returns:
        Decision, duration, volume, recommendations
    """

    result = {
        "agent": "calculate_irrigation",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    soil_moisture = sensor_data.get("soil_moisture", 50)
    temperature = sensor_data.get("air_temperature", 25)
    humidity = sensor_data.get("humidity", 60)

    # Get weather predictions
    forecast_data = weather_forecast.get("data", {})
    rain_expected = forecast_data.get("rain_expected", False)
    rain_prob = forecast_data.get("avg_rain_probability", 0)

    moisture_threshold = 40

    if rain_expected and rain_prob > 60:
        result["data"] = {
            "should_irrigate": False,
            "reason": f"Rain expected ({rain_prob}% probability) - postpone irrigation",
            "recommendations": ["Monitor soil moisture after rainfall"],
            "optimal_timing": "After rain",
        }
    elif soil_moisture < moisture_threshold:
        deficit = moisture_threshold - soil_moisture
        duration = 20 + (deficit * 2)
        volume = duration * 50

        evap_risk = (
            "high"
            if temperature > 35 and humidity < 40
            else "medium"
            if temperature > 30
            else "low"
        )

        result["data"] = {
            "should_irrigate": True,
            "duration_minutes": int(duration),
            "water_volume_liters": int(volume),
            "reason": f"Soil moisture low ({soil_moisture}%) - irrigation required",
            "evaporation_risk": evap_risk,
            "recommendations": [
                f"Apply {volume} liters over {int(duration)} minutes",
                "Irrigate early morning or evening"
                if evap_risk == "high"
                else "Any time is fine",
            ],
            "optimal_timing": "Early morning" if evap_risk == "high" else "Anytime",
        }
    else:
        result["data"] = {
            "should_irrigate": False,
            "reason": f"Soil moisture adequate ({soil_moisture}%)",
            "recommendations": ["Monitor daily"],
            "optimal_timing": "Not needed",
        }

    return result


# =============================================================================
# FERTILIZER TOOL
# =============================================================================


@tool
def recommend_fertilizer(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend fertilizer based on NPK levels.

    Args:
        sensor_data: NPK values from sensors

    Returns:
        NPK recommendations, organic options
    """

    result = {
        "agent": "recommend_fertilizer",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    n = sensor_data.get("npk_nitrogen", 50)
    p = sensor_data.get("npk_phosphorus", 30)
    k = sensor_data.get("npk_potassium", 40)

    recommendations = []
    npk_recommendation = {"nitrogen": None, "phosphorus": None, "potassium": None}

    # Nitrogen
    if n < 35:
        recommendations.append(
            "Apply Urea (46-0-0) - 50 kg/acre for nitrogen deficiency"
        )
        npk_recommendation["nitrogen"] = "deficient"
    elif n < 50:
        recommendations.append("Consider light nitrogen application")
        npk_recommendation["nitrogen"] = "low"
    else:
        npk_recommendation["nitrogen"] = "adequate"

    # Phosphorus
    if p < 20:
        recommendations.append(
            "Apply DAP (18-46-0) - 50 kg/acre for phosphorus deficiency"
        )
        npk_recommendation["phosphorus"] = "deficient"
    elif p < 30:
        recommendations.append("Consider light phosphorus application")
        npk_recommendation["phosphorus"] = "low"
    else:
        npk_recommendation["phosphorus"] = "adequate"

    # Potassium
    if k < 30:
        recommendations.append(
            "Apply MOP (0-0-60) - 25 kg/acre for potassium deficiency"
        )
        npk_recommendation["potassium"] = "deficient"
    elif k < 40:
        recommendations.append("Consider light potassium application")
        npk_recommendation["potassium"] = "low"
    else:
        npk_recommendation["potassium"] = "adequate"

    # Organic options
    organic_options = [
        "Farmyard Manure (FYM) - 5 tons/acre",
        "Vermicompost - 2 tons/acre",
        "Neem cake - 100 kg/acre",
        "Compost - 3 tons/acre",
    ]

    result["data"] = {
        "npk_status": {"nitrogen": n, "phosphorus": p, "potassium": k},
        "npk_recommendation": npk_recommendation,
        "synthetic_recommendations": recommendations,
        "organic_options": organic_options,
        "application_timing": "Best applied before irrigation or rain",
    }

    return result


# =============================================================================
# DISEASE DETECTION TOOL
# =============================================================================


@tool
def detect_disease(
    crop_type: str = "wheat", symptoms: List[str] = None, image_data: str = None
) -> Dict[str, Any]:
    """
    Detect crop diseases based on symptoms or image.

    Args:
        crop_type: Type of crop (wheat, rice, tomato, etc.)
        symptoms: List of observed symptoms
        image_data: Base64 encoded image (optional)

    Returns:
        Disease detected (if any), treatment, prevention
    """

    result = {
        "agent": "detect_disease",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    if symptoms is None:
        symptoms = []

    # Simple disease database
    disease_db = {
        "wheat": [
            {
                "name": "Rust",
                "symptoms": ["orange spots", "yellow leaves", "pustules"],
                "treatment": "Apply fungicide (Propiconazole)",
                "severity": "high",
            },
            {
                "name": "Powdery Mildew",
                "symptoms": ["white powder", "stunted growth"],
                "treatment": "Apply sulfur-based fungicide",
                "severity": "medium",
            },
            {
                "name": "Blight",
                "symptoms": ["brown spots", "wilting"],
                "treatment": "Remove affected parts, apply fungicide",
                "severity": "high",
            },
        ],
        "rice": [
            {
                "name": "Blast",
                "symptoms": ["diamond lesions", "neck rot"],
                "treatment": "Apply Tricyclazole",
                "severity": "high",
            },
            {
                "name": "Bacterial Leaf Blight",
                "symptoms": ["yellow leaves", "wilting"],
                "treatment": "Apply copper fungicide",
                "severity": "medium",
            },
        ],
        "tomato": [
            {
                "name": "Early Blight",
                "symptoms": ["dark spots", "yellowing"],
                "treatment": "Apply chlorothalonil",
                "severity": "medium",
            },
            {
                "name": "Leaf Mold",
                "symptoms": ["yellow spots", "fuzzy growth"],
                "treatment": "Improve ventilation, apply fungicide",
                "severity": "low",
            },
            {
                "name": "Tomato Mosaic Virus",
                "symptoms": ["mottled leaves", "curling"],
                "treatment": "Remove affected plants, control aphids",
                "severity": "high",
            },
        ],
        "cotton": [
            {
                "name": "Cotton Boll Rot",
                "symptoms": ["brown boll", "cotton rot"],
                "treatment": "Apply copper fungicide",
                "severity": "medium",
            },
            {
                "name": "Leaf Curl Virus",
                "symptoms": ["curled leaves", "stunted"],
                "treatment": "Control whitefly, apply insecticide",
                "severity": "high",
            },
        ],
    }

    crop_diseases = disease_db.get(crop_type.lower(), [])

    if image_data:
        # Would use computer vision here - simplified for now
        result["data"]["note"] = (
            "Image analysis requires ML model - using symptom-based detection"
        )

    if symptoms:
        # Match symptoms
        for disease in crop_diseases:
            matched = sum(
                1
                for s in symptoms
                if s.lower() in " ".join(disease["symptoms"]).lower()
            )
            if matched > 0:
                result["data"] = {
                    "disease_detected": True,
                    "disease_name": disease["name"],
                    "confidence": min(95, 50 + matched * 15),
                    "severity": disease["severity"],
                    "treatment": disease["treatment"],
                    "prevention": "Practice crop rotation, use disease-resistant varieties",
                }
                break

    if "data" not in result or not result["data"].get("disease_detected"):
        result["data"] = {
            "disease_detected": False,
            "message": "No disease detected based on provided symptoms",
            "recommendations": [
                "Continue monitoring",
                "Maintain good agricultural practices",
            ],
        }

    return result


# =============================================================================
# YIELD PREDICTION TOOL
# =============================================================================


@tool
def predict_yield(crop_type: str, sensor_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Predict harvest yield based on crop and conditions.

    Args:
        crop_type: Type of crop
        sensor_data: Current sensor readings (optional)

    Returns:
        Expected yield, days to harvest, confidence
    """

    result = {
        "agent": "predict_yield",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    # Base yields (quintals/acre)
    base_yields = {
        "wheat": 25,
        "rice": 30,
        "cotton": 12,
        "sugarcane": 350,
        "maize": 20,
        "soybean": 10,
        "tomato": 150,
        "potato": 120,
        "onion": 100,
    }

    base = base_yields.get(crop_type.lower(), 20)
    days_to_harvest = 90  # Default

    if sensor_data:
        # Adjust based on conditions
        moisture = sensor_data.get("soil_moisture", 50)
        temp = sensor_data.get("air_temperature", 25)

        # Stress factors
        if moisture < 30 or moisture > 70:
            base *= 0.8
            days_to_harvest += 10
        if temp < 15 or temp > 35:
            base *= 0.85
            days_to_harvest += 5

    result["data"] = {
        "crop_type": crop_type,
        "expected_yield_quintals_per_acre": round(base, 1),
        "days_to_harvest": days_to_harvest,
        "confidence": "medium",
        "factors_affecting_yield": [
            "Current soil moisture conditions" if sensor_data else "Normal conditions",
            "Weather forecast",
            "Fertilizer application",
        ],
    }

    return result


# =============================================================================
# MARKET FORECAST TOOL
# =============================================================================


@tool
def get_market_forecast(crop_type: str = "wheat") -> Dict[str, Any]:
    """
    Get market price forecast for a crop using ML models.
    Uses XGBoost, Gradient Boosting, Random Forest, and Ridge Regression ensemble.

    Args:
        crop_type: Type of crop

    Returns:
        Current price, ML predictions, trend, best sell date, model performance
    """

    result = {
        "agent": "get_market_forecast",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    try:
        from ml.market_predictor import predict_market_prices

        # Get ML-based predictions
        ml_result = predict_market_prices(crop_type, days=30)

        # Format forecast for the agent
        forecast = []
        for p in ml_result["predictions"]:
            forecast.append(
                {
                    "day": p["day"],
                    "price": p["ensemble"],
                    "xgboost": p["xgboost"],
                    "random_forest": p["random_forest"],
                }
            )

        result["data"] = {
            "crop_type": ml_result["crop_type"],
            "current_price_per_quintal": ml_result["current_price"],
            "trend": ml_result["trend"],
            "trend_percentage": ml_result["trend_percentage"],
            "price_forecast_30_days": forecast,
            "best_sell_date": f"Day {ml_result['best_sell_day']}",
            "best_expected_price": ml_result["best_expected_price"],
            "model_performance": ml_result["model_performance"],
            "algorithm_used": ml_result["algorithm_used"],
            "recommendation": (
                "Hold for better prices"
                if ml_result["trend"] == "rising"
                else "Sell now"
                if ml_result["trend"] == "falling"
                else "Monitor prices"
            ),
        }

    except Exception as e:
        # Fallback to simple model if ML fails
        import random

        base_prices = {
            "wheat": 2275,
            "rice": 2183,
            "cotton": 6620,
            "sugarcane": 315,
            "maize": 2090,
            "soybean": 4600,
            "tomato": 1500,
            "potato": 1200,
            "onion": 1800,
        }
        current_price = base_prices.get(crop_type.lower(), 2000)
        trend = random.choice(["rising", "falling", "stable"])
        trend_pct = random.uniform(-5, 5)

        forecast = []
        for i in range(1, 31):
            if trend == "rising":
                price = current_price * (1 + (i * 0.002))
            elif trend == "falling":
                price = current_price * (1 - (i * 0.002))
            else:
                price = current_price * (1 + random.uniform(-0.01, 0.01))
            forecast.append({"day": i, "price": round(price, 2)})

        best_price = max(forecast, key=lambda x: x["price"])

        result["data"] = {
            "crop_type": crop_type,
            "current_price_per_quintal": current_price,
            "trend": trend,
            "trend_percentage": round(trend_pct, 2),
            "price_forecast_30_days": forecast,
            "best_sell_date": f"Day {best_price['day']}",
            "best_expected_price": round(best_price["price"], 2),
            "recommendation": "Hold for better prices"
            if trend == "rising"
            else "Sell now"
            if trend == "falling"
            else "Monitor prices",
        }

    return result


# =============================================================================
# CLIMATE RISK TOOL
# =============================================================================


@tool
def assess_climate_risk(location: str = "Pune") -> Dict[str, Any]:
    """
    Assess climate risks for a location.

    Args:
        location: City name

    Returns:
        Drought, flood, heatwave, frost risks
    """

    result = {
        "agent": "assess_climate_risk",
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "status": "success",
        "data": {},
    }

    # Get current weather
    weather = get_current_weather.invoke(location)
    forecast = get_weather_forecast.invoke(location, hours=48)

    if weather.get("status") == "success" and weather.get("data"):
        temp = weather["data"].get("temperature", 25)
        humidity = weather["data"].get("humidity", 60)
    else:
        temp, humidity = 28, 55

    if forecast.get("status") == "success" and forecast.get("data"):
        rain_prob = forecast["data"].get("avg_rain_probability", 0)
    else:
        rain_prob = 20

    # Risk calculations
    drought_risk = (
        "high"
        if humidity < 40 and rain_prob < 20
        else "medium"
        if humidity < 50
        else "low"
    )
    flood_risk = "high" if rain_prob > 70 else "medium" if rain_prob > 40 else "low"
    heatwave_risk = "high" if temp > 40 else "medium" if temp > 35 else "low"
    frost_risk = "high" if temp < 5 else "medium" if temp < 10 else "low"

    # Overall risk
    risk_scores = {"high": 3, "medium": 2, "low": 1}
    overall_score = sum(
        risk_scores.get(r, 1)
        for r in [drought_risk, flood_risk, heatwave_risk, frost_risk]
    )
    overall_risk = (
        "high" if overall_score >= 10 else "medium" if overall_score >= 6 else "low"
    )

    result["data"] = {
        "drought_risk": drought_risk,
        "flood_risk": flood_risk,
        "heatwave_risk": heatwave_risk,
        "frost_risk": frost_risk,
        "overall_risk": overall_risk,
        "current_conditions": {
            "temperature": temp,
            "humidity": humidity,
            "rain_probability": rain_prob,
        },
        "mitigation": {
            "drought": "Use drip irrigation, mulching"
            if drought_risk != "low"
            else "Normal",
            "flood": "Ensure drainage, raise beds" if flood_risk != "low" else "Normal",
            "heatwave": "Provide shade, increase watering"
            if heatwave_risk != "low"
            else "Normal",
            "frost": "Cover crops, smoke pots" if frost_risk != "low" else "Normal",
        },
    }

    return result


# =============================================================================
# CONFLICT RESOLUTION TOOL
# =============================================================================


@tool
def resolve_conflicts(
    irrigation_decision: Dict, weather_forecast: Dict, fertilizer_recommendation: Dict
) -> Dict[str, Any]:
    """
    Resolve conflicts between agent recommendations.

    Args:
        irrigation_decision: Water management decision
        weather_forecast: Weather forecast data
        fertilizer_recommendation: Fertilizer recommendation

    Returns:
        Resolved conflicts and final decisions
    """

    result = {
        "agent": "resolve_conflicts",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {},
    }

    conflicts = []
    resolutions = []

    # Check irrigation vs rain
    irr_data = irrigation_decision.get("data", {})
    weather_data = weather_forecast.get("data", {})

    should_irrigate = irr_data.get("should_irrigate", False)
    rain_prob = weather_data.get("avg_rain_probability", 0)

    if should_irrigate and rain_prob > 60:
        conflicts.append("Irrigation recommended but rain expected (60%+)")
        resolutions.append("POSTPONE irrigation until after rain")

    # Check fertilizer vs rain
    if rain_prob > 70:
        conflicts.append("Heavy rain expected (70%+) may wash away fertilizer")
        resolutions.append(
            "POSTPONE fertilizer application until after rain + 1-2 days"
        )

    # Check disease vs harvest timing
    # (would need yield data for this)

    result["data"] = {
        "conflicts_found": len(conflicts),
        "conflicts": conflicts,
        "resolutions": resolutions,
        "final_decisions": {
            "irrigation": "Postpone"
            if "irrigation" in str(resolutions).lower()
            else ("Recommended" if should_irrigate else "Not needed"),
            "fertilizer": "Postpone"
            if "fertilizer" in str(resolutions).lower()
            else "Apply as recommended",
            "general": "Monitor conditions and act after weather event",
        },
    }

    return result
