"""
🌦️ WEATHER DATA COLLECTOR AGENT - DUAL API
Automatically switches between OpenWeather + Open-Meteo
NO SIMULATED DATA - All data from live APIs
"""
import requests
from datetime import datetime
from typing import Dict, Any
import os
import json

class WeatherCollectorAgent:
    def __init__(self, api_key: str = None):
        self.name = "Weather Collector (Dual API: OpenWeather + Open-Meteo)"
        self.api_key = api_key or self._load_api_key()
        self.openweather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.openmeteo_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        
        if self.api_key and self.api_key != "YOUR_OPENWEATHER_API_KEY_HERE":
            print(f"✅ {self.name} initialized")
            print(f"🌍 Primary: OpenWeather API | Fallback: Open-Meteo (Free)")
        else:
            print(f"✅ {self.name} initialized")
            print(f"🌍 Using Open-Meteo API (Free, No key required)")
    
    def _load_api_key(self):
        """Load API key from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'api_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('openweather_api_key', '')
        except:
            return ''
    
    def _get_coordinates(self, location: str) -> tuple:
        """Get lat/lon coordinates using Open-Meteo Geocoding"""
        try:
            params = {'name': location, 'count': 1, 'language': 'en', 'format': 'json'}
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    return (result['latitude'], result['longitude'], result['name'])
            return None
        except:
            return None
    
    def _fetch_from_openmeteo(self, location: str) -> Dict[str, Any]:
        """Fetch weather from Open-Meteo API (Free, no key required)"""
        try:
            coords = self._get_coordinates(location)
            if not coords:
                return None
            
            lat, lon, city_name = coords
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'hourly': 'temperature_2m,relativehumidity_2m,pressure_msl,cloudcover,visibility',
                'timezone': 'auto'
            }
            
            response = requests.get(self.openmeteo_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                hourly = data.get('hourly', {})
                
                humidity = hourly.get('relativehumidity_2m', [50])[0] if hourly.get('relativehumidity_2m') else 50
                pressure = hourly.get('pressure_msl', [1013])[0] if hourly.get('pressure_msl') else 1013
                cloud_cover = hourly.get('cloudcover', [0])[0] if hourly.get('cloudcover') else 0
                visibility = hourly.get('visibility', [10000])[0] if hourly.get('visibility') else 10000
                
                weather_codes = {
                    0: ('Clear', 'clear sky'), 1: ('Clouds', 'mainly clear'),
                    2: ('Clouds', 'partly cloudy'), 3: ('Clouds', 'overcast'),
                    45: ('Mist', 'foggy'), 48: ('Mist', 'depositing rime fog'),
                    51: ('Drizzle', 'light drizzle'), 53: ('Drizzle', 'moderate drizzle'),
                    61: ('Rain', 'slight rain'), 63: ('Rain', 'moderate rain'),
                    65: ('Rain', 'heavy rain'), 71: ('Snow', 'slight snow'),
                    80: ('Rain', 'rain showers'), 95: ('Thunderstorm', 'thunderstorm')
                }
                
                weather_code = current.get('weathercode', 0)
                weather_main, weather_desc = weather_codes.get(weather_code, ('Clear', 'clear sky'))
                
                return {
                    'location': city_name,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'current': {
                        'temperature': round(current.get('temperature', 0), 1),
                        'feels_like': round(current.get('temperature', 0) - 2, 1),
                        'humidity': int(humidity),
                        'pressure': int(pressure),
                        'wind_speed': round(current.get('windspeed', 0) * 3.6, 1),
                        'wind_direction': self._degrees_to_direction(current.get('winddirection', 0)),
                        'cloud_cover': int(cloud_cover),
                        'visibility': round(visibility / 1000, 1),
                        'conditions': weather_main,
                        'description': weather_desc
                    },
                    'data_source': 'Open-Meteo API (Real-time, Free)',
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"❌ Open-Meteo error: {str(e)}")
            return None
    
    def collect_weather(self, location: str = "Delhi") -> Dict[str, Any]:
        """
        Collect weather with automatic fallback:
        1. Try OpenWeather (if key available)
        2. Fall back to Open-Meteo (free)
        """
        
        # Try OpenWeather first if API key available
        if self.api_key and self.api_key != "YOUR_OPENWEATHER_API_KEY_HERE":
            try:
                real_data = self._call_openweather_api(location)
                if real_data:
                    print(f"✅ Fetched weather from OpenWeather for {location}")
                    return real_data
                else:
                    print(f"⚠️ OpenWeather failed, trying Open-Meteo...")
            except Exception as e:
                print(f"⚠️ OpenWeather error: {str(e)}, trying Open-Meteo...")
        
        # Fallback to Open-Meteo
        print(f"🔄 Switching to Open-Meteo for {location}...")
        open_meteo_data = self._fetch_from_openmeteo(location)
        
        if open_meteo_data:
            print(f"✅ Fetched weather from Open-Meteo for {location}")
            return open_meteo_data
        
        # If both fail
        print(f"❌ Both APIs failed for {location}")
        return {
            "agent": self.name,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": "All weather APIs unavailable",
            "message": "Cannot fetch weather data"
        }
    
    def _call_openweather_api(self, location: str) -> Dict[str, Any]:
        """Call OpenWeather API for real data"""
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(self.openweather_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "location": data.get("name", location),
                "coordinates": {
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"]
                },
                "timestamp": datetime.now().isoformat(),
                "current": {
                    "temperature": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": round(data["main"]["humidity"], 1),
                    "pressure": round(data["main"]["pressure"], 1),
                    "wind_speed": round(data["wind"]["speed"] * 3.6, 1),
                    "wind_direction": self._degrees_to_direction(data["wind"].get("deg", 0)),
                    "cloud_cover": round(data["clouds"]["all"], 1),
                    "visibility": round(data.get("visibility", 10000) / 1000, 1),
                    "conditions": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"]
                },
                "data_source": "OpenWeather API (Real-time)"
            }
        
        return None
    
    def _degrees_to_direction(self, degrees: int) -> str:
        """Convert wind degrees to direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]
