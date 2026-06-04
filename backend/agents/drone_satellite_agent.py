"""
🛰️ DRONE & SATELLITE AGENT
Real-time satellite climate data via NASA POWER API + simulated drone imaging
"""
from typing import Dict, Any
import random
from datetime import datetime, timedelta
import requests

class DroneSatelliteAgent:
    def __init__(self):
        self.name = "Drone & Satellite Agent"
        self.nasa_power_api = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # Default location: Pune, Maharashtra (can be customized per farm)
        self.default_location = {
            "latitude": 18.5204,
            "longitude": 73.8567,
            "city": "Pune"
        }
    
    def analyze_farm(self, farm_id: str, latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        """
        Analyze farm using real NASA satellite data + simulated drone imaging
        
        Args:
            farm_id: Farm identifier
            latitude: Farm latitude (defaults to Pune)
            longitude: Farm longitude (defaults to Pune)
        """
        
        # Use default location if not provided
        if latitude is None:
            latitude = self.default_location["latitude"]
        if longitude is None:
            longitude = self.default_location["longitude"]
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "farm_id": farm_id,
            "location": {"latitude": latitude, "longitude": longitude},
            "drone_analysis": {},
            "satellite_analysis": {},
            "soil_health_map": {},
            "recommendations": [],
            "data_source": "NASA POWER API + Simulated Drone"
        }
        
        # Drone Analysis (High-resolution field analysis - simulated)
        result["drone_analysis"] = self._simulate_drone_scan(farm_id)
        
        # Satellite Analysis (Real NASA POWER API data)
        result["satellite_analysis"] = self._get_real_satellite_data(latitude, longitude)
        
        # Soil Health Mapping (simulated from drone data)
        result["soil_health_map"] = self._generate_soil_health_map(farm_id)
        
        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(result)
        
        return result
    
    def _simulate_drone_scan(self, farm_id: str) -> Dict[str, Any]:
        """Simulate drone field scanning"""
        
        # Simulate NDVI (Normalized Difference Vegetation Index)
        ndvi_avg = round(random.uniform(0.5, 0.9), 2)
        
        # Simulate crop health zones
        zones = []
        zone_count = random.randint(3, 6)
        
        for i in range(zone_count):
            zones.append({
                "zone_id": f"Z{i+1}",
                "area_percentage": round(random.uniform(10, 30), 1),
                "health_status": random.choice(["Excellent", "Good", "Fair", "Poor"]),
                "ndvi_value": round(random.uniform(0.4, 0.95), 2),
                "issue": random.choice(["None", "Low moisture", "Nutrient deficiency", "Pest damage"])
            })
        
        return {
            "scan_date": datetime.now().isoformat(),
            "altitude": "120 meters",
            "resolution": "5 cm/pixel",
            "area_covered": "10 hectares",
            "ndvi_average": ndvi_avg,
            "crop_health": "Good" if ndvi_avg > 0.6 else "Fair",
            "zones": zones,
            "anomalies_detected": random.randint(0, 3)
        }
    
    def _simulate_satellite_data(self, farm_id: str) -> Dict[str, Any]:
        """Fallback: Simulate satellite climate prediction if API fails"""
        
        return {
            "satellite": "Simulated Data (Fallback)",
            "last_pass": datetime.now().isoformat(),
            "cloud_cover": round(random.uniform(10, 40), 1),
            "temperature_trend": {
                "current": round(random.uniform(25, 35), 1),
                "7_day_forecast": round(random.uniform(26, 36), 1),
                "trend": random.choice(["rising", "stable", "falling"])
            },
            "precipitation_forecast": {
                "next_7_days": round(random.uniform(0, 50), 1),
                "probability": round(random.uniform(20, 80), 1)
            },
            "vegetation_index": {
                "evi": round(random.uniform(0.3, 0.7), 2),
                "status": "Healthy vegetation"
            },
            "soil_moisture_estimation": {
                "surface_moisture": round(random.uniform(30, 60), 1),
                "status": "Adequate"
            },
            "data_source": "simulated"
        }
    
    def _get_real_satellite_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get REAL satellite data from NASA POWER API"""
        
        try:
            # Get last 7 days of data (use 2024 data since we're in simulation)
            end_date = datetime(2024, 12, 31)  # Use recent historical data
            start_date = end_date - timedelta(days=7)
            
            # NASA POWER API parameters
            params = {
                "parameters": "T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN",  # Temperature, Precipitation, Humidity, Wind, Solar
                "community": "AG",  # Agriculture community
                "longitude": longitude,
                "latitude": latitude,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON"
            }
            
            # Make API request
            print(f"🛰️ Fetching NASA POWER data for {latitude}, {longitude}...")
            response = requests.get(self.nasa_power_api, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for errors in response
                if data.get("messages"):
                    print(f"NASA API Messages: {data.get('messages')}")
                
                parameters = data.get("properties", {}).get("parameter", {})
                
                if not parameters:
                    print("⚠️ No parameter data from NASA API, using fallback")
                    return self._simulate_satellite_data("DEMO")
                
                # Extract temperature data
                temps = list(parameters.get("T2M", {}).values())
                current_temp = temps[-1] if temps else 28.0
                avg_temp_7day = sum(temps) / len(temps) if temps else 28.0
                
                # Extract precipitation data
                precip = list(parameters.get("PRECTOTCORR", {}).values())
                total_precip_7days = sum(precip) if precip else 0
                
                # Extract humidity
                humidity = list(parameters.get("RH2M", {}).values())
                current_humidity = humidity[-1] if humidity else 60.0
                
                # Extract solar radiation
                solar = list(parameters.get("ALLSKY_SFC_SW_DWN", {}).values())
                avg_solar = sum(solar) / len(solar) if solar else 5.5
                
                # Determine trend
                if len(temps) >= 3:
                    recent_trend = temps[-1] - temps[-3]
                    trend = "rising" if recent_trend > 1 else "falling" if recent_trend < -1 else "stable"
                else:
                    trend = "stable"
                
                # Calculate soil moisture estimation (based on precip and humidity)
                soil_moisture = min(100, (current_humidity * 0.6) + (total_precip_7days * 2))
                moisture_status = "Adequate" if soil_moisture > 40 else "Low"
                
                print(f"✅ NASA POWER data retrieved successfully")
                return {
                    "satellite": "NASA POWER (REAL DATA)",
                    "data_source": "https://power.larc.nasa.gov",
                    "last_updated": datetime.now().isoformat(),
                    "location": f"{latitude}°N, {longitude}°E",
                    "temperature_trend": {
                        "current": round(current_temp, 1),
                        "7_day_average": round(avg_temp_7day, 1),
                        "trend": trend
                    },
                    "precipitation": {
                        "last_7_days_mm": round(total_precip_7days, 1),
                        "daily_average": round(total_precip_7days / 7, 2)
                    },
                    "humidity": {
                        "current": round(current_humidity, 1),
                        "status": "High" if current_humidity > 70 else "Moderate" if current_humidity > 50 else "Low"
                    },
                    "solar_radiation": {
                        "average_kWh_m2_day": round(avg_solar, 2),
                        "status": "Excellent" if avg_solar > 6 else "Good" if avg_solar > 4 else "Fair"
                    },
                    "soil_moisture_estimation": {
                        "estimated_percentage": round(soil_moisture, 1),
                        "status": moisture_status
                    },
                    "api_status": "✅ Live Data"
                }
            
            else:
                # API failed, use fallback
                print(f"NASA POWER API error: {response.status_code}")
                return self._simulate_satellite_data("fallback")
        
        except Exception as e:
            # Network error or API issue
            print(f"NASA POWER API exception: {str(e)}")
            return self._simulate_satellite_data("fallback")
    
    
    def _generate_soil_health_map(self, farm_id: str) -> Dict[str, Any]:
        """Generate soil health map from aerial data"""
        
        # Simulate soil health grid (10x10)
        grid = []
        
        for row in range(5):
            row_data = []
            for col in range(5):
                cell_health = round(random.uniform(40, 100), 1)
                row_data.append({
                    "position": f"R{row}C{col}",
                    "health_score": cell_health,
                    "status": "Good" if cell_health > 70 else "Fair" if cell_health > 50 else "Poor"
                })
            grid.append(row_data)
        
        # Calculate statistics
        all_scores = [cell["health_score"] for row in grid for cell in row]
        avg_health = sum(all_scores) / len(all_scores)
        
        return {
            "resolution": "5m x 5m cells",
            "grid_size": "5x5",
            "average_health": round(avg_health, 1),
            "grid_data": grid,
            "problem_areas": [
                cell["position"] for row in grid for cell in row if cell["health_score"] < 60
            ]
        }
    
    def _generate_recommendations(self, result: Dict) -> list:
        """Generate recommendations from drone/satellite analysis"""
        
        recommendations = []
        
        # Drone-based recommendations
        drone_data = result["drone_analysis"]
        if drone_data["ndvi_average"] < 0.6:
            recommendations.append("📉 Low vegetation index - check for stress factors")
        
        if drone_data["anomalies_detected"] > 0:
            recommendations.append(f"⚠️ {drone_data['anomalies_detected']} anomalies detected - investigate affected areas")
        
        # Check zones
        poor_zones = [z for z in drone_data["zones"] if z["health_status"] == "Poor"]
        if poor_zones:
            recommendations.append(f"🎯 Focus attention on zones: {', '.join([z['zone_id'] for z in poor_zones])}")
        
        # Satellite-based recommendations
        sat_data = result["satellite_analysis"]
        
        # Check if using real or simulated data
        is_real_data = sat_data.get("api_status") == "✅ Live Data"
        
        if is_real_data:
            # Recommendations based on real NASA data
            if "precipitation" in sat_data and sat_data["precipitation"]["last_7_days_mm"] > 50:
                recommendations.append("🌧️ Heavy rainfall detected (50+ mm) - monitor for waterlogging")
            elif "precipitation" in sat_data and sat_data["precipitation"]["last_7_days_mm"] < 5:
                recommendations.append("☀️ Low rainfall (< 5mm) - irrigation recommended")
            
            if "temperature_trend" in sat_data:
                if sat_data["temperature_trend"]["trend"] == "rising":
                    recommendations.append("🌡️ Temperature rising - ensure adequate irrigation")
                elif sat_data["temperature_trend"]["current"] > 35:
                    recommendations.append("🔥 High temperature (>35°C) - protect crops from heat stress")
            
            if "soil_moisture_estimation" in sat_data:
                if sat_data["soil_moisture_estimation"]["status"] == "Low":
                    recommendations.append("💧 Low soil moisture detected - urgent irrigation needed")
            
            if "humidity" in sat_data and sat_data["humidity"]["status"] == "High":
                recommendations.append("🌫️ High humidity - monitor for fungal diseases")
        
        else:
            # Recommendations based on simulated data (fallback)
            if sat_data.get("precipitation_forecast", {}).get("probability", 0) > 70:
                recommendations.append("🌧️ High rain probability - postpone spraying operations")
            
            if sat_data.get("temperature_trend", {}).get("trend") == "rising":
                recommendations.append("🌡️ Temperature rising - ensure adequate irrigation")
        
        # Soil health map recommendations
        soil_map = result["soil_health_map"]
        if soil_map["problem_areas"]:
            recommendations.append(f"🗺️ Soil health issues in {len(soil_map['problem_areas'])} areas - targeted intervention needed")
        
        return recommendations
