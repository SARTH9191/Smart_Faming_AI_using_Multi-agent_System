"""
🎤 VOICE ASSISTANT AGENT — LLM-Powered, Profile-Aware, Multilingual
====================================================================
Powered by Groq (llama3-8b-8192) for fast, free inference.
Receives full farmer profile + sensor data + crops context.
Only answers agriculture-related questions.
Responds in the same language the farmer spoke.
Falls back to rule-based system if LLM is unavailable.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import re
import os
import json
import requests


# ── Language detection helpers ──────────────────────────────────────

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}

AGRI_OFF_TOPIC_REDIRECT = {
    "en": (
        "I'm your Smart Farming Assistant and can only help with agriculture topics like "
        "crops, soil, weather, irrigation, market prices, diseases, and government schemes. "
        "Please ask me something related to your farm!"
    ),
    "hi": (
        "मैं आपका स्मार्ट फार्मिंग असिस्टेंट हूं और केवल कृषि विषयों पर मदद कर सकता हूं जैसे "
        "फसल, मिट्टी, मौसम, सिंचाई, बाजार भाव, रोग और सरकारी योजनाएं। "
        "कृपया अपने खेत से संबंधित कोई प्रश्न पूछें!"
    ),
    "mr": (
        "मी तुमचा स्मार्ट फार्मिंग असिस्टंट आहे आणि केवळ कृषी विषयांवर मदत करू शकतो जसे "
        "पिके, माती, हवामान, सिंचन, बाजार भाव, रोग आणि सरकारी योजना. "
        "कृपया तुमच्या शेताशी संबंधित प्रश्न विचारा!"
    ),
}


class VoiceAssistantAgent:
    """
    Multilingual voice assistant backed by Groq LLM.
    Falls back to rule-based keyword matching if LLM is unavailable.
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL = "llama-3.1-8b-instant"

    def __init__(self, database):
        self.db = database
        self.name = "Voice Assistant (AI)"
        self.groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY", "")

        # ── Keyword command map (fallback) ──────────────────────────
        self.commands = {
            "en": {
                "weather": ["weather", "forecast", "rain", "temperature", "climate"],
                "water": ["irrigation", "water", "irrigate", "watering", "moisture"],
                "soil": ["soil", "moisture", "ph", "nutrients", "npk"],
                "disease": ["disease", "sick", "problem", "pest", "fungus"],
                "market": ["price", "market", "sell", "mandi", "rate", "crop price"],
                "schemes": ["scheme", "subsidy", "government", "loan", "yojana"],
                "yield": ["yield", "harvest", "prediction", "output", "production"],
                "help": ["help", "assist", "how", "what"],
            },
            "hi": {
                "weather": ["mausam", "barish", "tapman", "मौसम", "बारिश", "तापमान", "weather"],
                "water": ["pani", "sinchai", "paani", "पानी", "सिंचाई", "irrigation"],
                "soil": ["mitti", "bhoomi", "मिट्टी", "भूमि", "soil", "npk", "पोषक"],
                "disease": ["bimari", "rog", "keeda", "बीमारी", "रोग", "कीड़ा", "disease"],
                "market": ["daam", "bazaar", "mandi", "kimmat", "दाम", "बाजार", "मंडी", "किम्मत", "market", "price", "भाव"],
                "schemes": ["yojana", "sahayata", "loan", "योजना", "साहायता", "scheme", "subsidy"],
                "yield": ["paidawar", "fasal", "पैदावार", "फसल", "उत्पादन", "yield"],
                "help": ["madad", "sahayata", "kaise", "मदद", "साहायता", "कैसे", "help"],
            },
            "mr": {
                "weather": ["hawa", "paus", "tapa", "हवा", "पाऊस", "तापमान", "मौसम", "weather"],
                "water": ["pani", "panyacha", "पाणी", "पाण्याचा", "सिंचन", "sinchan", "irrigation"],
                "soil": ["maati", "jamin", "माती", "जमीन", "मृदा", "soil", "npk"],
                "disease": ["rog", "ajar", "रोग", "आजार", "बीमारी", "disease"],
                "market": ["kimmat", "bazaar", "bhav", "किंमत", "बाजार", "मंडी", "भाव", "market", "price"],
                "schemes": ["yojna", "sahaya", "योजना", "साहाय्य", "सरकारी", "scheme"],
                "yield": ["utpadan", "pik", "उत्पादन", "पीक", "काढणी", "yield"],
                "help": ["madad", "kashi", "मदत", "कशी", "help", "काय"],
            },
        }

    # ════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ════════════════════════════════════════════════════════════════

    def process_command(
        self,
        text: str,
        language: str = "en",
        farmer_profile: Optional[Dict[str, Any]] = None,
        sensor_data: Optional[Dict[str, Any]] = None,
        crops: Optional[List[Dict[str, Any]]] = None,
        recent_recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Process a voice/text command.
        With LLM available: uses Groq + full farm context.
        Without LLM: falls back to keyword matching.
        """

        # Auto-detect language if text has Devanagari
        detected_lang = self._detect_language(text)
        if detected_lang and detected_lang != language:
            print(f"🔍 Auto-detected language: {detected_lang} (overriding {language})")
            language = detected_lang

        result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "input_text": text,
            "language": language,
            "detected_language": detected_lang,
            "intent": "llm",
            "response_text": "",
            "voice_summary": "",
            "action_taken": "",
            "data": {},
            "blockchain_logged": False,
            "green_tokens_earned": 0,
            "llm_used": False,
        }

        # ── Check for eco-action FIRST (blockchain logging) ─────────
        text_lower = text.lower()
        eco_action = self._detect_eco_action(text_lower, language)
        if eco_action:
            return self._handle_eco_action(eco_action, language, result)

        # ── Try LLM path ───────────────────────────────────────────
        if self.groq_api_key:
            try:
                llm_response = self._call_groq_llm(
                    text=text,
                    language=language,
                    farmer_profile=farmer_profile or {},
                    sensor_data=sensor_data or {},
                    crops=crops or [],
                    recent_recommendations=recent_recommendations or [],
                )
                result["response_text"] = llm_response
                result["voice_summary"] = llm_response
                result["action_taken"] = "Groq LLM (llama3-8b-8192) responded with farm context"
                result["llm_used"] = True
                result["intent"] = "llm_response"
                return result
            except Exception as e:
                print(f"⚠️ Groq LLM failed: {e}. Falling back to rule-based.")

        # ── Fallback: Rule-based keyword matching ───────────────────
        return self._rule_based_process(text, language, result, sensor_data or {})

    # ════════════════════════════════════════════════════════════════
    # GROQ LLM ENGINE
    # ════════════════════════════════════════════════════════════════

    def _call_groq_llm(
        self,
        text: str,
        language: str,
        farmer_profile: Dict[str, Any],
        sensor_data: Dict[str, Any],
        crops: List[Dict[str, Any]],
        recent_recommendations: List[Dict[str, Any]],
    ) -> str:
        """Call Groq Llama3 with rich farm context and agriculture guardrails."""

        system_prompt = self._build_system_prompt(
            language, farmer_profile, sensor_data, crops, recent_recommendations
        )

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.4,
            "max_tokens": 350,   # Keep responses concise for TTS
            "top_p": 0.9,
        }

        print(f"🧠 Calling Groq LLM ({self.GROQ_MODEL}) for voice command...")
        response = requests.post(
            self.GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code != 200:
            error_detail = response.text[:200]
            raise RuntimeError(f"Groq API error {response.status_code}: {error_detail}")

        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
        print(f"✅ Groq LLM responded ({len(answer)} chars)")
        return answer

    def _build_system_prompt(
        self,
        language: str,
        farmer_profile: Dict[str, Any],
        sensor_data: Dict[str, Any],
        crops: List[Dict[str, Any]],
        recent_recommendations: List[Dict[str, Any]],
    ) -> str:
        """Build a personalized, context-rich system prompt for the LLM."""

        lang_name = LANGUAGE_NAMES.get(language, "English")
        farmer_name = farmer_profile.get("name", "Farmer")
        location = farmer_profile.get("location", "India")
        farm_size = farmer_profile.get("farm_size", "unknown")
        lat = farmer_profile.get("latitude")
        lon = farmer_profile.get("longitude")

        # Format crops
        crops_text = "No crops registered."
        if crops:
            crop_lines = []
            for c in crops[:5]:  # limit to 5
                line = f"  - {c.get('crop_type', '?')} ({c.get('status', '?')})"
                if c.get("variety"):
                    line += f", variety: {c['variety']}"
                if c.get("planted_date"):
                    line += f", planted: {c['planted_date'][:10]}"
                if c.get("area_hectares"):
                    line += f", area: {c['area_hectares']} ha"
                crop_lines.append(line)
            crops_text = "\n".join(crop_lines)

        # Format sensor data
        sensor_text = "No sensor data available."
        if sensor_data:
            sensor_text = (
                f"  - Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%\n"
                f"  - Soil Temperature: {sensor_data.get('soil_temperature', 'N/A')}°C\n"
                f"  - Soil pH: {sensor_data.get('soil_ph', 'N/A')}\n"
                f"  - Nitrogen (N): {sensor_data.get('npk_nitrogen', 'N/A')} mg/kg\n"
                f"  - Phosphorus (P): {sensor_data.get('npk_phosphorus', 'N/A')} mg/kg\n"
                f"  - Potassium (K): {sensor_data.get('npk_potassium', 'N/A')} mg/kg\n"
                f"  - Humidity: {sensor_data.get('humidity', 'N/A')}%\n"
                f"  - Air Temperature: {sensor_data.get('air_temperature', 'N/A')}°C\n"
                f"  - Rainfall: {sensor_data.get('rainfall', 'N/A')} mm\n"
                f"  - Reading Timestamp: {sensor_data.get('timestamp', 'N/A')}"
            )

        # Format recent recommendations
        rec_text = "No recent recommendations."
        if recent_recommendations:
            rec_lines = [
                f"  - [{r.get('agent_name', '?')}] {r.get('recommendation_text', '')[:120]}"
                for r in recent_recommendations[:3]
            ]
            rec_text = "\n".join(rec_lines)

        location_detail = location
        if lat and lon:
            location_detail += f" (coordinates: {lat:.4f}°N, {lon:.4f}°E)"

        # Core system prompt
        prompt = f"""You are an expert Smart Farming AI Assistant for {farmer_name}'s farm.

=== FARM PROFILE ===
Farmer Name: {farmer_name}
Farm Location: {location_detail}
Farm Size: {farm_size} hectares
Preferred Language: {lang_name}

=== ACTIVE CROPS ===
{crops_text}

=== LATEST SENSOR READINGS ===
{sensor_text}

=== RECENT AI RECOMMENDATIONS ===
{rec_text}

=== YOUR RULES ===
1. You ONLY answer questions related to agriculture, farming, crops, soil health, weather, irrigation, fertilizers, crop diseases, market prices, government schemes for farmers, and sustainable farming practices.
2. If the user asks ANYTHING unrelated to farming or agriculture (e.g., jokes, politics, sports, general knowledge), politely decline and redirect them to farming topics. Do NOT answer off-topic questions under any circumstances.
3. ALWAYS respond in {lang_name}. If the user wrote in {lang_name}, respond in {lang_name}. Do not switch languages unless explicitly asked.
4. Address the farmer by their name ({farmer_name}) naturally in your response.
5. Use the actual sensor data and crop data above to give specific, accurate, personalized advice — not generic advice.
6. Keep responses concise (2-4 sentences) and conversational — they will be read aloud via text-to-speech.
7. If sensor data shows a critical condition (e.g., soil moisture < 25%), proactively alert the farmer even if they didn't ask.
8. Today's date is {datetime.now().strftime('%B %d, %Y')}.
"""
        return prompt

    # ════════════════════════════════════════════════════════════════
    # RULE-BASED FALLBACK
    # ════════════════════════════════════════════════════════════════

    def _rule_based_process(
        self,
        text: str,
        language: str,
        result: Dict[str, Any],
        sensor_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Keyword-based fallback when LLM is unavailable."""
        text_lower = text.lower()
        intent = self._detect_intent(text_lower, language)
        result["intent"] = intent

        if intent == "weather":
            try:
                from agents.weather_forecast_agent import WeatherForecastAgent
                weather_agent = WeatherForecastAgent()
                weather_data = weather_agent.predict_weather("Delhi", 24)
                recs = weather_data.get("recommendations_multilingual", {}).get(
                    language, weather_data.get("recommendations", [])
                )
                summary = weather_data.get("summary", {})
                temp = summary.get("avg_temperature", "N/A")
                result["data"] = {"summary": summary, "recommendations": recs[:2]}
                if language == "hi":
                    result["voice_summary"] = f"औसत तापमान {temp}°C है। {recs[0] if recs else 'मौसम ठीक है।'}"
                elif language == "mr":
                    result["voice_summary"] = f"सरासरी तापमान {temp}°C आहे। {recs[0] if recs else 'हवामान चांगले आहे।'}"
                else:
                    result["voice_summary"] = f"Average temperature is {temp}°C. {recs[0] if recs else 'Weather looks good.'}"
            except Exception as e:
                result["voice_summary"] = f"Weather data unavailable: {e}"
            result["action_taken"] = "Rule-based: fetched weather"

        elif intent in ("water", "soil"):
            moisture = sensor_data.get("soil_moisture", "N/A")
            ph = sensor_data.get("soil_ph", "N/A")
            if language == "hi":
                result["voice_summary"] = f"मिट्टी में नमी {moisture}% और पीएच {ph} है।"
            elif language == "mr":
                result["voice_summary"] = f"मातीत ओलावा {moisture}% आणि पीएच {ph} आहे।"
            else:
                result["voice_summary"] = f"Soil moisture is {moisture}% and pH is {ph}."
            result["action_taken"] = "Rule-based: soil data"

        elif intent == "market":
            try:
                from agents.market_forecast_agent import MarketForecastAgent
                market_agent = MarketForecastAgent()
                market_data = market_agent.forecast_prices("wheat", 7)
                price = market_data.get("current_price", "N/A")
                trend = market_data.get("trend", "stable")
                if language == "hi":
                    result["voice_summary"] = f"गेहूं का भाव {price} रुपये है। बाजार {trend} है।"
                elif language == "mr":
                    result["voice_summary"] = f"गव्हाची किंमत {price} रुपये आहे। बाजार {trend} आहे।"
                else:
                    result["voice_summary"] = f"Wheat price is {price}. Market trend: {trend}."
            except Exception:
                result["voice_summary"] = "Market data not available right now."
            result["action_taken"] = "Rule-based: market data"

        elif intent == "schemes":
            try:
                from agents.govt_scheme_agent import GovtSchemeAgent
                govt_agent = GovtSchemeAgent()
                schemes_data = govt_agent.get_applicable_schemes("all", "all")
                schemes = [s["name"] for s in schemes_data.get("priority_schemes", [])][:2]
                helpline = schemes_data.get("application_support", {}).get("helpline", "N/A")
                if language == "hi":
                    result["voice_summary"] = f"आपके लिए योजनाएं: {', '.join(schemes)}। हेल्पलाइन: {helpline}।"
                elif language == "mr":
                    result["voice_summary"] = f"तुमच्यासाठी योजना: {', '.join(schemes)}। हेल्पलाइन: {helpline}।"
                else:
                    result["voice_summary"] = f"Top schemes for you: {', '.join(schemes)}. Helpline: {helpline}."
            except Exception:
                result["voice_summary"] = "Government scheme info not available."
            result["action_taken"] = "Rule-based: govt schemes"

        else:
            # Unknown intent — show redirect
            result["voice_summary"] = AGRI_OFF_TOPIC_REDIRECT.get(language, AGRI_OFF_TOPIC_REDIRECT["en"])
            result["action_taken"] = "Rule-based: unknown intent"

        result["response_text"] = result["voice_summary"]
        return result

    # ════════════════════════════════════════════════════════════════
    # ECO-ACTION HANDLING (BLOCKCHAIN)
    # ════════════════════════════════════════════════════════════════

    def _handle_eco_action(
        self, eco_action: Dict, language: str, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        result["intent"] = "eco_action"
        result["eco_action_type"] = eco_action["action_type"]
        result["green_tokens_earned"] = eco_action["tokens"]

        blockchain_result = self._log_to_blockchain(eco_action, language)
        result["blockchain_logged"] = blockchain_result.get("success", False)
        result["data"] = blockchain_result

        action_name = eco_action.get("action_name", "eco action")
        tokens = eco_action["tokens"]

        if language == "hi":
            msg = f"बधाई हो! आपने {action_name} के लिए {tokens} ग्रीन टोकन कमाए हैं। आपकी टिकाऊ खेती पर्यावरण के लिए बहुत अच्छी है!"
        elif language == "mr":
            msg = f"अभिनंदन! तुम्ही {action_name} साठी {tokens} ग्रीन टोकन मिळवले आहेत। तुमच्या शाश्वत शेतीचा पर्यावरणावर चांगला परिणाम होत आहे!"
        else:
            msg = f"Excellent! You've earned {tokens} Green Tokens for {action_name}. Your sustainable farming practices are helping the environment!"

        result["response_text"] = msg
        result["voice_summary"] = msg
        result["action_taken"] = f"Logged eco-action and awarded {tokens} tokens"
        return result

    def _log_to_blockchain(self, eco_action: Dict, language: str) -> Dict[str, Any]:
        try:
            from agents.blockchain_agent import BlockchainAgent
            blockchain_agent = BlockchainAgent()
            farm_id = "FARM001"
            result_bc = blockchain_agent.add_transaction(
                farm_id=farm_id,
                action_type=eco_action["action_type"],
                action_details=eco_action["action_name"],
                green_tokens=eco_action["tokens"],
            )
            if result_bc.get("status") == "success":
                return {
                    "success": True,
                    "block_index": result_bc.get("block_index"),
                    "tokens_earned": result_bc.get("tokens_earned"),
                    "new_balance": result_bc.get("new_balance"),
                }
            return {"success": False, "error": "Blockchain logging failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ════════════════════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════════════════════

    def _detect_intent(self, text: str, language: str) -> str:
        commands = self.commands.get(language, self.commands["en"])
        for intent, keywords in commands.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return intent
        return "unknown"

    def _detect_language(self, text: str) -> str:
        """Auto-detect language from character script."""
        devanagari_chars = sum(1 for char in text if "\u0900" <= char <= "\u097F")
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars == 0:
            return "en"

        devanagari_ratio = devanagari_chars / total_chars

        if devanagari_ratio > 0.3:
            marathi_indicators = ["आहे", "आहेत", "काय", "कशी", "तुम्ही", "माती", "पाऊस", "मदत"]
            hindi_indicators = ["है", "हैं", "क्या", "कैसे", "आप", "मिट्टी", "बारिश", "मदद"]
            m_count = sum(1 for w in marathi_indicators if w in text)
            h_count = sum(1 for w in hindi_indicators if w in text)
            if m_count > h_count:
                return "mr"
            elif h_count > m_count:
                return "hi"
            return "hi"

        text_lower = text.lower()
        marathi_roman = ["hava", "paus", "maati", "kashi", "tumhi", "mala"]
        hindi_roman = ["mausam", "barish", "mitti", "kaise", "aap", "mujhe"]
        mr = sum(1 for w in marathi_roman if w in text_lower)
        hi = sum(1 for w in hindi_roman if w in text_lower)

        if mr > hi and mr > 0:
            return "mr"
        if hi > 0:
            return "hi"
        return "en"

    def _detect_eco_action(self, text: str, language: str):
        """Detect eco-friendly actions for blockchain logging."""
        eco_actions = {
            "drip_irrigation": {
                "keywords": {"en": ["drip irrigation", "drip irrigate", "installed drip", "use drip"],
                             "hi": ["drip sinchai", "drip irrigation", "थेंब सिंचाई"],
                             "mr": ["थेंब सिंचन", "ड्रिप सिंचन", "drip irrigation"]},
                "tokens": 20,
                "action_name": {"en": "Drip Irrigation", "hi": "थेंब सिंचाई", "mr": "थेंब सिंचन"},
            },
            "organic_fertilizer": {
                "keywords": {"en": ["organic fertilizer", "organic compost", "bio fertilizer", "vermicompost"],
                             "hi": ["organic khad", "jaivic khad", "जैविक खाद"],
                             "mr": ["जैविक खत", "सेंद्रिय खत", "कंपोस्ट"]},
                "tokens": 15,
                "action_name": {"en": "Organic Fertilizer", "hi": "जैविक खाद", "mr": "जैविक खत"},
            },
            "solar_pump": {
                "keywords": {"en": ["solar pump", "solar water pump", "installed solar pump"],
                             "hi": ["solar pump", "सौर पंप"],
                             "mr": ["सौर पंप", "solar pump"]},
                "tokens": 30,
                "action_name": {"en": "Solar Pump", "hi": "सौर पंप", "mr": "सौर पंप"},
            },
            "rainwater_harvesting": {
                "keywords": {"en": ["rainwater harvest", "rain water collection", "collect rainwater"],
                             "hi": ["बारिश का पानी संग्रहण", "rainwater harvest"],
                             "mr": ["पावसाचे पाणी संचयन", "rainwater harvest"]},
                "tokens": 25,
                "action_name": {"en": "Rainwater Harvesting", "hi": "वर्षा जल संचयन", "mr": "पावसाचे पाणी संचयन"},
            },
            "composting": {
                "keywords": {"en": ["composting", "compost pit", "started compost", "making compost"],
                             "hi": ["compost", "खाद बनाना", "कम्पोस्ट"],
                             "mr": ["कंपोस्ट", "खत तयार", "composting"]},
                "tokens": 15,
                "action_name": {"en": "Composting", "hi": "कम्पोस्टिंग", "mr": "कंपोस्टिंग"},
            },
            "crop_rotation": {
                "keywords": {"en": ["crop rotation", "rotate crops", "rotated crop"],
                             "hi": ["fasal chakra", "फसल चक्र", "crop rotation"],
                             "mr": ["पीक फेरबदल", "crop rotation"]},
                "tokens": 12,
                "action_name": {"en": "Crop Rotation", "hi": "फसल चक्र", "mr": "पीक फेरबदल"},
            },
            "mulching": {
                "keywords": {"en": ["mulching", "applied mulch", "mulch cover"],
                             "hi": ["mulching", "मल्चिंग"],
                             "mr": ["mulching", "मल्चिंग"]},
                "tokens": 10,
                "action_name": {"en": "Mulching", "hi": "मल्चिंग", "mr": "मल्चिंग"},
            },
            "zero_tillage": {
                "keywords": {"en": ["zero tillage", "no till", "no tillage"],
                             "hi": ["zero tillage", "बिना जोताई"],
                             "mr": ["zero tillage", "शून्य नांगरणी"]},
                "tokens": 18,
                "action_name": {"en": "Zero Tillage", "hi": "बिना जोताई", "mr": "शून्य नांगरणी"},
            },
        }

        for action_type, action_data in eco_actions.items():
            keywords = action_data["keywords"].get(language, action_data["keywords"]["en"])
            for keyword in keywords:
                if keyword.lower() in text:
                    return {
                        "action_type": action_type,
                        "action_name": action_data["action_name"].get(language, action_data["action_name"]["en"]),
                        "tokens": action_data["tokens"],
                    }
        return None
