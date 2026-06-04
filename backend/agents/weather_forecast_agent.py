"""
🌤️ WEATHER FORECAST AGENT - 100% LIVE API
Predicts weather patterns using OpenWeather API for irrigation and farming decisions
NO SIMULATED DATA - All forecasts from live API
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

class WeatherForecastAgent:
    def __init__(self, api_key: str = None):
        self.name = "Weather Forecast Agent (100% Live API)"
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        
        if self.api_key and self.api_key != "YOUR_OPENWEATHER_API_KEY_HERE":
            print(f"✅ {self.name} initialized with OpenWeather API")
            print(f"🌍 Using 100% live forecast data - No simulations")
        else:
            print(f"⚠️ {self.name} initialized WITHOUT API key")
            print(f"❌ Weather forecasts unavailable - API key required")
    
    def _load_api_key(self):
        """Load API key from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'api_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('openweather_api_key', '')
        except:
            return ''
    
    def predict_weather(self, location: str, hours: int = 24) -> Dict[str, Any]:
        """
        Generate weather forecast from OpenWeather API
        Returns error if API unavailable (NO simulated fallback)
        """
        
        # Check if API key is available
        if not self.api_key or self.api_key == "YOUR_OPENWEATHER_API_KEY_HERE":
            return {
                "agent": self.name,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": "OpenWeather API key not configured",
                "message": "Please add your API key to api_config.json",
                "data_source": "Unavailable"
            }
        
        # Try to get real forecast from API
        try:
            real_forecast = self._call_forecast_api(location, hours)
            if real_forecast:
                return real_forecast
        except Exception as e:
            print(f"❌ OpenWeather Forecast API error: {str(e)}")
            return {
                "agent": self.name,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "message": "Unable to fetch live weather forecast",
                "data_source": "API Error"
            }
        
        # If we reach here, API returned invalid data
        return {
            "agent": self.name,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": "Invalid API response",
            "message": "OpenWeather Forecast API returned unexpected data",
            "data_source": "API Error"
        }
    
    def _call_forecast_api(self, location: str, hours: int) -> Dict[str, Any]:
        """
        Call OpenWeather Forecast API for real 5-day forecast
        """
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(40, int(hours / 3))  # API returns 3-hour intervals, max 40 items (5 days)
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            forecast_data = {
                "agent": self.name,
                "location": data["city"]["name"],
                "timestamp": datetime.now().isoformat(),
                "forecast_hours": hours,
                "hourly_forecast": [],
                "summary": {},
                "recommendations": [],
                "data_source": "OpenWeather API (Real-time)"
            }
            
            # Parse forecast list
            for item in data["list"][:min(16, int(hours / 3))]:  # Take up to requested hours
                forecast_time = datetime.fromtimestamp(item["dt"])
                
                hourly = {
                    "time": forecast_time.isoformat(),
                    "hour": int((forecast_time - datetime.now()).total_seconds() / 3600),
                    "temperature": round(item["main"]["temp"], 1),
                    "feels_like": round(item["main"]["feels_like"], 1),
                    "humidity": round(item["main"]["humidity"], 1),
                    "rain_probability": round(item.get("pop", 0) * 100, 1),  # Probability of precipitation
                    "wind_speed": round(item["wind"]["speed"] * 3.6, 1),  # m/s to km/h
                    "conditions": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "cloud_cover": item["clouds"]["all"]
                }
                
                # Check if rain volume is present
                if "rain" in item:
                    hourly["rain_volume"] = item["rain"].get("3h", 0)  # mm in last 3 hours
                
                forecast_data["hourly_forecast"].append(hourly)
            
            # Calculate summary statistics
            temps = [h["temperature"] for h in forecast_data["hourly_forecast"]]
            rain_probs = [h["rain_probability"] for h in forecast_data["hourly_forecast"]]
            
            forecast_data["summary"] = {
                "avg_temperature": round(sum(temps) / len(temps), 1),
                "max_temperature": round(max(temps), 1),
                "min_temperature": round(min(temps), 1),
                "avg_rain_probability": round(sum(rain_probs) / len(rain_probs), 1),
                "max_rain_probability": round(max(rain_probs), 1),
                "rain_expected": max(rain_probs) > 60
            }
            
            # Generate recommendations (default English, will be overridden by voice assistant)
            forecast_data["recommendations"] = self._generate_recommendations(forecast_data["summary"], "en")
            forecast_data["recommendations_multilingual"] = {
                "en": self._generate_recommendations(forecast_data["summary"], "en"),
                "hi": self._generate_recommendations(forecast_data["summary"], "hi"),
                "mr": self._generate_recommendations(forecast_data["summary"], "mr")
            }
            
            # Risk scoring
            forecast_data["risk_score"] = self._calculate_weather_risk(forecast_data["summary"])
            
            print(f"✅ Fetched real weather forecast for {location}")
            return forecast_data
        else:
            print(f"⚠️ OpenWeather Forecast API returned status {response.status_code}")
            return None
    
    def get_extended_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
        """
        Get extended weather forecast (wrapper for predict_weather)
        OpenWeather free tier provides 5-day forecast
        """
        if not self.api_key or self.api_key == "YOUR_OPENWEATHER_API_KEY_HERE":
            return {
                "status": "error",
                "error": "API key required for extended forecasts",
                "message": "Configure OpenWeather API key in api_config.json"
            }
        
        # Convert days to hours (max 5 days = 120 hours for free tier)
        hours = min(days * 24, 120)
        return self.predict_weather(location, hours)
    
    def _generate_recommendations(self, summary: Dict, language: str = "en") -> List[str]:
        """Generate farming recommendations based on forecast in multiple languages"""
        recommendations = []
        
        # Multilingual recommendations
        if summary["rain_expected"]:
            if language == "hi":
                recommendations.append("⛈️ बारिश की उम्मीद है - सिंचाई और उर्वरक का उपयोग स्थगित करें")
                recommendations.append("🌾 जल निकासी प्रणाली तैयार करें")
            elif language == "mr":
                recommendations.append("⛈️ पाऊस अपेक्षित आहे - सिंचन आणि खत वापर पुढे ढकला")
                recommendations.append("🌾 जलनिर्गमन प्रणाली तयार करा")
            else:
                recommendations.append("⛈️ Rain expected - postpone irrigation and fertilizer application")
                recommendations.append("🌾 Prepare drainage systems")
        else:
            if language == "hi":
                recommendations.append("☀️ कोई महत्वपूर्ण बारिश नहीं - सिंचाई कार्यक्रम की योजना बनाएं")
            elif language == "mr":
                recommendations.append("☀️ लक्षणीय पाऊस नाही - सिंचन वेळापत्रक नियोजित करा")
            else:
                recommendations.append("☀️ No significant rain - plan irrigation schedule")
        
        if summary["max_temperature"] > 35:
            if language == "hi":
                recommendations.append("🌡️ गर्मी की लहर चेतावनी - सिंचाई की आवृत्ति बढ़ाएं")
            elif language == "mr":
                recommendations.append("🌡️ उष्णतेची लहर इशारा - सिंचन वारंवारता वाढवा")
            else:
                recommendations.append("🌡️ Heat wave warning - increase irrigation frequency")
        
        if summary["avg_rain_probability"] < 20:
            if language == "hi":
                recommendations.append("🏜️ सूखे का अनुमान - पर्याप्त जल भंडार सुनिश्चित करें")
            elif language == "mr":
                recommendations.append("🏜️ कोरडेपणाचा अंदाज - पुरेसा पाणी साठा सुनिश्चित करा")
            else:
                recommendations.append("🏜️ Dry spell predicted - ensure adequate water reserves")
        
        return recommendations
    
    def _calculate_weather_risk(self, summary: Dict) -> Dict[str, Any]:
        """Calculate weather-related risks"""
        risk_score = 0
        risk_factors = []
        
        # High temperature risk
        if summary["max_temperature"] > 38:
            risk_score += 30
            risk_factors.append("extreme_heat")
        
        # Heavy rain risk
        if summary["max_rain_probability"] > 80:
            risk_score += 25
            risk_factors.append("heavy_rain")
        
        # Drought risk
        if summary["avg_rain_probability"] < 10:
            risk_score += 20
            risk_factors.append("drought")
        
        risk_level = "low"
        if risk_score > 50:
            risk_level = "high"
        elif risk_score > 25:
            risk_level = "medium"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "factors": risk_factors
        }
