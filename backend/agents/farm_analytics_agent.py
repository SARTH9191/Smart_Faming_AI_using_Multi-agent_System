"""
🧠 FARM ANALYTICS AGENT - The Action Autopilot
==============================================
Calculates comprehensive farm health scores, predictive yield trends,
cost optimizations, anomaly detection, regional benchmarking, and AI crop rotation.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class FarmAnalyticsAgent:
    def __init__(self, db):
        self.db = db
        self.name = "Farm Analytics & Strategy Engine"

    def calculate_health_score(self, current_sensors: Dict[str, Any], crop_type: str) -> Dict[str, Any]:
        """Calculates a 0-100 score based on NPK, pH, moisture, and climate risk"""
        score = 100.0
        factors = []
        
        # Soil Moisture
        moisture = current_sensors.get("soil_moisture", 50)
        if moisture < 30 or moisture > 80:
            score -= 15
            factors.append("Sub-optimal soil moisture")
            
        # pH Level
        ph = current_sensors.get("soil_ph", 7.0)
        if ph < 6.0 or ph > 7.5:
            score -= 10
            factors.append("Soil pH out of optimal bounds")
            
        # NPK Levels (Rough estimation for generic crop)
        n, p, k = current_sensors.get("npk_nitrogen", 50), current_sensors.get("npk_phosphorus", 50), current_sensors.get("npk_potassium", 50)
        if n < 40:
            score -= 10
            factors.append("Low Nitrogen")
        if p < 20: 
            score -= 5
            factors.append("Low Phosphorus")
        if k < 30:
            score -= 5
            factors.append("Low Potassium")

        # Temperature
        temp = current_sensors.get("air_temperature", 25)
        if temp > 38:
            score -= 10
            factors.append("Heat stress")
            
        score = max(0.0, score)
        return {
            "score": round(score, 1),
            "grade": "A" if score > 90 else "B" if score > 75 else "C" if score > 60 else "D",
            "trend": "improving" if score > 70 else "declining",
            "factors": factors if factors else ["All parameters optimal"]
        }

    def predict_yield_trends(self, crop_type: str, area_hectares: float, health_score: float) -> Dict[str, Any]:
        """Predicts harvest with confidence intervals based on health score."""
        # Base generic yield: 3 tons per hectare
        base_yield = 3000 * area_hectares
        
        # Adjust by health score (100 = 120% yield, 50 = 80% yield)
        health_multiplier = 0.8 + (health_score / 100.0) * 0.4
        expected_yield_kg = base_yield * health_multiplier
        
        # Confidence interval is wider if health is poor
        variance = 0.1 if health_score > 80 else 0.25
        margin_error = expected_yield_kg * variance
        
        return {
            "predicted_yield_kg": round(expected_yield_kg, 2),
            "margin_of_error_kg": round(margin_error, 2),
            "confidence_percentage": round(100 - (variance * 100)),
            "unit": "kg",
            "message": f"{round(expected_yield_kg)} kg ± {round(margin_error)} kg ({round(100-(variance*100))}% confidence)"
        }

    def analyze_costs(self, crop_type: str, area_hectares: float) -> Dict[str, Any]:
        """Analyzes expenses and suggests cost savings."""
        base_cost_per_ha = 25000  # Generic INR cost per hectare
        total_estimated_cost = base_cost_per_ha * area_hectares
        
        suggestions = [
            {"strategy": "Organic Fertilizer Switch", "savings_pct": random.uniform(10, 20), "message": "Use organic fertilizer from local compost to save up to 20% on inputs."},
            {"strategy": "Precision Irrigation", "savings_pct": random.uniform(5, 15), "message": "Deploy drip irrigation to reduce water and pumping electricity costs."}
        ]
        
        return {
            "estimated_current_cost_inr": round(total_estimated_cost, 2),
            "optimization_suggestions": suggestions
        }

    def detect_anomalies(self, current_sensors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Guard-Dog agent for instant sensor deviations"""
        anomalies = []
        if current_sensors.get("soil_moisture", 50) < 20:
            anomalies.append({"type": "critical", "message": "⚠️ Soil moisture critically low. Potential irrigation leak or failure."})
        if current_sensors.get("air_temperature", 25) > 42:
            anomalies.append({"type": "high", "message": "🔥 Extreme heat detected. Risk of crop wilting."})
        if current_sensors.get("humidity", 50) > 90 and current_sensors.get("air_temperature", 25) > 25:
            anomalies.append({"type": "medium", "message": "🦠 High humidity and temp. High risk for fungal disease."})
        return anomalies

    def crop_rotation_strategy(self, current_crop: str) -> Dict[str, Any]:
        """Suggests next crop based on simple nitrogen rotation heuristics"""
        legumes = ["Soybean", "Lentils", "Peas", "Chickpeas"]
        heavy_feeders = ["Wheat", "Corn", "Rice", "Sugarcane"]
        
        if current_crop.title() in heavy_feeders:
            next_crop = random.choice(legumes)
            reason = "Replenishes soil nitrogen depleted by heavy feeders."
        else:
            next_crop = random.choice(heavy_feeders)
            reason = "Utilizes nitrogen fixed by previous legume crop."
            
        return {
            "suggested_next_crop": next_crop,
            "reasoning": reason,
            "message": f"Plant {next_crop} next season - {reason.lower()}"
        }

    def regional_benchmarking(self, state: str, health_score: float) -> str:
        """Simulates comparing the farm against regional averages."""
        if health_score > 85:
            return f"You are in the Top 10% in {state or 'your region'}."
        elif health_score > 70:
            return f"You are in the Top 25% in {state or 'your region'}."
        elif health_score > 50:
            return f"You are exactly average for {state or 'your region'}."
        else:
            return f"Your farm metrics are trailing behind the {state or 'your region'} average."

    async def generate_full_report(self, farm_id: str, profile: Dict = None, crop_type: str = None) -> Dict[str, Any]:
        """Compiles all analytics into a single rich response"""
        try:
            readings = await self.db.get_latest_readings(farm_id, limit=1)
            current_sensors = readings[0] if readings else {}
            
            # Fetch crops from DB directly
            db_crops = await self.db.get_crops(farm_id)
            
            # --- Multi-Crop and Acre Conversions ---
            available_crops = []
            
            if db_crops:
                for c in db_crops:
                    if c.get("crop_type"):
                        normalized_name = c["crop_type"].title()
                        if normalized_name not in available_crops:
                            available_crops.append(normalized_name)
                            
            if not available_crops:
                available_crops = ["Wheat"]
                
            current_crop = (crop_type.title() if crop_type else available_crops[0])
            if current_crop not in available_crops:
                available_crops.insert(0, current_crop)

            # Determine area_hectares matching the selected crop
            matching_crop = next((c for c in db_crops if c.get("crop_type", "").title() == current_crop), None)
            if matching_crop and matching_crop.get("area_hectares"):
                area_hectares = float(matching_crop["area_hectares"])
            else:
                acres = profile.get("total_land_area_acres") if profile else None
                area_hectares = float(acres) * 0.404686 if acres and float(acres) > 0 else 1.0

            state = profile.get("location", "Maharashtra") if profile else "Maharashtra"
            # ---------------------------------------
            
            health = self.calculate_health_score(current_sensors, current_crop)
            yield_pred = self.predict_yield_trends(current_crop.lower(), area_hectares, health["score"])
            costs = self.analyze_costs(current_crop.lower(), area_hectares)
            anomalies = self.detect_anomalies(current_sensors)
            rotation = self.crop_rotation_strategy(current_crop.lower())
            benchmark = self.regional_benchmarking(state, health["score"])
            
            return {
                "health_score": health,
                "yield_prediction": yield_pred,
                "cost_optimization": costs,
                "anomalies": anomalies,
                "crop_rotation": rotation,
                "benchmarking": benchmark,
                "available_crops": available_crops,
                "selected_crop": current_crop,
                "farm_area_hectares": round(area_hectares, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
