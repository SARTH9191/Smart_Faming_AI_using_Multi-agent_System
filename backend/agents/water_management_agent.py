"""
💧 WATER MANAGEMENT AGENT
Smart irrigation scheduling and water optimization
"""
from typing import Dict, Any
from datetime import datetime

class WaterManagementAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Water Management Agent"
    
    def calculate_irrigation_need(self, sensor_data: Dict, weather_forecast: Dict) -> Dict[str, Any]:
        """
        Calculate irrigation requirements based on soil moisture, weather, and evaporation
        """
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "should_irrigate": False,
            "duration_minutes": 0,
            "water_volume_liters": 0,
            "reason": "",
            "recommendations": []
        }
        
        # Get sensor readings
        soil_moisture = sensor_data.get("soil_moisture", 50)
        air_temperature = sensor_data.get("air_temperature", 25)
        humidity = sensor_data.get("humidity", 60)
        
        # Get weather predictions
        rain_expected = weather_forecast.get("summary", {}).get("rain_expected", False)
        rain_probability = weather_forecast.get("summary", {}).get("avg_rain_probability", 0)
        
        # Decision logic
        moisture_threshold = 40  # %
        
        if rain_expected and rain_probability > 60:
            result["should_irrigate"] = False
            result["reason"] = f"Rain expected ({rain_probability}% probability) - irrigation postponed"
            result["recommendations"].append("Monitor soil moisture after rainfall")
        
        elif soil_moisture < moisture_threshold:
            result["should_irrigate"] = True
            
            # Calculate irrigation duration based on deficit
            moisture_deficit = moisture_threshold - soil_moisture
            base_duration = 20  # minutes
            duration = base_duration + (moisture_deficit * 2)
            
            result["duration_minutes"] = int(duration)
            result["water_volume_liters"] = int(duration * 50)  # 50 L/min average flow
            result["reason"] = f"Soil moisture low ({soil_moisture}%) - irrigation required"
            
            # Evaporation risk
            evap_risk = self._calculate_evaporation_risk(air_temperature, humidity)
            result["evaporation_risk"] = evap_risk
            
            if evap_risk == "high":
                result["recommendations"].append("⏰ Irrigate early morning or evening to reduce evaporation")
            
            result["recommendations"].append(f"💧 Apply {result['water_volume_liters']} liters over {result['duration_minutes']} minutes")
        
        else:
            result["should_irrigate"] = False
            result["reason"] = f"Soil moisture adequate ({soil_moisture}%)"
            result["recommendations"].append("✓ No irrigation needed - monitor daily")
        
        # Schedule optimization
        result["optimal_schedule"] = self._generate_irrigation_schedule(sensor_data, weather_forecast)
        
        return result
    
    def _calculate_evaporation_risk(self, temperature: float, humidity: float) -> str:
        """Calculate evaporation risk level"""
        
        # High temp + low humidity = high evaporation
        if temperature > 35 and humidity < 40:
            return "high"
        elif temperature > 30 and humidity < 50:
            return "medium"
        else:
            return "low"
    
    def _generate_irrigation_schedule(self, sensor_data: Dict, weather_forecast: Dict) -> Dict[str, Any]:
        """Generate week-long irrigation schedule"""
        
        schedule = {
            "next_7_days": [],
            "total_water_needed": 0,
            "frequency": "every_2_days"
        }
        
        # Simple scheduling logic
        days = ["Monday", "Wednesday", "Friday", "Sunday"]
        
        for day in days:
            schedule["next_7_days"].append({
                "day": day,
                "recommended_time": "06:00 AM",
                "duration_minutes": 30,
                "water_liters": 1500
            })
        
        schedule["total_water_needed"] = len(days) * 1500
        
        return schedule
