"""
📊 CROP YIELD PREDICTION AGENT
Predicts expected crop yield and harvest dates
"""
from typing import Dict, Any
from datetime import datetime, timedelta
import random

class YieldPredictionAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Yield Prediction Agent"
        
        # Average yields (tons per hectare)
        self.baseline_yields = {
            "wheat": 4.5,
            "rice": 5.0,
            "corn": 6.0,
            "cotton": 2.5,
            "sugarcane": 70.0
        }
        
        # Growth durations (days)
        self.growth_durations = {
            "wheat": 120,
            "rice": 150,
            "corn": 100,
            "cotton": 180,
            "sugarcane": 365
        }
    
    def predict_yield(self, crop_type: str, area_hectares: float, 
                     soil_quality: str = "medium", planted_date: str = None) -> Dict[str, Any]:
        """
        Predict crop yield based on multiple factors
        """
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "crop_type": crop_type,
            "area_hectares": area_hectares,
            "soil_quality": soil_quality,
            "expected_yield_tons": 0,
            "yield_per_hectare": 0,
            "harvest_date": None,
            "confidence": 0,
            "factors": {},
            "recommendations": []
        }
        
        # Get baseline yield
        baseline = self.baseline_yields.get(crop_type, 3.0)
        
        # Apply quality modifiers
        quality_multipliers = {
            "excellent": 1.2,
            "good": 1.1,
            "medium": 1.0,
            "poor": 0.7
        }
        
        quality_mult = quality_multipliers.get(soil_quality, 1.0)
        
        # Weather impact (simulated)
        weather_impact = random.uniform(0.9, 1.1)
        
        # Disease impact (simulated)
        disease_impact = random.uniform(0.95, 1.0)
        
        # Calculate final yield
        yield_per_hectare = baseline * quality_mult * weather_impact * disease_impact
        total_yield = yield_per_hectare * area_hectares
        
        result["yield_per_hectare"] = round(yield_per_hectare, 2)
        result["expected_yield_tons"] = round(total_yield, 2)
        
        # Confidence calculation
        confidence = 70 + (quality_mult - 1) * 20
        result["confidence"] = round(min(95, max(60, confidence)), 1)
        
        # Calculate harvest date
        if not planted_date:
            planted_date = datetime.now() - timedelta(days=30)
        else:
            planted_date = datetime.fromisoformat(planted_date)
        
        growth_days = self.growth_durations.get(crop_type, 120)
        harvest_date = planted_date + timedelta(days=growth_days)
        result["harvest_date"] = harvest_date.strftime("%Y-%m-%d")
        
        days_to_harvest = (harvest_date - datetime.now()).days
        result["days_to_harvest"] = max(0, days_to_harvest)
        
        # Factor breakdown
        result["factors"] = {
            "soil_quality_impact": f"{(quality_mult - 1) * 100:+.1f}%",
            "weather_impact": f"{(weather_impact - 1) * 100:+.1f}%",
            "disease_impact": f"{(disease_impact - 1) * 100:+.1f}%",
            "baseline_yield": f"{baseline} tons/hectare"
        }
        
        # Generate recommendations
        if yield_per_hectare < baseline * 0.8:
            result["recommendations"].append("⚠️ Yield below optimal - review farming practices")
            result["recommendations"].append("Consider soil testing and nutrient supplementation")
        else:
            result["recommendations"].append("✓ Yield projection on track")
        
        if days_to_harvest > 0:
            result["recommendations"].append(f"📅 Estimated harvest in {days_to_harvest} days")
        else:
            result["recommendations"].append("🌾 Crop ready for harvest")
        
        # Market value estimation
        result["market_estimate"] = self._estimate_market_value(crop_type, total_yield)
        
        return result
    
    def _estimate_market_value(self, crop_type: str, yield_tons: float) -> Dict[str, Any]:
        """Estimate market value of yield (in INR per Quintal)"""
        
        # Average prices (INR per Quintal) - Standard Indian Market Unit
        # 1 Ton = 10 Quintals
        prices_per_quintal = {
            "wheat": 2200,     # Reduced from ton logic (22000/10)
            "rice": 2400,
            "corn": 1900,
            "cotton": 5200,
            "sugarcane": 350,  # ~350 per quintal
            "mustard": 4500,
            "soybean": 4800,
            "chickpeas": 5000,
            "potato": 1500,
            "onion": 1800,
            "tomato": 2000
        }
        
        # Make crop_type robust matching
        crop_clean = crop_type.lower().strip()
        base_price = prices_per_quintal.get(crop_clean, 2000)
        
        price_variation = random.uniform(0.9, 1.1)
        estimated_price_per_quintal = base_price * price_variation
        
        # Convert total yield in tons to quintals
        yield_quintals = yield_tons * 10
        total_value = yield_quintals * estimated_price_per_quintal
        
        return {
            "estimated_price_per_quintal": round(estimated_price_per_quintal, 2),
            "total_estimated_value": round(total_value, 2),
            "currency": "INR",
            "market_unit": "Quintal",
            "note": "Price subject to local mandi conditions"
        }
