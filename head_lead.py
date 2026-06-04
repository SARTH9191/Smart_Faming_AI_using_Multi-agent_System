"""
≡ƒºá LEAD AGENT - Master Orchestrator
Coordinates all specialized agents, resolves conflicts, makes global decisions
"""
from datetime import datetime
from typing import Dict, Any, List
import json

class LeadAgent:
    def __init__(self, database):
        self.db = database
        self.name = "Lead Orchestrator"
        self.agent_priority = {
            'critical': ['water_management', 'disease_detection', 'climate_risk'],
            'high': ['soil', 'weather_forecast', 'yield_prediction'],
            'medium': ['fertilizer', 'market_forecast', 'sustainability'],
            'low': ['blockchain', 'voice_assistant', 'drone_satellite']
        }
    
    def orchestrate_all_agents(self, farm_id: str) -> Dict[str, Any]:
        """
        Main orchestration logic - executes all agents in optimal order
        """
        print(f"≡ƒºá Lead Agent: Orchestrating analysis for {farm_id}")
        
        # Get latest sensor data
        sensor_data = self.db.get_latest_sensor_data(farm_id, limit=1)
        if not sensor_data:
            return {"error": "No sensor data available. Please simulate sensors first."}
        
        latest_sensors = sensor_data[0]
        
        # Initialize results
        results = {
            "farm_id": farm_id,
            "timestamp": datetime.now().isoformat(),
            "orchestration_summary": {},
            "agent_results": {},
            "global_recommendations": [],
            "conflict_resolutions": [],
            "priority_actions": []
        }
        
        try:
            # Import and execute agents
            from agents.soil_agent import SoilAgent
            from agents.weather_forecast_agent import WeatherForecastAgent
            from agents.water_management_agent import WaterManagementAgent
            from agents.fertilizer_agent import FertilizerAgent
            from agents.disease_detection_agent import DiseaseDetectionAgent
            from agents.yield_prediction_agent import YieldPredictionAgent
            from agents.sustainability_agent import SustainabilityAgent
            
            # 1. Soil Analysis (Foundation)
            try:
                soil_agent = SoilAgent(self.db)
                soil_result = soil_agent.analyze_soil(latest_sensors)
                results["agent_results"]["soil"] = soil_result
            except Exception as e:
                results["agent_results"]["soil"] = {"error": str(e), "status": "failed"}
            
            # 2. Weather Forecast (Critical for decisions)
            try:
                weather_agent = WeatherForecastAgent()
                weather_forecast = weather_agent.predict_weather("Delhi", 24)
                results["agent_results"]["weather"] = weather_forecast
            except Exception as e:
                weather_forecast = {"summary": {}, "rain_probability": 0}
                results["agent_results"]["weather"] = {"error": str(e), "status": "failed"}
            
            # 3. Water Management (Critical)
            try:
                water_agent = WaterManagementAgent(self.db)
                water_decision = water_agent.calculate_irrigation_need(latest_sensors, weather_forecast)
                results["agent_results"]["water"] = water_decision
            except Exception as e:
                water_decision = {"should_irrigate": False}
                results["agent_results"]["water"] = {"error": str(e), "status": "failed"}
            
            # 4. Fertilizer Recommendation
            try:
                fertilizer_agent = FertilizerAgent(self.db)
                fertilizer_plan = fertilizer_agent.recommend_fertilizer(latest_sensors)
                results["agent_results"]["fertilizer"] = fertilizer_plan
            except Exception as e:
                fertilizer_plan = {"recommended": False}
                results["agent_results"]["fertilizer"] = {"error": str(e), "status": "failed"}
            
            # 5. Disease Detection
            try:
                disease_agent = DiseaseDetectionAgent()
                disease_check = disease_agent.detect_disease("wheat", [])
                results["agent_results"]["disease"] = disease_check
            except Exception as e:
                results["agent_results"]["disease"] = {"error": str(e), "status": "failed"}
            
            # 6. Yield Prediction
            try:
                yield_agent = YieldPredictionAgent(self.db)
                soil_quality = results["agent_results"].get("soil", {}).get("quality", "medium")
                yield_pred = yield_agent.predict_yield("wheat", 2.0, soil_quality)
                results["agent_results"]["yield"] = yield_pred
            except Exception as e:
                results["agent_results"]["yield"] = {"error": str(e), "status": "failed"}
            
            # 7. Sustainability Check
            try:
                sustainability_agent = SustainabilityAgent(self.db)
                sustainability = sustainability_agent.calculate_sustainability_score(farm_id)
                results["agent_results"]["sustainability"] = sustainability
            except Exception as e:
                results["agent_results"]["sustainability"] = {"error": str(e), "status": "failed"}
            
            # Conflict Resolution
            conflicts = self._resolve_conflicts(water_decision, weather_forecast, fertilizer_plan)
            results["conflict_resolutions"] = conflicts
            
            # Generate Global Recommendations
            global_recs = self._generate_global_recommendations(results["agent_results"])
            results["global_recommendations"] = global_recs
            
            # Priority Actions
            priority = self._determine_priority_actions(results["agent_results"])
            results["priority_actions"] = priority
            
            # Store recommendations
            for rec in global_recs:
                try:
                    self.db.store_recommendation(
                        farm_id=farm_id,
                        agent_name="Lead Agent",
                        rec_type="global",
                        rec_text=rec,
                        priority="high"
                    )
                except Exception:
                    pass  # Non-critical, continue
            
            # Count successful agents
            successful_agents = sum(1 for r in results["agent_results"].values() if "error" not in r)
            
            results["orchestration_summary"] = {
                "total_agents_executed": 7,
                "successful_agents": successful_agents,
                "conflicts_resolved": len(conflicts),
                "recommendations_generated": len(global_recs),
                "system_health": "optimal" if successful_agents >= 5 else "degraded" if successful_agents >= 3 else "critical"
            }
            
        except Exception as e:
            results["error"] = f"Orchestration failed: {str(e)}"
            results["orchestration_summary"] = {"system_health": "error"}
        
        return results
    
    def _resolve_conflicts(self, water_decision, weather_forecast, fertilizer_plan) -> List[str]:
        """Resolve conflicts between agent recommendations"""
        conflicts = []
        
        # Conflict: Don't irrigate if rain predicted
        if water_decision.get("should_irrigate") and weather_forecast.get("rain_probability", 0) > 60:
            conflicts.append(
                "RESOLVED: Irrigation postponed - Rain predicted (60%+ probability)"
            )
        
        # Conflict: Don't fertilize if heavy rain expected
        if weather_forecast.get("rain_probability", 0) > 70:
            conflicts.append(
                "RESOLVED: Fertilizer application postponed - Heavy rain expected"
            )
        
        return conflicts
    
    def _generate_global_recommendations(self, agent_results: Dict) -> List[str]:
        """Generate high-level recommendations from all agents"""
        recommendations = []
        
        # Water management
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            recommendations.append(
                f"≡ƒÆº Irrigate for {water.get('duration_minutes', 30)} minutes"
            )
        
        # Soil health
        soil = agent_results.get("soil", {})
        if soil.get("quality") == "poor":
            recommendations.append("≡ƒî▒ Soil health critical - Apply organic matter")
        
        # Disease
        disease = agent_results.get("disease", {})
        if disease.get("disease_detected"):
            recommendations.append(
                f"ΓÜá∩╕Å Disease detected: {disease.get('disease_name')} - Take action"
            )
        
        # Yield optimization
        yield_data = agent_results.get("yield", {})
        if yield_data.get("expected_yield_tons", 0) < 3:
            recommendations.append("≡ƒôè Yield below optimal - Review farming practices")
        
        return recommendations
    
    def _determine_priority_actions(self, agent_results: Dict) -> List[Dict]:
        """Determine which actions need immediate attention"""
        actions = []
        
        # Critical: Disease detection
        disease = agent_results.get("disease", {})
        if disease.get("disease_detected"):
            actions.append({
                "priority": "critical",
                "action": "disease_control",
                "description": "Apply recommended pesticide immediately"
            })
        
        # High: Water management
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            actions.append({
                "priority": "high",
                "action": "irrigation",
                "description": f"Schedule irrigation for {water.get('duration_minutes')} min"
            })
        
        # Medium: Fertilizer
        fertilizer = agent_results.get("fertilizer", {})
        if fertilizer.get("recommended"):
            actions.append({
                "priority": "medium",
                "action": "fertilization",
                "description": "Apply fertilizer as per schedule"
            })
        
        return actions
    
    def get_latest_recommendations(self, farm_id: str) -> List[Dict]:
        """Get latest recommendations for dashboard"""
        return self.db.get_recommendations(farm_id, status="pending", limit=10)
    
    def generate_realtime_recommendations(self, farm_id: str) -> List[Dict]:
        """
        Generate real-time recommendations based on current sensor data
        WITHOUT running all agents (lightweight, fast)
        """
        # Get latest sensor data
        sensor_data = self.db.get_latest_sensor_data(farm_id, limit=1)
        if not sensor_data:
            return []
        
        latest = sensor_data[0]
        recommendations = []
        timestamp = datetime.now().isoformat()
        
        # 1. CRITICAL: Soil Moisture Check
        soil_moisture = latest.get("soil_moisture", 0)
        if soil_moisture < 30:
            recommendations.append({
                "priority": "critical",
                "agent": "Water Management AI",
                "title": "≡ƒÜ¿ Critical: Low Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Immediate irrigation needed!",
                "action": "Start irrigation for 30-45 minutes",
                "timestamp": timestamp,
                "type": "water_critical"
            })
        elif soil_moisture < 40:
            recommendations.append({
                "priority": "high",
                "agent": "Water Management AI",
                "title": "ΓÜá∩╕Å Low Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Irrigation recommended",
                "action": "Schedule irrigation within 24 hours",
                "timestamp": timestamp,
                "type": "water_warning"
            })
        elif soil_moisture > 80:
            recommendations.append({
                "priority": "medium",
                "agent": "Water Management AI",
                "title": "≡ƒÆº High Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Excessive water detected",
                "action": "Check drainage system, skip next irrigation",
                "timestamp": timestamp,
                "type": "water_excess"
            })
        
        # 2. Soil pH Check
        soil_ph = latest.get("soil_ph", 7.0)
        if soil_ph < 5.5:
            recommendations.append({
                "priority": "high",
                "agent": "Soil Health AI",
                "title": "≡ƒº¬ Acidic Soil Detected",
                "message": f"pH level at {soil_ph:.1f} - Too acidic for optimal growth",
                "action": "Apply lime to raise pH (target: 6.0-7.5)",
                "timestamp": timestamp,
                "type": "ph_low"
            })
        elif soil_ph > 8.0:
            recommendations.append({
                "priority": "high",
                "agent": "Soil Health AI",
                "title": "≡ƒº¬ Alkaline Soil Detected",
                "message": f"pH level at {soil_ph:.1f} - Too alkaline",
                "action": "Apply sulfur or organic matter to lower pH",
                "timestamp": timestamp,
                "type": "ph_high"
            })
        
        # 3. Temperature Check
        air_temp = latest.get("air_temperature", 25)
        if air_temp > 40:
            recommendations.append({
                "priority": "critical",
                "agent": "Climate AI",
                "title": "≡ƒîí∩╕Å Extreme Heat Alert",
                "message": f"Temperature at {air_temp:.1f}┬░C - Heat stress risk!",
                "action": "Increase irrigation frequency, provide shade if possible",
                "timestamp": timestamp,
                "type": "temp_high"
            })
        elif air_temp < 10:
            recommendations.append({
                "priority": "high",
                "agent": "Climate AI",
                "title": "Γ¥ä∩╕Å Cold Temperature Alert",
                "message": f"Temperature at {air_temp:.1f}┬░C - Frost risk",
                "action": "Consider protective covering for sensitive crops",
                "timestamp": timestamp,
                "type": "temp_low"
            })
        
        # 4. NPK Nutrient Check
        nitrogen = latest.get("npk_nitrogen", 0)
        phosphorus = latest.get("npk_phosphorus", 0)
        potassium = latest.get("npk_potassium", 0)
        
        if nitrogen < 150:
            recommendations.append({
                "priority": "medium",
                "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Nitrogen Levels",
                "message": f"Nitrogen at {nitrogen:.0f} mg/kg - Below optimal",
                "action": "Apply nitrogen-rich fertilizer (urea or organic compost)",
                "timestamp": timestamp,
                "type": "nutrient_nitrogen"
            })
        
        if phosphorus < 15:
            recommendations.append({
                "priority": "medium",
                "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Phosphorus Levels",
                "message": f"Phosphorus at {phosphorus:.0f} mg/kg - Below optimal",
                "action": "Apply phosphate fertilizer or bone meal",
                "timestamp": timestamp,
                "type": "nutrient_phosphorus"
            })
        
        if potassium < 150:
            recommendations.append({
                "priority": "medium",
                "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Potassium Levels",
                "message": f"Potassium at {potassium:.0f} mg/kg - Below optimal",
                "action": "Apply potash or wood ash",
                "timestamp": timestamp,
                "type": "nutrient_potassium"
            })
        
        # 5. Optimal Conditions Recognition
        if (40 <= soil_moisture <= 70 and 
            6.0 <= soil_ph <= 7.5 and 
            20 <= air_temp <= 30 and
            nitrogen >= 200 and phosphorus >= 20 and potassium >= 200):
            recommendations.append({
                "priority": "info",
                "agent": "Lead Orchestrator AI",
                "title": "Γ£à Optimal Growing Conditions",
                "message": "All parameters are within ideal range!",
                "action": "Maintain current practices - conditions are excellent",
                "timestamp": timestamp,
                "type": "optimal"
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 5))
        
        return recommendations
