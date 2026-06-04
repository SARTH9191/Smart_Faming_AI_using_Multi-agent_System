"""
🌍 SUSTAINABILITY AGENT
Monitors carbon/water footprint and awards Green Tokens
"""
from typing import Dict, Any, List
from datetime import datetime

class SustainabilityAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Sustainability Agent"
    
    def calculate_sustainability_score(self, farm_id: str) -> Dict[str, Any]:
        """Calculate overall sustainability score for the farm"""
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "farm_id": farm_id,
            "sustainability_score": 0,
            "carbon_footprint": {},
            "water_footprint": {},
            "eco_practices": [],
            "improvement_areas": [],
            "recommendations": []
        }
        
        # Get recent actions
        actions = self.db.get_actions_log(farm_id, limit=30)
        
        # Calculate carbon footprint
        result["carbon_footprint"] = self._calculate_carbon_footprint(actions)
        
        # Calculate water footprint
        result["water_footprint"] = self._calculate_water_footprint(actions)
        
        # Identify eco-friendly practices
        result["eco_practices"] = self._identify_eco_practices(actions)
        
        # Calculate overall score (0-100)
        carbon_score = result["carbon_footprint"].get("score", 50)
        water_score = result["water_footprint"].get("score", 50)
        practice_score = len(result["eco_practices"]) * 5
        
        result["sustainability_score"] = min(100, int((carbon_score + water_score + practice_score) / 3))
        
        # Generate recommendations
        result["recommendations"] = self._generate_sustainability_recommendations(result)
        
        # Identify improvement areas
        if carbon_score < 60:
            result["improvement_areas"].append("Reduce carbon emissions")
        if water_score < 60:
            result["improvement_areas"].append("Improve water efficiency")
        if len(result["eco_practices"]) < 3:
            result["improvement_areas"].append("Adopt more eco-friendly practices")
        
        return result
    
    def _calculate_carbon_footprint(self, actions: List[Dict]) -> Dict[str, Any]:
        """Calculate carbon footprint from farm activities"""
        
        total_emissions = 0  # kg CO2
        
        # Emission factors (simplified)
        emission_factors = {
            "fertilizer": 5.0,  # kg CO2 per application
            "pesticide": 3.0,
            "irrigation": 1.5,
            "tilling": 4.0,
            "transport": 2.0
        }
        
        for action in actions:
            action_type = action.get("action_type", "")
            for activity, factor in emission_factors.items():
                if activity in action_type.lower():
                    total_emissions += factor
        
        # Calculate score (lower emissions = higher score)
        max_expected = 200  # kg CO2
        score = max(0, 100 - (total_emissions / max_expected * 100))
        
        return {
            "total_kg_co2": round(total_emissions, 2),
            "score": round(score, 1),
            "rating": self._get_rating(score),
            "offset_needed": round(total_emissions * 0.1, 2)  # trees needed
        }
    
    def _calculate_water_footprint(self, actions: List[Dict]) -> Dict[str, Any]:
        """Calculate water usage efficiency"""
        
        total_water_used = 0  # liters
        
        for action in actions:
            if "irrigation" in action.get("action_type", "").lower():
                # Extract water usage from action details (simplified)
                total_water_used += 1500  # average per irrigation event
        
        # Calculate efficiency score
        optimal_usage = len([a for a in actions if "irrigation" in a.get("action_type", "").lower()]) * 1200
        if optimal_usage > 0:
            efficiency = (optimal_usage / total_water_used) * 100 if total_water_used > 0 else 100
        else:
            efficiency = 100
        
        score = min(100, efficiency)
        
        return {
            "total_liters": total_water_used,
            "efficiency_score": round(score, 1),
            "rating": self._get_rating(score),
            "water_saved": max(0, total_water_used - optimal_usage)
        }
    
    def _identify_eco_practices(self, actions: List[Dict]) -> List[Dict]:
        """Identify eco-friendly practices being followed"""
        
        eco_practices = []
        
        eco_keywords = {
            "organic": {"name": "Organic Farming", "impact": "High", "tokens": 15},
            "drip": {"name": "Drip Irrigation", "impact": "High", "tokens": 20},
            "compost": {"name": "Composting", "impact": "Medium", "tokens": 15},
            "mulch": {"name": "Mulching", "impact": "Medium", "tokens": 10},
            "rotation": {"name": "Crop Rotation", "impact": "Medium", "tokens": 12},
            "rainwater": {"name": "Rainwater Harvesting", "impact": "High", "tokens": 25}
        }
        
        for action in actions:
            action_text = (action.get("action_type", "") + " " + action.get("action_details", "")).lower()
            for keyword, details in eco_keywords.items():
                if keyword in action_text and details["name"] not in [p["name"] for p in eco_practices]:
                    eco_practices.append(details)
        
        return eco_practices
    
    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_sustainability_recommendations(self, result: Dict) -> List[str]:
        """Generate sustainability recommendations"""
        
        recommendations = []
        
        score = result["sustainability_score"]
        
        if score < 60:
            recommendations.append("🌱 Consider switching to organic fertilizers")
            recommendations.append("💧 Install drip irrigation to reduce water waste")
        
        if result["carbon_footprint"]["score"] < 60:
            recommendations.append("🌳 Plant trees to offset carbon emissions")
            recommendations.append("♻️ Adopt zero-tillage farming methods")
        
        if result["water_footprint"]["efficiency_score"] < 60:
            recommendations.append("💧 Implement rainwater harvesting")
            recommendations.append("⏰ Irrigate during early morning or evening")
        
        if len(result["eco_practices"]) < 3:
            recommendations.append("🔄 Practice crop rotation")
            recommendations.append("🌾 Use mulching to retain soil moisture")
        
        return recommendations
