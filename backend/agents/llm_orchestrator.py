"""
LLM ORCHESTRATOR — Local LLM Integration with Mistral via Ollama
================================================================
Now accepts RICH context from ContextBuilder and logs every
conversation to llm_conversation_history in PostgreSQL.
Falls back to rule-based resolution if LLM unavailable.
"""

import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


import os

class LLMOrchestrator:
    """
    Local LLM orchestrator using Groq API (Primary) or Mistral via Ollama (Fallback).
    Falls back to rule-based resolution if both unavailable.
    """

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "mistral:latest"
    ):
        self.base_url = base_url
        self.ollama_model = model
        self.groq_model = "llama-3.1-8b-instant"
        
        self._groq_available = False
        self._ollama_available = False
        
        self.groq_api_key = self._load_api_key()
        if self.groq_api_key:
            from groq import Groq
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                self._groq_available = True
                print(f"LLM Orchestrator: Groq API available using {self.groq_model}")
            except Exception as e:
                print(f"LLM Orchestrator: Failed to initialize Groq client: {e}")
                
        self._check_availability()
        
    def _load_api_key(self):
        """Load API key from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'api_config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('groq_api_key', '')
        except:
            return ''

    def _check_availability(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self._ollama_available = response.status_code == 200
            if self._ollama_available and not self._groq_available:
                print(f"LLM Orchestrator: Mistral available at {self.base_url}")
        except Exception:
            self._ollama_available = False
            
        if not self._groq_available and not self._ollama_available:
            print("LLM Orchestrator: No LLM available, using rule-based fallback")

    @property
    def is_available(self) -> bool:
        self._check_availability()
        return self._groq_available or self._ollama_available

    async def generate_unified_advice(
        self,
        shared_context: Dict[str, Any],
        rich_context: Dict[str, Any] = None,
        farm_id: str = None,
        db=None,
        use_llm: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate unified advice from all agent outputs.
        Now accepts rich_context from ContextBuilder and logs to DB.
        """
        if use_llm and self.is_available:
            result = self._generate_with_llm(shared_context, rich_context)
        else:
            result = self._generate_rule_based(shared_context)

        # ── Persist LLM conversation to PostgreSQL ──
        if db and farm_id:
            try:
                prompt = result.get("_prompt", "")
                await db.store_llm_conversation(
                    farm_id=farm_id,
                    prompt_sent=prompt,
                    response_received=result.get("advice", ""),
                    model_used=result.get("model", self.groq_model if self._groq_available else self.ollama_model),
                    context_used={
                        "shared_context": shared_context,
                        "rich_context_keys": list(rich_context.keys()) if rich_context else [],
                    },
                    latency_ms=result.get("_latency_ms"),
                )
            except Exception as e:
                print(f"⚠️ Failed to log LLM conversation: {e}")

        # Remove internal fields before returning
        result.pop("_prompt", None)
        result.pop("_latency_ms", None)

        return result

    def _generate_with_llm(
        self, shared_context: Dict[str, Any], rich_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use LLM (Groq or Ollama) for unified reasoning — now with rich context."""
        prompt = self._build_llm_prompt(shared_context, rich_context)

        start_time = time.time()
        
        # Method 1: Groq API (Primary)
        if self._groq_available:
            print(f"🧠 Sending data to Groq LLM ({self.groq_model})...")
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are AgroBrain OS, an expert agricultural AI advisor for an Indian farm. Always provide accurate, data-driven advice without hallucinating."
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.groq_model,
                    temperature=0.3,
                    max_completion_tokens=512,
                )
                
                latency = (time.time() - start_time) * 1000
                print("✅ Groq successfully generated multi-agent advice!")
                return {
                    "source": "groq",
                    "model": self.groq_model,
                    "advice": chat_completion.choices[0].message.content.strip(),
                    "confidence": "high",
                    "timestamp": datetime.now().isoformat(),
                    "_prompt": prompt,
                    "_latency_ms": latency,
                }
            except Exception as e:
                print(f"❌ Groq LLM call failed. Falling back to Ollama/Rule-based. Error: {str(e)[:100]}")
                
        # Method 2: Ollama (Fallback)
        if self._ollama_available:
            print(f"🧠 Sending data to local Ollama LLM ({self.ollama_model})...")
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 512},
                    },
                    timeout=120,
                )

                latency = (time.time() - start_time) * 1000  # ms

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Ollama successfully generated multi-agent advice!")
                    return {
                        "source": "ollama",
                        "model": self.ollama_model,
                        "advice": result.get("response", "").strip(),
                        "confidence": "high",
                        "timestamp": datetime.now().isoformat(),
                        "_prompt": prompt,
                        "_latency_ms": latency,
                    }
                else:
                    print(f"⚠️ Ollama returned error status: {response.status_code}")
            except Exception as e:
                print(f"❌ Ollama LLM call failed. Falling back to rule-based. Error: {str(e)[:100]}")

        return self._generate_rule_based(shared_context)

    def _build_llm_prompt(
        self, shared_context: Dict[str, Any], rich_context: Dict[str, Any] = None
    ) -> str:
        """
        Build prompt for LLM — now includes historical context from PostgreSQL.
        """
        # ── Section 1: Crop Timeline ──
        crop_section = ""
        if rich_context and rich_context.get("crop_timeline"):
            ct = rich_context["crop_timeline"]
            if ct.get("status") != "no_active_crop":
                crop_section = f"""
CROP TIMELINE:
- Crop: {ct.get('crop', 'N/A')}
- Planted: {ct.get('planted_date', 'N/A')} ({ct.get('days_since_planting', '?')} days ago)
- Growth Stage: {ct.get('growth_stage', 'N/A')}
- Expected Harvest: {ct.get('expected_harvest', 'N/A')} ({ct.get('days_to_harvest', '?')} days remaining)
"""

        # ── Section 2: Sensor Trends (7-day) ──
        trends_section = ""
        if rich_context and rich_context.get("sensor_trends_7d"):
            st = rich_context["sensor_trends_7d"]
            if st.get("status") != "no_data":
                moisture = st.get("soil_moisture", {})
                temp = st.get("air_temperature", {})
                trends_section = f"""
7-DAY SENSOR TRENDS ({st.get('reading_count', 0)} readings):
- Soil Moisture: avg {moisture.get('avg', 'N/A')}%, range {moisture.get('min', '?')}-{moisture.get('max', '?')}%, trend: {moisture.get('trend', 'N/A')}
- Air Temperature: avg {temp.get('avg', 'N/A')}°C, range {temp.get('min', '?')}-{temp.get('max', '?')}°C
- Soil pH: avg {st.get('soil_ph', {}).get('avg', 'N/A')}
- NPK: N={st.get('npk', {}).get('nitrogen_avg', 'N/A')}, P={st.get('npk', {}).get('phosphorus_avg', 'N/A')}, K={st.get('npk', {}).get('potassium_avg', 'N/A')}
- Total Rainfall: {st.get('total_rainfall_mm', 0)} mm
"""

        # ── Section 3: Past Recommendations ──
        past_recs_section = ""
        if rich_context and rich_context.get("past_recommendations"):
            recs = rich_context["past_recommendations"]
            past_recs_section = "\nPAST RECOMMENDATIONS (most recent):\n"
            for r in recs:
                past_recs_section += f"- [{r.get('date', '?')}] {r.get('agent', '?')}: {r.get('text', '')[:100]}\n"

        # ── Section 4: Past Actions ──
        past_actions_section = ""
        if rich_context and rich_context.get("past_actions"):
            acts = rich_context["past_actions"]
            past_actions_section = "\nFARMER'S RECENT ACTIONS:\n"
            for a in acts:
                past_actions_section += f"- [{a.get('date', '?')}] {a.get('action', '?')}: {a.get('details', '')[:80]}\n"

        # ── Section 5: Weather API Data ──
        weather_api_section = ""
        if rich_context and rich_context.get("recent_weather_api"):
            rw = rich_context["recent_weather_api"]
            if rw.get("status") != "no_cached_weather":
                ds = rw.get("data_summary", {})
                weather_api_section = f"""
LATEST WEATHER API DATA (fetched: {rw.get('fetched_at', 'N/A')}):
- Temperature: {ds.get('temperature', 'N/A')}°C
- Humidity: {ds.get('humidity', 'N/A')}%
- Condition: {ds.get('description', 'N/A')}
- Rain Probability: {ds.get('rain_probability', 'N/A')}
"""

        return f"""<s>[INST] You are an expert agricultural AI advisor for an Indian farm. Analyze ALL of the following context — including historical trends and past decisions — and provide unified, actionable farming advice.

CURRENT SENSOR SNAPSHOT (Agent Context Bus):
{json.dumps(shared_context, indent=2)}
{crop_section}{trends_section}{weather_api_section}{past_recs_section}{past_actions_section}
Based on ALL of this data:
1. Consider the crop growth stage and days to harvest when making recommendations
2. Look at 7-day sensor TRENDS (not just current values) to identify patterns
3. Reference past recommendations — do NOT repeat advice that was already given recently unless the situation has worsened
4. If the farmer already took an action (see RECENT ACTIONS), acknowledge it and assess its effectiveness
5. Identify any conflicts between agent recommendations and resolve them

Output your response in this format:
1. 📊 Agent Outputs Summary (briefly summarize what each agent suggested)
2. 🧠 Historical Context Analysis (what trends and past data tell us)
3. ⚖️ Conflict Resolution (how conflicts were resolved)
4. ✅ Final Recommendation (clear, single actionable decision for the farmer NOW)
[/INST]"""

    def _generate_rule_based(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback for unified advice"""
        advice_points = []
        priority = "normal"

        # Critical checks
        if context.get("disease_alert") and context.get("risk_level") == "high":
            advice_points.append("🚨 CRITICAL: Disease detected - prioritize treatment immediately")
            priority = "critical"

        soil_moisture = context.get("soil_moisture", 0)
        if soil_moisture < 25 and soil_moisture > 0:
            advice_points.append("🚨 CRITICAL: Soil moisture critically low - irrigate immediately")
            priority = "critical"

        temperature = context.get("temperature", 0)
        if temperature > 42:
            advice_points.append("🚨 CRITICAL: Extreme heat - increase water immediately")
            priority = "critical"

        rain_in_24h = context.get("rain_in_24h", False)
        if rain_in_24h:
            advice_points.append("⏸️ Rain expected in 24h - avoid fertilizer")

        humidity = context.get("humidity", 0)
        disease_alert = context.get("disease_alert", False)
        if humidity > 85 and disease_alert:
            advice_points.append("🌫️ High humidity + disease risk - spray only morning/evening")

        fertilizer_advice = context.get("fertilizer_advice", "")
        disease_severity = context.get("risk_level", "none")
        if "recommended" in fertilizer_advice.lower() and not rain_in_24h:
            if disease_severity != "high":
                advice_points.append("🌱 Fertilizer recommended - apply according to schedule")

        irrigation_needed = context.get("irrigation_needed", False)
        if irrigation_needed and not rain_in_24h:
            if soil_moisture < 80:
                duration = context.get("irrigation_duration", 30)
                advice_points.append(f"💧 Irrigation needed - run for {duration} minutes")

        if (40 <= soil_moisture <= 70 and 15 <= temperature <= 35
            and not context.get("disease_alert") and not rain_in_24h):
            advice_points.append("✅ Conditions optimal - maintain current practices")

        final_recommendation = " | ".join(advice_points) if advice_points else "All systems normal"

        formatted_advice = (
            "1. 📊 Agent Outputs Summary\n"
            f"- Weather: Rain expected = {context.get('rain_in_24h', False)}\n"
            f"- Disease: Alert = {context.get('disease_alert', False)}\n"
            f"- Fertilizer: {context.get('fertilizer_advice', 'No advice')}\n\n"
            "2. 🧠 Historical Context Analysis\n"
            "Rule-based fallback — no historical context available (LLM offline).\n\n"
            "3. ⚖️ Conflict Resolution\n"
            "Rule-based fallback applied. Prioritized disease treatment and/or postponed sensitive activities if raining.\n\n"
            "4. ✅ Final Recommendation\n"
            + final_recommendation
        )

        return {
            "source": "rule_based",
            "advice": formatted_advice,
            "priority": priority,
            "confidence": "medium",
            "timestamp": datetime.now().isoformat(),
            "rules_applied": self._get_applied_rules(context),
        }

    def _get_applied_rules(self, context: Dict[str, Any]) -> List[str]:
        """List which rules were applied"""
        rules = []
        if context.get("rain_in_24h", False):
            rules.append("rain_delay")
        if context.get("risk_level") == "high":
            rules.append("disease_priority")
        if context.get("temperature", 0) > 40:
            rules.append("heat_irrigation_timing")
        if context.get("soil_moisture", 0) > 80:
            rules.append("saturation_skip")
        if context.get("nitrogen", 0) > 250:
            rules.append("npk_excess_skip")
        return rules
