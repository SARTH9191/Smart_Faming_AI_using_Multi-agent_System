"""
≡ƒºá LEAD AGENT - Master Orchestrator (Async + PostgreSQL Context)
================================================================
Coordinates all specialized agents, resolves conflicts, makes global decisions.
NOW uses ContextBuilder for long-term memory and persists agent results.
"""
from datetime import datetime
from typing import Dict, Any, List
import json
import asyncio


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

    async def orchestrate_all_agents(self, farm_id: str) -> Dict[str, Any]:
        """
        Main orchestration logic ΓÇö async, with long-term context.
        """
        print(f"≡ƒºá Lead Agent: Orchestrating analysis for {farm_id}")

        # Ensure default field exists for this farm_id
        await self.db.ensure_default_field(farm_id)

        # Get latest sensor data
        sensor_data = await self.db.get_latest_sensor_data(farm_id, limit=1)
        if not sensor_data:
            return {"error": "No sensor data available. Please simulate sensors first."}

        latest_sensors = sensor_data[0]

        # ΓöÇΓöÇ Build rich context from PostgreSQL (the brain's memory) ΓöÇΓöÇ
        from core.context_builder import context_builder
        rich_context = await context_builder.build_context(farm_id, depth="full")

        # Initialize results
        results = {
            "farm_id": farm_id,
            "timestamp": datetime.now().isoformat(),
            "orchestration_summary": {},
            "agent_results": {},
            "global_recommendations": [],
            "conflict_resolutions": [],
            "priority_actions": [],
            "context_used": rich_context,  # Expose for debugging
        }

        try:
            # Import and execute agents (sync agents ΓÇö run in executor)
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
                # Cache weather data to PostgreSQL
                await self.db.cache_api_response(
                    source="openweather", endpoint="forecast",
                    location="Delhi", response_payload=weather_forecast,
                    ttl_seconds=1800, farm_id=farm_id,
                )
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

            # ΓöÇΓöÇ Persist ALL agent results to agent_memory_logs ΓöÇΓöÇ
            for agent_name, agent_result in results["agent_results"].items():
                try:
                    summary = f"{agent_name}: "
                    if "error" in agent_result:
                        summary += f"FAILED - {agent_result.get('error', '')[:80]}"
                    else:
                        summary += json.dumps(agent_result, default=str)[:120]

                    await self.db.store_agent_memory(
                        farm_id=farm_id,
                        agent_name=agent_name,
                        action="analyze",
                        input_context={"sensor_snapshot": latest_sensors},
                        output_result=agent_result,
                        summary=summary,
                    )
                except Exception:
                    pass  # Non-critical

            # ΓöÇΓöÇ Build shared context (with rich historical context) ΓöÇΓöÇ
            weather_data = results["agent_results"].get("weather", {})
            weather_summary = weather_data.get("summary", {}) if isinstance(weather_data, dict) else {}
            disease_data = results["agent_results"].get("disease", {})
            fertilizer_data = results["agent_results"].get("fertilizer", {})

            rain_in_24h = weather_summary.get("rain_expected", False)
            if not isinstance(rain_in_24h, bool):
                rain_in_24h = weather_summary.get("avg_rain_probability", 0) > 60

            weather_text = f"Avg Temp: {weather_summary.get('avg_temperature', 'N/A')}C, Rain Prob: {weather_summary.get('avg_rain_probability', 'N/A')}%"
            if isinstance(weather_data, dict) and weather_data.get("status") == "error":
                weather_text = "Weather API Error"

            fertilizer_advice = "Fertilizer recommended" if fertilizer_data.get("recommended") else "No fertilizer needed"

            shared_context = {
                "rain_in_24h": rain_in_24h,
                "weather_summary": weather_text,
                "disease_alert": disease_data.get("disease_detected", False),
                "risk_level": disease_data.get("severity", "none"),
                "fertilizer_advice": fertilizer_advice,
            }
            results["shared_context"] = shared_context

            # ΓöÇΓöÇ LLM Orchestration ΓÇö now with RICH context ΓöÇΓöÇ
            from agents.llm_orchestrator import LLMOrchestrator
            llm = LLMOrchestrator()

            unified_advice = await llm.generate_unified_advice(
                shared_context=shared_context,
                rich_context=rich_context,
                farm_id=farm_id,
                db=self.db,
                use_llm=True,
            )
            final_recommendation_text = unified_advice.get("advice", "")

            # Legacy fields for dashboard compatibility
            conflicts = []
            if rain_in_24h and fertilizer_data.get("recommended"):
                conflicts.append("RESOLVED: Avoid fertilizer - Rain predicted in 24h")
            if shared_context["disease_alert"]:
                conflicts.append("RESOLVED: Prioritize disease treatment over nutrition interventions")

            results["conflict_resolutions"] = conflicts
            results["global_recommendations"] = [final_recommendation_text]

            # Priority Actions
            priority = self._determine_priority_actions(results["agent_results"])
            results["priority_actions"] = priority

            # ΓöÇΓöÇ Store recommendations to PostgreSQL ΓöÇΓöÇ
            for rec in results["global_recommendations"]:
                try:
                    await self.db.store_recommendation(
                        farm_id=farm_id,
                        agent_name="Lead Agent",
                        rec_type="global",
                        rec_text=rec,
                        priority="high",
                        context_snapshot=shared_context,
                        llm_source=unified_advice.get("source", "rule_based"),
                    )
                except Exception:
                    pass  # Non-critical

            # Count successful agents
            successful_agents = sum(1 for r in results["agent_results"].values() if "error" not in r)

            results["orchestration_summary"] = {
                "total_agents_executed": 7,
                "successful_agents": successful_agents,
                "conflicts_resolved": len(conflicts),
                "recommendations_generated": len(results["global_recommendations"]),
                "context_depth": "full",
                "llm_source": unified_advice.get("source", "unknown"),
                "system_health": "optimal" if successful_agents >= 5 else "degraded" if successful_agents >= 3 else "critical"
            }

        except Exception as e:
            results["error"] = f"Orchestration failed: {str(e)}"
            results["orchestration_summary"] = {"system_health": "error"}

        return results

    def _resolve_conflicts(self, water_decision, weather_forecast, fertilizer_plan) -> List[str]:
        """Resolve conflicts between agent recommendations"""
        conflicts = []
        if water_decision.get("should_irrigate") and weather_forecast.get("rain_probability", 0) > 60:
            conflicts.append("RESOLVED: Irrigation postponed - Rain predicted (60%+ probability)")
        if weather_forecast.get("rain_probability", 0) > 70:
            conflicts.append("RESOLVED: Fertilizer application postponed - Heavy rain expected")
        return conflicts

    def _generate_global_recommendations(self, agent_results: Dict) -> List[str]:
        """Generate high-level recommendations from all agents"""
        recommendations = []
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            recommendations.append(f"≡ƒÆº Irrigate for {water.get('duration_minutes', 30)} minutes")
        soil = agent_results.get("soil", {})
        if soil.get("quality") == "poor":
            recommendations.append("≡ƒî▒ Soil health critical - Apply organic matter")
        disease = agent_results.get("disease", {})
        if disease.get("disease_detected"):
            recommendations.append(f"ΓÜá∩╕Å Disease detected: {disease.get('disease_name')} - Take action")
        yield_data = agent_results.get("yield", {})
        if yield_data.get("expected_yield_tons", 0) < 3:
            recommendations.append("≡ƒôè Yield below optimal - Review farming practices")
        return recommendations

    def _determine_priority_actions(self, agent_results: Dict) -> List[Dict]:
        """Determine which actions need immediate attention"""
        actions = []
        disease = agent_results.get("disease", {})
        if disease.get("disease_detected"):
            actions.append({"priority": "critical", "action": "disease_control", "description": "Apply recommended pesticide immediately"})
        water = agent_results.get("water", {})
        if water.get("should_irrigate"):
            actions.append({"priority": "high", "action": "irrigation", "description": f"Schedule irrigation for {water.get('duration_minutes')} min"})
        fertilizer = agent_results.get("fertilizer", {})
        if fertilizer.get("recommended"):
            actions.append({"priority": "medium", "action": "fertilization", "description": "Apply fertilizer as per schedule"})
        return actions

    async def get_latest_recommendations(self, farm_id: str) -> List[Dict]:
        """Get latest recommendations for dashboard"""
        return await self.db.get_recommendations(farm_id, status="pending", limit=10)

    async def generate_realtime_recommendations(self, farm_id: str) -> List[Dict]:
        """
        Generate real-time recommendations based on current sensor data
        WITHOUT running all agents (lightweight, fast)
        """
        sensor_data = await self.db.get_latest_sensor_data(farm_id, limit=1)
        if not sensor_data:
            return []

        latest = sensor_data[0]
        recommendations = []
        timestamp = datetime.now().isoformat()

        # 1. CRITICAL: Soil Moisture Check
        soil_moisture = latest.get("soil_moisture", 0)
        if soil_moisture < 30:
            recommendations.append({
                "priority": "critical", "agent": "Water Management AI",
                "title": "≡ƒÜ¿ Critical: Low Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Immediate irrigation needed!",
                "action": "Start irrigation for 30-45 minutes", "timestamp": timestamp, "type": "water_critical"
            })
        elif soil_moisture < 40:
            recommendations.append({
                "priority": "high", "agent": "Water Management AI",
                "title": "ΓÜá∩╕Å Low Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Irrigation recommended",
                "action": "Schedule irrigation within 24 hours", "timestamp": timestamp, "type": "water_warning"
            })
        elif soil_moisture > 80:
            recommendations.append({
                "priority": "medium", "agent": "Water Management AI",
                "title": "≡ƒÆº High Soil Moisture",
                "message": f"Soil moisture at {soil_moisture:.1f}% - Excessive water detected",
                "action": "Check drainage system, skip next irrigation", "timestamp": timestamp, "type": "water_excess"
            })

        # 2. Soil pH Check
        soil_ph = latest.get("soil_ph", 7.0)
        if soil_ph < 5.5:
            recommendations.append({
                "priority": "high", "agent": "Soil Health AI",
                "title": "≡ƒº¬ Acidic Soil Detected",
                "message": f"pH level at {soil_ph:.1f} - Too acidic for optimal growth",
                "action": "Apply lime to raise pH (target: 6.0-7.5)", "timestamp": timestamp, "type": "ph_low"
            })
        elif soil_ph > 8.0:
            recommendations.append({
                "priority": "high", "agent": "Soil Health AI",
                "title": "≡ƒº¬ Alkaline Soil Detected",
                "message": f"pH level at {soil_ph:.1f} - Too alkaline",
                "action": "Apply sulfur or organic matter to lower pH", "timestamp": timestamp, "type": "ph_high"
            })

        # 3. Temperature Check
        air_temp = latest.get("air_temperature", 25)
        if air_temp > 40:
            recommendations.append({
                "priority": "critical", "agent": "Climate AI",
                "title": "≡ƒîí∩╕Å Extreme Heat Alert",
                "message": f"Temperature at {air_temp:.1f}┬░C - Heat stress risk!",
                "action": "Increase irrigation frequency, provide shade if possible", "timestamp": timestamp, "type": "temp_high"
            })
        elif air_temp < 10:
            recommendations.append({
                "priority": "high", "agent": "Climate AI",
                "title": "Γ¥ä∩╕Å Cold Temperature Alert",
                "message": f"Temperature at {air_temp:.1f}┬░C - Frost risk",
                "action": "Consider protective covering for sensitive crops", "timestamp": timestamp, "type": "temp_low"
            })

        # 4. NPK Nutrient Check
        nitrogen = latest.get("npk_nitrogen", 0)
        phosphorus = latest.get("npk_phosphorus", 0)
        potassium = latest.get("npk_potassium", 0)

        if nitrogen < 150:
            recommendations.append({
                "priority": "medium", "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Nitrogen Levels",
                "message": f"Nitrogen at {nitrogen:.0f} mg/kg - Below optimal",
                "action": "Apply nitrogen-rich fertilizer (urea or organic compost)", "timestamp": timestamp, "type": "nutrient_nitrogen"
            })
        if phosphorus < 15:
            recommendations.append({
                "priority": "medium", "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Phosphorus Levels",
                "message": f"Phosphorus at {phosphorus:.0f} mg/kg - Below optimal",
                "action": "Apply phosphate fertilizer or bone meal", "timestamp": timestamp, "type": "nutrient_phosphorus"
            })
        if potassium < 150:
            recommendations.append({
                "priority": "medium", "agent": "Fertilizer AI",
                "title": "≡ƒî▒ Low Potassium Levels",
                "message": f"Potassium at {potassium:.0f} mg/kg - Below optimal",
                "action": "Apply potash or wood ash", "timestamp": timestamp, "type": "nutrient_potassium"
            })

        # 5. Optimal Conditions
        if (40 <= soil_moisture <= 70 and 6.0 <= soil_ph <= 7.5 and
            20 <= air_temp <= 30 and nitrogen >= 200 and phosphorus >= 20 and potassium >= 200):
            recommendations.append({
                "priority": "info", "agent": "Lead Orchestrator AI",
                "title": "Γ£à Optimal Growing Conditions",
                "message": "All parameters are within ideal range!",
                "action": "Maintain current practices - conditions are excellent", "timestamp": timestamp, "type": "optimal"
            })

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 5))

        return recommendations
