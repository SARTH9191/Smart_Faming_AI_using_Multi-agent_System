"""
🧠 LEAD AGENT - Master Orchestrator (Async + PostgreSQL Context)
================================================================
Coordinates all specialized agents, resolves conflicts, makes global decisions.
NOW uses ContextBuilder for long-term memory and persists agent results.
"""
from datetime import datetime
from typing import Dict, Any, List
import json
import asyncio
from agents.llm_orchestrator import LLMOrchestrator
from config import API_CONFIG

class LeadAgent:
    def __init__(self, database, auth_system=None):
        self.db = database
        self.auth_system = auth_system
        self.name = "Lead Orchestrator"
        self.agent_priority = {
            'critical': ['water_management', 'disease_detection', 'climate_risk'],
            'high': ['soil', 'weather_forecast', 'yield_prediction'],
            'medium': ['fertilizer', 'market_forecast', 'sustainability'],
            'low': ['blockchain', 'voice_assistant', 'drone_satellite']
        }
        self.llm = LLMOrchestrator(
            base_url=API_CONFIG.get("ollama_base_url", "http://localhost:11434"),
            model=API_CONFIG.get("ollama_model", "mistral:latest")
        )

    async def orchestrate_all_agents(self, farm_id: str) -> Dict[str, Any]:
        """
        Main orchestration logic — async, with long-term context.
        """
        print(f"🧠 Lead Agent: Orchestrating analysis for {farm_id}")

        # Get latest sensor data
        sensor_data = await self.db.get_latest_readings(farm_id, limit=1)
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
            # Import agents
            from agents.soil_agent import SoilAgent
            from agents.weather_forecast_agent import WeatherForecastAgent
            from agents.water_management_agent import WaterManagementAgent
            from agents.fertilizer_agent import FertilizerAgent
            from agents.disease_detection_agent import DiseaseDetectionAgent
            from agents.yield_prediction_agent import YieldPredictionAgent
            from agents.sustainability_agent import SustainabilityAgent

            # 1. Soil Analysis
            try:
                soil_agent = SoilAgent(self.db)
                results["agent_results"]["soil"] = soil_agent.analyze_soil(latest_sensors)
            except Exception as e:
                results["agent_results"]["soil"] = {"error": str(e), "status": "failed"}

            # 2. Weather Forecast
            try:
                weather_agent = WeatherForecastAgent()
                weather_forecast = weather_agent.predict_weather("Delhi", 24)
                results["agent_results"]["weather"] = weather_forecast
            except Exception as e:
                weather_forecast = {"summary": {}, "rain_probability": 0}
                results["agent_results"]["weather"] = {"error": str(e), "status": "failed"}

            # 3. Water Management
            try:
                water_agent = WaterManagementAgent(self.db)
                water_decision = water_agent.calculate_irrigation_need(latest_sensors, weather_forecast)
                results["agent_results"]["water"] = water_decision
            except Exception as e:
                water_decision = {"should_irrigate": False}
                results["agent_results"]["water"] = {"error": str(e), "status": "failed"}

            # 4. Fertilizer
            try:
                fertilizer_agent = FertilizerAgent(self.db)
                results["agent_results"]["fertilizer"] = fertilizer_agent.recommend_fertilizer(latest_sensors)
            except Exception as e:
                results["agent_results"]["fertilizer"] = {"error": str(e), "status": "failed"}

            # 5. Disease Detection
            try:
                disease_agent = DiseaseDetectionAgent()
                results["agent_results"]["disease"] = disease_agent.detect_disease("wheat", [])
            except Exception as e:
                results["agent_results"]["disease"] = {"error": str(e), "status": "failed"}

            # Conflict Resolution
            conflicts = self._resolve_conflicts(water_decision, weather_forecast, results["agent_results"].get("fertilizer", {}))
            results["conflict_resolutions"] = conflicts

            # Generate Global Recommendations
            global_recs = self._generate_global_recommendations(results["agent_results"])
            results["global_recommendations"] = global_recs

            # Priority Actions
            priority = self._determine_priority_actions(results["agent_results"])
            results["priority_actions"] = priority

            # ── 6. Unified AI Advice (The "Interacting agents" part) ──
            # Prepare context for LLM
            shared_context = {
                "soil_moisture": latest_sensors.get("soil_moisture"),
                "temperature": latest_sensors.get("air_temperature"),
                "humidity": latest_sensors.get("humidity"),
                "rain_in_24h": weather_forecast.get("rain_probability", 0) > 50,
                "disease_alert": results["agent_results"].get("disease", {}).get("disease_detected", False),
                "risk_level": results["agent_results"].get("disease", {}).get("risk_level", "low"),
                "fertilizer_advice": results["agent_results"].get("fertilizer", {}).get("recommendation_text", "")
            }

            # Get unified advice (calls Ollama/Mistral)
            unified_advice = await self.llm.generate_unified_advice(
                shared_context=shared_context,
                farm_id=farm_id,
                db=self.db
            )
            
            results["unified_advice"] = unified_advice
            if unified_advice.get("source") in ["llm", "groq", "ollama"]:
                results["global_recommendations"].insert(0, f"🤖 AI Insights:\n\n{unified_advice['advice']}")

            # Store recommendations
            for rec in global_recs:
                try:
                    await self.db.store_recommendation({
                        "farm_id": farm_id,
                        "agent_name": "Lead Agent",
                        "recommendation_type": "global",
                        "recommendation_text": rec,
                        "priority": "high"
                    })
                except Exception:
                    pass

            successful_agents = sum(1 for r in results["agent_results"].values() if "error" not in r)
            results["orchestration_summary"] = {
                "total_agents_executed": 7,
                "successful_agents": successful_agents,
                "conflicts_resolved": len(conflicts),
                "system_health": "optimal" if successful_agents >= 5 else "degraded"
            }

        except Exception as e:
            results["error"] = f"Orchestration failed: {str(e)}"
        
        return results

    def _resolve_conflicts(self, water_decision, weather_forecast, fertilizer_plan) -> List[str]:
        conflicts = []
        if water_decision.get("should_irrigate") and weather_forecast.get("rain_probability", 0) > 60:
            conflicts.append("RESOLVED: Irrigation postponed - Rain predicted (60%+ probability)")
        if weather_forecast.get("rain_probability", 0) > 70:
            conflicts.append("RESOLVED: Fertilizer application postponed - Heavy rain expected")
        return conflicts

    def _generate_global_recommendations(self, agent_results: Dict) -> List[str]:
        recommendations = []
        
        # Water / Irrigation Detailed Recommendation
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            duration = water.get('duration_minutes', 30)
            recommendations.append(f"💧 Action Required: Irrigate for {duration} minutes to safely restore optimal soil moisture levels, taking into account current weather forecasts.")
            
        # Disease Detailed Recommendation
        disease = agent_results.get("disease", {})
        is_diseased = disease.get("disease_detected", False) or (disease.get("disease_key") and disease.get("disease_key") != "healthy")
        if is_diseased:
            name = disease.get('disease_name') or disease.get('display_name') or disease.get('disease_key', 'Unknown pathgen')
            reason = disease.get('reasoning', 'Take immediate protective action to prevent further spread.')
            recommendations.append(f"⚠️ Critical Alert: Disease detected ({name}). {reason}")
            
        # Fertilizer Detailed Recommendation
        fertilizer = agent_results.get("fertilizer", {})
        if fertilizer.get("recommendation_text"):
            recommendations.append(f"🌱 Fertilizer Recommendation: {fertilizer.get('recommendation_text')}")
            
        return recommendations

    def _determine_priority_actions(self, agent_results: Dict) -> List[Dict]:
        actions = []
        disease = agent_results.get("disease", {})
        if disease.get("disease_detected"):
            actions.append({"priority": "critical", "action": "disease_control", "description": "Apply recommended pesticide immediately"})
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            actions.append({"priority": "high", "action": "irrigation", "description": f"Schedule irrigation for {water.get('duration_minutes')} min"})
        return actions

    async def get_latest_recommendations(self, farm_id: str) -> List[Dict]:
        return await self.db.get_recommendations(farm_id, limit=10)

    async def generate_realtime_recommendations(self, farm_id: str) -> List[Dict]:
        sensor_data = await self.db.get_latest_readings(farm_id, limit=1)
        if not sensor_data:
            return []
        
        latest = sensor_data[0]
        recommendations = []
        timestamp = datetime.now().isoformat()
        
        soil_moisture = latest.get("soil_moisture", 0)
        if soil_moisture < 30:
            recommendations.append({
                "priority": "critical",
                "agent": "Water Management AI",
                "title": "🚨 Critical: Low Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Immediate irrigation needed!",
                "action": "Start irrigation for 30-45 minutes",
                "timestamp": timestamp,
                "type": "water_critical"
            })
        
        return recommendations
