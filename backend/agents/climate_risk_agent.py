"""
⚠️ CLIMATE RISK PREDICTION AGENT
Predicts drought/flood/heatwave risks with 30-day risk index
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class ClimateRiskAgent:
    def __init__(self):
        self.name = "Climate Risk Prediction Agent"
    
    def assess_risk(self, location: str, days: int = 30) -> Dict[str, Any]:
        """
        Assess climate risks for next N days
        In production: Use ML models trained on historical climate data
        """
        
        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "assessment_period_days": days,
            "overall_risk_score": 0,
            "risk_level": "low",
            "specific_risks": {},
            "daily_risk_index": [],
            "mitigation_strategies": [],
            "recommendations": []
        }
        
        # Assess specific risks
        result["specific_risks"] = {
            "drought": self._assess_drought_risk(location, days),
            "flood": self._assess_flood_risk(location, days),
            "heatwave": self._assess_heatwave_risk(location, days),
            "frost": self._assess_frost_risk(location, days),
            "storm": self._assess_storm_risk(location, days)
        }
        
        # Calculate overall risk score
        risk_scores = [risk["risk_score"] for risk in result["specific_risks"].values()]
        result["overall_risk_score"] = round(sum(risk_scores) / len(risk_scores), 1)
        
        # Determine risk level
        if result["overall_risk_score"] > 70:
            result["risk_level"] = "high"
        elif result["overall_risk_score"] > 40:
            result["risk_level"] = "medium"
        else:
            result["risk_level"] = "low"
        
        # Generate daily risk index
        result["daily_risk_index"] = self._generate_daily_risk_index(days, result["specific_risks"])
        
        # Mitigation strategies
        result["mitigation_strategies"] = self._generate_mitigation_strategies(result["specific_risks"])
        
        # Recommendations
        result["recommendations"] = self._generate_risk_recommendations(result)
        
        return result
    
    def _assess_drought_risk(self, location: str, days: int) -> Dict[str, Any]:
        """Assess drought risk"""
        
        # Simulate drought indicators
        rainfall_deficit = random.uniform(0, 40)  # % below normal
        soil_moisture_index = random.uniform(30, 80)
        temperature_anomaly = random.uniform(-2, 5)  # degrees above normal
        
        # Calculate risk score
        risk_score = 0
        if rainfall_deficit > 30:
            risk_score += 35
        if soil_moisture_index < 40:
            risk_score += 30
        if temperature_anomaly > 3:
            risk_score += 25
        
        risk_score = min(100, risk_score)
        
        return {
            "risk_score": round(risk_score, 1),
            "probability": round(random.uniform(10, 70), 1),
            "severity": "high" if risk_score > 60 else "medium" if risk_score > 30 else "low",
            "indicators": {
                "rainfall_deficit_percent": round(rainfall_deficit, 1),
                "soil_moisture_index": round(soil_moisture_index, 1),
                "temperature_anomaly": round(temperature_anomaly, 1)
            },
            "onset_estimate": "7-14 days" if risk_score > 60 else "15-30 days"
        }
    
    def _assess_flood_risk(self, location: str, days: int) -> Dict[str, Any]:
        """Assess flood risk"""
        
        heavy_rain_probability = random.uniform(10, 60)
        watershed_saturation = random.uniform(40, 90)
        
        risk_score = 0
        if heavy_rain_probability > 50:
            risk_score += 40
        if watershed_saturation > 70:
            risk_score += 30
        
        return {
            "risk_score": round(risk_score, 1),
            "probability": round(heavy_rain_probability, 1),
            "severity": "high" if risk_score > 60 else "medium" if risk_score > 30 else "low",
            "indicators": {
                "heavy_rain_probability": round(heavy_rain_probability, 1),
                "watershed_saturation": round(watershed_saturation, 1)
            }
        }
    
    def _assess_heatwave_risk(self, location: str, days: int) -> Dict[str, Any]:
        """Assess heatwave risk"""
        
        max_temp_forecast = random.uniform(35, 48)
        consecutive_hot_days = random.randint(0, 7)
        
        risk_score = 0
        if max_temp_forecast > 42:
            risk_score += 50
        elif max_temp_forecast > 38:
            risk_score += 30
        
        if consecutive_hot_days > 5:
            risk_score += 30
        
        return {
            "risk_score": round(risk_score, 1),
            "probability": round(random.uniform(20, 80), 1),
            "severity": "high" if risk_score > 60 else "medium" if risk_score > 30 else "low",
            "indicators": {
                "max_temperature_forecast": round(max_temp_forecast, 1),
                "consecutive_hot_days": consecutive_hot_days
            }
        }
    
    def _assess_frost_risk(self, location: str, days: int) -> Dict[str, Any]:
        """Assess frost risk"""
        
        min_temp_forecast = random.uniform(0, 15)
        
        risk_score = 30 if min_temp_forecast < 5 else 10 if min_temp_forecast < 10 else 0
        
        return {
            "risk_score": round(risk_score, 1),
            "probability": round(random.uniform(5, 40), 1),
            "severity": "medium" if risk_score > 20 else "low",
            "indicators": {
                "min_temperature_forecast": round(min_temp_forecast, 1)
            }
        }
    
    def _assess_storm_risk(self, location: str, days: int) -> Dict[str, Any]:
        """Assess storm risk"""
        
        wind_speed_forecast = random.uniform(20, 80)
        storm_probability = random.uniform(10, 50)
        
        risk_score = 0
        if wind_speed_forecast > 60:
            risk_score += 40
        if storm_probability > 40:
            risk_score += 30
        
        return {
            "risk_score": round(risk_score, 1),
            "probability": round(storm_probability, 1),
            "severity": "high" if risk_score > 50 else "medium" if risk_score > 25 else "low",
            "indicators": {
                "max_wind_speed_forecast": round(wind_speed_forecast, 1),
                "storm_probability": round(storm_probability, 1)
            }
        }
    
    def _generate_daily_risk_index(self, days: int, specific_risks: Dict) -> List[Dict]:
        """Generate day-by-day risk index"""
        
        daily_index = []
        
        for day in range(min(days, 30)):
            date = datetime.now() + timedelta(days=day)
            
            # Simulate daily risk (influenced by specific risks)
            base_risk = sum([r["risk_score"] for r in specific_risks.values()]) / len(specific_risks)
            daily_risk = base_risk + random.uniform(-15, 15)
            daily_risk = max(0, min(100, daily_risk))
            
            daily_index.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day + 1,
                "risk_score": round(daily_risk, 1),
                "risk_level": "high" if daily_risk > 60 else "medium" if daily_risk > 30 else "low",
                "primary_threat": random.choice(list(specific_risks.keys()))
            })
        
        return daily_index
    
    def _generate_mitigation_strategies(self, specific_risks: Dict) -> List[Dict]:
        """Generate mitigation strategies for identified risks"""
        
        strategies = []
        
        # Drought mitigation
        if specific_risks["drought"]["risk_score"] > 50:
            strategies.append({
                "risk": "Drought",
                "strategy": "Water Conservation",
                "actions": [
                    "Install drip irrigation system",
                    "Mulch soil to retain moisture",
                    "Harvest rainwater during early season",
                    "Select drought-resistant crop varieties"
                ]
            })
        
        # Flood mitigation
        if specific_risks["flood"]["risk_score"] > 50:
            strategies.append({
                "risk": "Flood",
                "strategy": "Drainage & Protection",
                "actions": [
                    "Clear drainage channels",
                    "Build bunds around fields",
                    "Harvest crops if matured",
                    "Relocate stored produce to higher ground"
                ]
            })
        
        # Heatwave mitigation
        if specific_risks["heatwave"]["risk_score"] > 50:
            strategies.append({
                "risk": "Heatwave",
                "strategy": "Heat Stress Management",
                "actions": [
                    "Increase irrigation frequency",
                    "Provide shade nets for sensitive crops",
                    "Apply mulch to reduce soil temperature",
                    "Spray water during extreme heat hours"
                ]
            })
        
        return strategies
    
    def _generate_risk_recommendations(self, result: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if result["overall_risk_score"] > 70:
            recommendations.append("🚨 HIGH RISK: Take immediate protective measures")
        elif result["overall_risk_score"] > 40:
            recommendations.append("⚠️ MODERATE RISK: Prepare contingency plans")
        
        # Specific recommendations based on highest risk
        risks = result["specific_risks"]
        highest_risk = max(risks.items(), key=lambda x: x[1]["risk_score"])
        
        recommendations.append(f"⚠️ Primary threat: {highest_risk[0].upper()} (Risk Score: {highest_risk[1]['risk_score']})")
        
        if highest_risk[0] == "drought":
            recommendations.append("💧 Prioritize water conservation measures")
        elif highest_risk[0] == "flood":
            recommendations.append("🌊 Ensure drainage systems are functional")
        elif highest_risk[0] == "heatwave":
            recommendations.append("🌡️ Increase irrigation, provide crop shade")
        
        # Insurance recommendation
        if result["overall_risk_score"] > 50:
            recommendations.append("📋 Ensure crop insurance is active (PMFBY)")
        
        return recommendations
