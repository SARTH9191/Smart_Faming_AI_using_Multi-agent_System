"""
🌱 SOIL AGENT - Soil Data Analysis & Health Monitoring
"""
from typing import Dict, Any
import statistics

class SoilAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Soil Health Agent"
        
        # Optimal ranges
        self.optimal_ranges = {
            'soil_moisture': (40, 60),  # %
            'soil_ph': (6.0, 7.5),
            'soil_temperature': (15, 28),  # Celsius
            'npk_nitrogen': (35, 60),  # mg/kg
            'npk_phosphorus': (20, 40),
            'npk_potassium': (30, 50)
        }
    
    def analyze_soil(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive soil analysis"""
        
        result = {
            "agent": self.name,
            "timestamp": sensor_data.get("timestamp"),
            "readings": {},
            "quality": "unknown",
            "issues": [],
            "recommendations": [],
            "health_score": 0
        }
        
        # Analyze each parameter
        scores = []
        
        # Soil Moisture
        moisture = sensor_data.get("soil_moisture", 0)
        moisture_score = self._evaluate_parameter(moisture, self.optimal_ranges['soil_moisture'])
        scores.append(moisture_score)
        result["readings"]["moisture"] = {
            "value": moisture,
            "status": self._get_status(moisture_score),
            "unit": "%"
        }
        if moisture < 30:
            result["issues"].append("Soil moisture critically low")
            result["recommendations"].append("Increase irrigation frequency")
        elif moisture > 70:
            result["issues"].append("Soil waterlogged")
            result["recommendations"].append("Improve drainage")
        
        # Soil pH
        ph = sensor_data.get("soil_ph", 7.0)
        ph_score = self._evaluate_parameter(ph, self.optimal_ranges['soil_ph'])
        scores.append(ph_score)
        result["readings"]["ph"] = {
            "value": ph,
            "status": self._get_status(ph_score),
            "unit": "pH"
        }
        if ph < 5.5:
            result["issues"].append("Soil too acidic")
            result["recommendations"].append("Apply lime to increase pH")
        elif ph > 8.0:
            result["issues"].append("Soil too alkaline")
            result["recommendations"].append("Apply sulfur to decrease pH")
        
        # NPK Analysis
        nitrogen = sensor_data.get("npk_nitrogen", 0)
        nitrogen_score = self._evaluate_parameter(nitrogen, self.optimal_ranges['npk_nitrogen'])
        scores.append(nitrogen_score)
        result["readings"]["nitrogen"] = {
            "value": nitrogen,
            "status": self._get_status(nitrogen_score),
            "unit": "mg/kg"
        }
        
        phosphorus = sensor_data.get("npk_phosphorus", 0)
        phosphorus_score = self._evaluate_parameter(phosphorus, self.optimal_ranges['npk_phosphorus'])
        scores.append(phosphorus_score)
        result["readings"]["phosphorus"] = {
            "value": phosphorus,
            "status": self._get_status(phosphorus_score),
            "unit": "mg/kg"
        }
        
        potassium = sensor_data.get("npk_potassium", 0)
        potassium_score = self._evaluate_parameter(potassium, self.optimal_ranges['npk_potassium'])
        scores.append(potassium_score)
        result["readings"]["potassium"] = {
            "value": potassium,
            "status": self._get_status(potassium_score),
            "unit": "mg/kg"
        }
        
        # Calculate overall health score
        result["health_score"] = round(statistics.mean(scores), 2)
        
        # Determine quality
        if result["health_score"] >= 80:
            result["quality"] = "excellent"
        elif result["health_score"] >= 60:
            result["quality"] = "good"
        elif result["health_score"] >= 40:
            result["quality"] = "medium"
        else:
            result["quality"] = "poor"
        
        # Trend analysis (if historical data available)
        result["trend"] = self._analyze_trend(sensor_data.get("farm_id"))
        
        return result
    
    def _evaluate_parameter(self, value: float, optimal_range: tuple) -> float:
        """Evaluate parameter against optimal range (0-100 score)"""
        min_val, max_val = optimal_range
        mid_val = (min_val + max_val) / 2
        
        if min_val <= value <= max_val:
            # Within range - score based on distance from middle
            distance_from_mid = abs(value - mid_val) / (max_val - min_val)
            return 100 - (distance_from_mid * 20)
        else:
            # Outside range - penalize based on distance
            if value < min_val:
                distance = (min_val - value) / min_val
            else:
                distance = (value - max_val) / max_val
            
            score = max(0, 60 - (distance * 100))
            return score
    
    def _get_status(self, score: float) -> str:
        """Convert score to status"""
        if score >= 80:
            return "optimal"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "critical"
    
    def _analyze_trend(self, farm_id: str) -> Dict[str, str]:
        """Analyze soil health trend over time"""
        historical = self.db.get_latest_sensor_data(farm_id, limit=10)
        
        if len(historical) < 5:
            return {"status": "insufficient_data"}
        
        # Simple trend analysis on moisture
        moistures = [h.get("soil_moisture", 0) for h in historical]
        
        if len(moistures) >= 2:
            trend = "improving" if moistures[0] > moistures[-1] else "declining"
        else:
            trend = "stable"
        
        return {
            "status": trend,
            "message": f"Soil moisture trend: {trend}"
        }
