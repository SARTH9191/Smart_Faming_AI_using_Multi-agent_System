"""
Supervisor Agent - Autonomous ReAct Agent
==========================================
Powered by Groq LLM with tool use capabilities.
This is the core "brain" that orchestrates all tools autonomously.
"""

import os
import json
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

# Import all tools
from graph.tools import (
    get_current_weather,
    get_weather_forecast,
    analyze_soil,
    calculate_irrigation,
    recommend_fertilizer,
    detect_disease,
    predict_yield,
    get_market_forecast,
    assess_climate_risk,
    resolve_conflicts,
)


# Load API keys
def _load_api_keys():
    """Load API keys from config"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "api_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("groq_api_key", ""), config.get("openweather_api_key", "")
    except:
        return "", ""


GROQ_API_KEY, OPENWEATHER_API_KEY = _load_api_keys()

# System prompt for the supervisor
SYSTEM_PROMPT = """You are AgroBrain OS, an expert agricultural AI advisor for Indian farms.

Your role is to help farmers make data-driven decisions by:
1. Checking current weather conditions before any irrigation decisions
2. Analyzing soil health from sensor data
3. Detecting crop diseases based on symptoms
4. Predicting yields and market prices
5. Assessing climate risks

You have access to the following tools:
- get_current_weather: Current weather conditions
- get_weather_forecast: 24-48 hour weather forecast
- analyze_soil: Analyze soil health from sensor data
- calculate_irrigation: Decide if/when to irrigate
- recommend_fertilizer: Calculate NPK requirements
- detect_disease: Identify crop diseases
- predict_yield: Forecast harvest yield
- get_market_forecast: Predict market prices
- assess_climate_risk: Calculate climate risks
- resolve_conflicts: Resolve conflicts between recommendations

IMPORTANT RULES:
1. Always get weather data FIRST before making irrigation decisions
2. Consider weather forecast before recommending fertilizer application
3. If rain is expected (>60%), postpone irrigation
4. If disease symptoms are reported, prioritize disease detection
5. Provide specific, actionable recommendations in simple language

Think step by step. Use tools to gather data before making recommendations.
Always explain your reasoning to the farmer."""


class SupervisorAgent:
    """
    Autonomous supervisor agent that uses ReAct pattern
    to make decisions for the farm.
    """

    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.tools = [
            get_current_weather,
            get_weather_forecast,
            analyze_soil,
            calculate_irrigation,
            recommend_fertilizer,
            detect_disease,
            predict_yield,
            get_market_forecast,
            assess_climate_risk,
            resolve_conflicts,
        ]
        self.agent = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the ReAct agent with Groq"""
        if not self.groq_api_key:
            print("⚠️ SupervisorAgent: No Groq API key - falling back to rule-based")
            self.agent = None
            return

        try:
            # Create Groq LLM
            llm = ChatGroq(
                model="llama-3.1-8b-instant", api_key=self.groq_api_key, temperature=0.3
            )

            # Create ReAct agent
            self.agent = create_react_agent(llm, tools=self.tools, prompt=SYSTEM_PROMPT)

            print("OK SupervisorAgent initialized with Groq (llama-3.1-8b-instant)")

        except Exception as e:
            print(f"X SupervisorAgent initialization failed: {e}")
            self.agent = None

    @property
    def is_available(self) -> bool:
        """Check if agent is available"""
        return self.agent is not None

    async def run_autonomous(
        self, user_query: str, farm_id: str = "FARM001"
    ) -> Dict[str, Any]:
        """
        Run the agent autonomously with the user's query.

        Args:
            user_query: Natural language query from farmer
            farm_id: Farm identifier

        Returns:
            Dict with response and metadata
        """
        result = {
            "status": "success",
            "farm_id": farm_id,
            "query": user_query,
            "response": "",
            "tools_used": [],
            "timestamp": "",
        }

        if not self.is_available:
            # Fallback to simple rule-based response
            result["response"] = (
                "AI advisor temporarily unavailable. Please check API configuration."
            )
            result["status"] = "error"
            return result

        try:
            # Run the agent
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=user_query)]}
            )

            # Extract response
            messages = response.get("messages", [])
            if messages:
                result["response"] = messages[-1].content

            # Track tools used
            for msg in messages:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        result["tools_used"].append(tc.get("name", "unknown"))

            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["response"] = f"Error: {str(e)}"

        return result

    async def chat(
        self, message: str, history: List[Dict] = None, farm_id: str = "FARM001"
    ) -> Dict[str, Any]:
        """
        Chat with the agent conversationally.

        Args:
            message: User message
            history: Conversation history

        Returns:
            Agent response
        """
        # Use run_autonomous which has better error handling
        return await self.run_autonomous(message, farm_id)


# Singleton instance
_supervisor = None


def get_supervisor() -> SupervisorAgent:
    """Get or create supervisor instance"""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor


# For direct tool testing
async def test_tools():
    """Test all tools"""
    print("🧪 Testing tools...")

    # Test weather
    weather = await get_current_weather.ainvoke("Pune")
    print(f"✅ Weather: {weather}")

    # Test forecast
    forecast = await get_weather_forecast.ainvoke({"location": "Pune", "hours": 24})
    print(f"✅ Forecast: {forecast}")

    # Test soil
    soil = await analyze_soil.ainvoke(
        {
            "soil_moisture": 35,
            "soil_ph": 6.5,
            "air_temperature": 28,
            "npk_nitrogen": 45,
            "npk_phosphorus": 30,
            "npk_potassium": 40,
        }
    )
    print(f"✅ Soil: {soil}")

    # Test irrigation
    irr = await calculate_irrigation.ainvoke(
        {"soil_moisture": 30, "air_temperature": 32, "humidity": 50},
        {"data": {"rain_expected": False, "avg_rain_probability": 20}},
    )
    print(f"✅ Irrigation: {irr}")

    print("✅ All tools tested!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_tools())
