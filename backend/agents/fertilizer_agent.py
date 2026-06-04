"""
🌾 FERTILIZER & PESTICIDE AGENT
Smart fertilizer planning and eco-friendly pesticide recommendations
"""
from typing import Dict, Any, List
from datetime import datetime

class FertilizerAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Fertilizer & Pesticide Agent"
        
        # NPK requirements for different crops
        self.crop_requirements = {
            "wheat": {"N": 120, "P": 60, "K": 40},
            "rice": {"N": 150, "P": 75, "K": 75},
            "corn": {"N": 180, "P": 80, "K": 60},
            "cotton": {"N": 150, "P": 60, "K": 60}
        }
    
    def recommend_fertilizer(self, sensor_data: Dict, crop_type: str = "wheat") -> Dict[str, Any]:
        """
        Calculate fertilizer requirements based on soil NPK levels
        """
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "crop_type": crop_type,
            "recommended": False,
            "fertilizer_plan": {},
            "pesticide_plan": {},
            "eco_score": 0,
            "recommendations": []
        }
        
        # Current NPK levels
        current_n = sensor_data.get("npk_nitrogen", 0)
        current_p = sensor_data.get("npk_phosphorus", 0)
        current_k = sensor_data.get("npk_potassium", 0)
        
        # Required NPK for crop
        required = self.crop_requirements.get(crop_type, self.crop_requirements["wheat"])
        
        # Calculate deficits
        n_deficit = max(0, required["N"] - current_n)
        p_deficit = max(0, required["P"] - current_p)
        k_deficit = max(0, required["K"] - current_k)
        
        result["fertilizer_plan"] = {
            "nitrogen": {
                "current": current_n,
                "required": required["N"],
                "deficit": n_deficit,
                "application_kg_per_hectare": n_deficit * 0.5
            },
            "phosphorus": {
                "current": current_p,
                "required": required["P"],
                "deficit": p_deficit,
                "application_kg_per_hectare": p_deficit * 0.5
            },
            "potassium": {
                "current": current_k,
                "required": required["K"],
                "deficit": k_deficit,
                "application_kg_per_hectare": k_deficit * 0.5
            }
        }
        
        # Determine if fertilization is needed
        if n_deficit > 10 or p_deficit > 10 or k_deficit > 10:
            result["recommended"] = True
            result["recommendations"].append("🌱 Fertilizer application recommended")
            
            # Organic vs Chemical
            organic_option = self._recommend_organic_fertilizer(n_deficit, p_deficit, k_deficit)
            result["organic_options"] = organic_option
            
            # Application timing
            result["recommendations"].append("⏰ Apply in split doses: 50% at sowing, 30% at growth stage, 20% before flowering")
            result["recommendations"].append("💧 Ensure adequate soil moisture before application")
        else:
            result["recommended"] = False
            result["recommendations"].append("✓ Soil nutrient levels adequate")
        
        # Pesticide recommendations (eco-friendly focus)
        result["pesticide_plan"] = self._recommend_pesticides(crop_type)
        
        # Calculate eco-friendliness score
        result["eco_score"] = self._calculate_eco_score(result)
        
        return result
    
    def _recommend_organic_fertilizer(self, n_deficit: float, p_deficit: float, k_deficit: float) -> Dict:
        """Recommend organic fertilizer alternatives"""
        
        organic = {
            "options": [],
            "benefits": ["Improves soil structure", "Slow release nutrients", "Environmentally friendly"]
        }
        
        if n_deficit > 0:
            organic["options"].append({
                "nutrient": "Nitrogen",
                "source": "Compost / Farmyard Manure",
                "application_rate": f"{n_deficit * 10} kg/hectare"
            })
        
        if p_deficit > 0:
            organic["options"].append({
                "nutrient": "Phosphorus",
                "source": "Bone Meal / Rock Phosphate",
                "application_rate": f"{p_deficit * 8} kg/hectare"
            })
        
        if k_deficit > 0:
            organic["options"].append({
                "nutrient": "Potassium",
                "source": "Wood Ash / Greensand",
                "application_rate": f"{k_deficit * 6} kg/hectare"
            })
        
        return organic
    
    def _recommend_pesticides(self, crop_type: str) -> Dict:
        """Recommend eco-friendly pesticide options"""
        
        pesticide = {
            "preventive_measures": [
                "Crop rotation to break pest cycles",
                "Maintain field hygiene",
                "Use pest-resistant varieties",
                "Encourage natural predators"
            ],
            "organic_pesticides": [
                {
                    "name": "Neem Oil",
                    "target": "Aphids, whiteflies, mites",
                    "application": "Spray 2-3 ml per liter of water"
                },
                {
                    "name": "Bacillus thuringiensis (Bt)",
                    "target": "Caterpillars, larvae",
                    "application": "Apply as per manufacturer instructions"
                },
                {
                    "name": "Garlic-Chili Spray",
                    "target": "General pests",
                    "application": "Natural repellent, safe for environment"
                }
            ],
            "chemical_option": "Use only as last resort - consult agronomist"
        }
        
        return pesticide
    
    def _calculate_eco_score(self, result: Dict) -> int:
        """Calculate eco-friendliness score (0-100)"""
        
        score = 100
        
        # Penalize if heavy chemical fertilizer needed
        total_deficit = 0
        for nutrient in ["nitrogen", "phosphorus", "potassium"]:
            total_deficit += result["fertilizer_plan"][nutrient]["deficit"]
        
        if total_deficit > 100:
            score -= 20
        elif total_deficit > 50:
            score -= 10
        
        # Bonus for organic options
        if "organic_options" in result:
            score += 5
        
        return max(0, min(100, score))
