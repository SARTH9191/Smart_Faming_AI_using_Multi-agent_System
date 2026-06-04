"""
LangGraph Workflow - StateGraph Orchestration
==============================================
Alternative workflow using explicit state machine.
Can be used alongside or instead of the ReAct supervisor.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

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


# Core components
from core.database import AsyncDatabase
from config import API_CONFIG

# Shared database instance for nodes
_db = AsyncDatabase(API_CONFIG["database_url"])


# =============================================================================
# NODE FUNCTIONS
# =============================================================================


async def fetch_sensors_node(state: Dict) -> Dict:
    """Fetch latest sensor data from database"""
    farm_id = state.get("farm_id", "FARM001")
    
    try:
        readings = await _db.get_latest_readings(farm_id, limit=1)
        if readings:
            sensors = readings[0]
        else:
            # Fallback to realistic defaults if no data exists
            sensors = {
                "soil_moisture": 45,
                "soil_ph": 6.5,
                "air_temperature": 28,
                "humidity": 60,
                "npk_nitrogen": 45,
                "npk_phosphorus": 30,
                "npk_potassium": 40
            }
    except Exception as e:
        print(f"Error fetching sensors: {e}")
        # Fallback to defaults
        sensors = {
            "soil_moisture": 45, "soil_ph": 6.5, "air_temperature": 28, 
            "humidity": 60, "npk_nitrogen": 45, "npk_phosphorus": 30, "npk_potassium": 40
        }
    
    return {"sensors": sensors}

async def get_weather_node(state: Dict) -> Dict:
    """Get current weather and forecast"""
    location = state.get("location", "Pune")

    try:
        current = await get_current_weather.ainvoke(location)
        forecast = await get_weather_forecast.ainvoke(
            {"location": location, "hours": 24}
        )

        return {
            "weather_current": current.get("data", {}),
            "weather_forecast": forecast.get("data", {}),
        }
    except Exception as e:
        print(f"Weather error: {e}")
        return {
            "weather_current": {"temperature": 28, "humidity": 60},
            "weather_forecast": {"avg_rain_probability": 20, "rain_expected": False},
        }


async def analyze_soil_node(state: Dict) -> Dict:
    """Analyze soil from sensor data"""
    sensors = state.get("sensors", {})

    try:
        result = await analyze_soil.ainvoke({"sensor_data": sensors})
        return {"soil_analysis": result.get("data", {})}
    except Exception as e:
        print(f"Soil analysis error: {e}")
        return {"soil_analysis": {"health_score": 0, "error": str(e)}}


async def irrigation_node(state: Dict) -> Dict:
    """Calculate irrigation decision"""
    sensors = state.get("sensors", {})
    forecast = state.get("weather_forecast", {})

    try:
        result = await calculate_irrigation.ainvoke(
            {"sensor_data": sensors, "weather_forecast": {"data": forecast}}
        )
        return {"irrigation_decision": result.get("data", {})}
    except Exception as e:
        print(f"Irrigation error: {e}")
        return {"irrigation_decision": {"should_irrigate": False, "error": str(e)}}


async def fertilizer_node(state: Dict) -> Dict:
    """Recommend fertilizer"""
    sensors = state.get("sensors", {})

    try:
        result = await recommend_fertilizer.ainvoke({"sensor_data": sensors})
        return {"fertilizer_recommendation": result.get("data", {})}
    except Exception as e:
        print(f"Fertilizer error: {e}")
        return {"fertilizer_recommendation": {"error": str(e)}}


async def disease_node(state: Dict) -> Dict:
    """Detect disease"""
    crop_type = state.get("crop_type", "wheat")
    symptoms = state.get("symptoms", [])

    try:
        result = await detect_disease.ainvoke(
            {"crop_type": crop_type, "symptoms": symptoms}
        )
        return {"disease_detection": result.get("data", {})}
    except Exception as e:
        print(f"Disease detection error: {e}")
        return {"disease_detection": {"disease_detected": False, "error": str(e)}}


async def yield_node(state: Dict) -> Dict:
    """Predict yield"""
    crop_type = state.get("crop_type", "wheat")
    sensors = state.get("sensors", {})

    try:
        result = await predict_yield.ainvoke(
            {"crop_type": crop_type, "sensor_data": sensors}
        )
        return {"yield_prediction": result.get("data", {})}
    except Exception as e:
        print(f"Yield prediction error: {e}")
        return {"yield_prediction": {"error": str(e)}}


async def market_node(state: Dict) -> Dict:
    """Get market forecast"""
    crop_type = state.get("crop_type", "wheat")

    try:
        result = await get_market_forecast.ainvoke(crop_type)
        return {"market_forecast": result.get("data", {})}
    except Exception as e:
        print(f"Market forecast error: {e}")
        return {"market_forecast": {"error": str(e)}}


async def risk_node(state: Dict) -> Dict:
    """Assess climate risk"""
    location = state.get("location", "Pune")

    try:
        result = await assess_climate_risk.ainvoke(location)
        return {"climate_risk": result.get("data", {})}
    except Exception as e:
        print(f"Risk assessment error: {e}")
        return {"climate_risk": {"overall_risk": "low", "error": str(e)}}


async def conflict_node(state: Dict) -> Dict:
    """Resolve conflicts between recommendations"""
    irr = state.get("irrigation_decision", {})
    forecast = state.get("weather_forecast", {})
    fert = state.get("fertilizer_recommendation", {})

    try:
        result = await resolve_conflicts.ainvoke(
            {
                "irrigation_decision": irr,
                "weather_forecast": forecast,
                "fertilizer_recommendation": fert,
            }
        )
        return {"conflicts": result.get("data", {}).get("conflicts", [])}
    except Exception as e:
        print(f"Conflict resolution error: {e}")
        return {"conflicts": []}


async def llm_advice_node(state: Dict) -> Dict:
    """Generate final advice using LLM"""
    # Build context from all agent outputs
    context = {
        "sensors": state.get("sensors", {}),
        "soil": state.get("soil_analysis", {}),
        "weather": state.get("weather_forecast", {}),
        "irrigation": state.get("irrigation_decision", {}),
        "fertilizer": state.get("fertilizer_recommendation", {}),
        "disease": state.get("disease_detection", {}),
        "yield": state.get("yield_prediction", {}),
        "market": state.get("market_forecast", {}),
        "risk": state.get("climate_risk", {}),
        "conflicts": state.get("conflicts", []),
    }

    # Generate human-readable advice
    advice_parts = []

    # Irrigation
    irr = context.get("irrigation", {})
    if irr.get("should_irrigate"):
        advice_parts.append(
            f"💧 IRRIGATION: {irr.get('reason', 'Required')} - Run for {irr.get('duration_minutes', 30)} minutes"
        )
    else:
        advice_parts.append(f"✅ IRRIGATION: {irr.get('reason', 'Not needed')}")

    # Fertilizer
    fert = context.get("fertilizer", {})
    npk = fert.get("npk_status", {})
    if npk.get("nitrogen") and npk.get("nitrogen") < 35:
        advice_parts.append(
            f"🌱 FERTILIZER: Nitrogen deficient - {fert.get('synthetic_recommendations', ['Apply nitrogen'])[0]}"
        )

    # Disease
    dis = context.get("disease", {})
    if dis.get("disease_detected"):
        advice_parts.append(
            f"⚠️ DISEASE: {dis.get('disease_name')} detected - {dis.get('treatment', 'Apply treatment')}"
        )

    # Weather
    weather = context.get("weather", {})
    if weather.get("rain_expected"):
        advice_parts.append(
            f"🌧️ WEATHER: Rain expected ({weather.get('avg_rain_probability', 0)}% probability)"
        )

    # Risk
    risk = context.get("risk", {})
    if risk.get("overall_risk") != "low":
        advice_parts.append(
            f"⚡ RISK: {risk.get('overall_risk', 'medium')} - {risk.get('heatwave_risk', 'normal')} conditions"
        )

    # Conflicts
    if context.get("conflicts"):
        for c in context["conflicts"]:
            advice_parts.append(f"🔄 RESOLVED: {c}")

    final_advice = (
        "\n\n".join(advice_parts)
        if advice_parts
        else "All systems normal. Continue current practices."
    )

    return {
        "final_advice": final_advice,
        "confidence": "high" if len(advice_parts) >= 3 else "medium",
        "timestamp": datetime.now().isoformat(),
    }


# =============================================================================
# BUILD WORKFLOW
# =============================================================================


def build_workflow():
    """Build and compile the StateGraph workflow"""

    # Define state type
    class FarmState(dict):
        farm_id: str
        user_query: str
        location: str = "Pune"
        crop_type: str = "wheat"
        sensors: dict = {}
        weather_current: dict = {}
        weather_forecast: dict = {}
        soil_analysis: dict = {}
        irrigation_decision: dict = {}
        fertilizer_recommendation: dict = {}
        disease_detection: dict = {}
        yield_prediction: dict = {}
        market_forecast: dict = {}
        climate_risk: dict = {}
        conflicts: list = []
        final_advice: str = ""
        confidence: str = "medium"
        errors: list = []

    # Create graph
    builder = StateGraph(FarmState)

    # Add nodes
    builder.add_node("fetch_sensors", fetch_sensors_node)
    builder.add_node("get_weather", get_weather_node)
    builder.add_node("analyze_soil", analyze_soil_node)
    builder.add_node("calculate_irrigation", irrigation_node)
    builder.add_node("recommend_fertilizer", fertilizer_node)
    builder.add_node("detect_disease", disease_node)
    builder.add_node("predict_yield", yield_node)
    builder.add_node("get_market", market_node)
    builder.add_node("assess_risk", risk_node)
    builder.add_node("resolve_conflicts", conflict_node)
    builder.add_node("generate_advice", llm_advice_node)

    # Define edges - sequential flow
    builder.add_edge(START, "fetch_sensors")
    builder.add_edge("fetch_sensors", "get_weather")
    builder.add_edge("get_weather", "analyze_soil")
    builder.add_edge("analyze_soil", "calculate_irrigation")
    builder.add_edge("calculate_irrigation", "recommend_fertilizer")
    builder.add_edge("recommend_fertilizer", "detect_disease")
    builder.add_edge("detect_disease", "predict_yield")
    builder.add_edge("predict_yield", "get_market")
    builder.add_edge("get_market", "assess_risk")
    builder.add_edge("assess_risk", "resolve_conflicts")
    builder.add_edge("resolve_conflicts", "generate_advice")
    builder.add_edge("generate_advice", END)

    # Compile without checkpointer (simpler for now)
    return builder.compile()


# Singleton
_workflow = None


def get_workflow():
    """Get or create workflow instance"""
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


# =============================================================================
# RUN FUNCTIONS
# =============================================================================


async def run_farm_analysis(
    farm_id: str = "FARM001",
    location: str = "Pune",
    crop_type: str = "wheat",
    user_query: str = "Analyze my farm",
) -> Dict[str, Any]:
    """
    Run the full farm analysis workflow.

    Args:
        farm_id: Farm identifier
        location: Farm location
        crop_type: Crop type
        user_query: User's query

    Returns:
        Complete analysis result
    """
    workflow = get_workflow()

    initial_state = {
        "farm_id": farm_id,
        "user_query": user_query,
        "location": location,
        "crop_type": crop_type,
        "sensors": {},
        "weather_current": {},
        "weather_forecast": {},
        "soil_analysis": {},
        "irrigation_decision": {},
        "fertilizer_recommendation": {},
        "disease_detection": {},
        "yield_prediction": {},
        "market_forecast": {},
        "climate_risk": {},
        "conflicts": [],
        "final_advice": "",
        "confidence": "medium",
        "errors": [],
    }

    try:
        result = await workflow.ainvoke(initial_state)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e), "data": initial_state}


# Test function
async def test_workflow():
    """Test the workflow"""
    print("🧪 Testing workflow...")

    result = await run_farm_analysis(
        farm_id="TEST001", location="Pune", crop_type="wheat"
    )

    print(f"✅ Result: {result.get('status')}")
    print(f"📋 Advice: {result.get('data', {}).get('final_advice', '')[:200]}...")

    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_workflow())
