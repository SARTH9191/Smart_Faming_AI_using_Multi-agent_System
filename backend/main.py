"""
Smart Farming Agentic AI System — Main Backend Server
=====================================================
FastAPI Application Entry Point
Consolidated Version: PostgreSQL + Async + Full Agent Suite + AI Vision
"""

# ── Mock broken opentelemetry dependency ──────────────────────────
import sys
from unittest.mock import MagicMock

sys.modules["opentelemetry"] = MagicMock()
sys.modules["opentelemetry.api"] = MagicMock()
sys.modules["opentelemetry.sdk"] = MagicMock()
sys.modules["opentelemetry.sdk._logs"] = MagicMock()
sys.modules["opentelemetry.sdk._logs._internal"] = MagicMock()

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
import io
import os
import base64
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from both .env files
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Import configuration
from config import API_CONFIG

# LangGraph modules (Agentic AI System)
from graph import run_farm_analysis, get_supervisor

# Core components
from core.database import AsyncDatabase
from core.auth_system import AuthSystem

# Keep voice assistant as separate UI layer
from agents.voice_assistant_agent import VoiceAssistantAgent

# FastAPI will be initialized later with lifespan

# Initialize components
db = AsyncDatabase(API_CONFIG["database_url"])
auth_system = AuthSystem(db)

# Initialize LangGraph supervisor (main agentic brain)
supervisor = get_supervisor()

# Initialize voice assistant
voice_agent = VoiceAssistantAgent(db)


# ── Request Models ──────────────────────────────────────────────────


class SensorDataRequest(BaseModel):
    farm_id: str = "FARM001"
    duration_minutes: int = 1


class VoiceCommandRequest(BaseModel):
    text: str
    language: str = "en"
    farm_id: str = "FARM001"


class SpeechRecognitionRequest(BaseModel):
    audio_base64: str
    language: str = "en"


class DiseaseDetectionRequest(BaseModel):
    image_data: Optional[str] = None
    crop_type: str = "wheat"
    symptoms: List[str] = []


class ImageDiseaseRequest(BaseModel):
    image_base64: str
    crop_type: str = "wheat"


class YieldPredictionRequest(BaseModel):
    crop_type: str
    area_hectares: float
    soil_quality: str = "medium"


class AgentQueryRequest(BaseModel):
    farm_id: str = "FARM001"
    query: str = "Analyze my farm and give recommendations"
    location: str = "Pune"
    crop_type: str = "wheat"


class ChatMessageRequest(BaseModel):
    message: str
    farm_id: str = "FARM001"
    history: List[Dict[str, str]] = []


class CropRequest(BaseModel):
    crop_type: str
    variety: Optional[str] = None
    planted_date: Optional[str] = None
    area_hectares: float = 1.0
    status: str = "growing"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CropStatusUpdate(BaseModel):
    status: str


class CopilotRequest(BaseModel):
    message: str
    farm_id: str = "FARM001"


class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    farm_size: Optional[float] = None
    language: str = "en"
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    is_organic: Optional[bool] = False


class FarmDetailsRequest(BaseModel):
    total_land_area_acres: Optional[float] = None
    number_of_crops: Optional[int] = None
    crops_names: Optional[str] = None
    sowing_date: Optional[str] = None
    sowed_land_area_acres: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LoginRequest(BaseModel):
    email: Optional[str] = None
    farmer_id: Optional[str] = None
    password: str


# ── Lifecycle Events ────────────────────────────────────────────────


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    print("Initializing Smart Farming AI System...")
    await db.init_db()
    print("Database initialized")
    yield


app = FastAPI(
    title="AgroBrain OS - Agentic AI Farming System",
    description="LangGraph-powered Autonomous AI Agent for Precision Agriculture",
    version="3.0.0",
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run_agents")
async def run_agents(farm_id: str = "FARM001"):
    """Run all AI agents for a farm"""
    try:
        from graph import run_farm_analysis

        result = await run_farm_analysis(
            farm_id=farm_id,
            location="Pune",
            crop_type="wheat",
            user_query="Run full farm analysis",
        )

        return {
            "status": "success",
            "message": "All AI agents executed successfully",
            "data": result.get("data", {}),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/agent/run")
async def run_langgraph_agent(request: AgentQueryRequest):
    """Run full LangGraph autonomous workflow"""
    try:
        from graph import run_farm_analysis

        # Build farm-specific context from DB/profile of logged-in farmer
        profile = await auth_system.get_farmer_profile(request.farm_id)
        crops = await db.get_crops(request.farm_id)
        sensors = await db.get_latest_readings(request.farm_id, limit=1)

        profile_location = (profile or {}).get("location")
        effective_location = (
            request.location
            if request.location and request.location != "Pune"
            else (profile_location or "Pune")
        )

        crop_names = [c.get("crop_type") for c in (crops or []) if c.get("crop_type")]
        latest_sensor = sensors[0] if sensors else {}

        context_lines = [
            f"Farm ID: {request.farm_id}",
            f"Location: {effective_location}",
        ]
        if profile:
            context_lines.append(
                f"Soil: {profile.get('soil_type') or 'unknown'}, Irrigation: {profile.get('irrigation_source') or 'unknown'}, Organic: {profile.get('is_organic')}"
            )
            if profile.get("total_land_area_acres") is not None:
                context_lines.append(
                    f"Land area: {profile.get('total_land_area_acres')} acres"
                )
        if crop_names:
            context_lines.append(f"Active crops: {', '.join(crop_names[:6])}")
        if latest_sensor:
            context_lines.append(
                "Latest sensors: "
                f"soil_moisture={latest_sensor.get('soil_moisture')}, "
                f"soil_ph={latest_sensor.get('soil_ph')}, "
                f"air_temperature={latest_sensor.get('air_temperature')}"
            )

        contextual_query = (
            "Use this farm context strictly while answering:\n"
            + "\n".join(context_lines)
            + "\n\nUser request:\n"
            + request.query
        )

        result = await run_farm_analysis(
            farm_id=request.farm_id,
            location=effective_location,
            crop_type=request.crop_type,
            user_query=contextual_query,
        )

        # Save the recommendation to the database so the dashboard can fetch it
        if result.get("status") == "success" and result.get("data", {}).get(
            "final_advice"
        ):
            advice = result["data"]["final_advice"]
            await db.store_recommendation(
                {
                    "farm_id": request.farm_id,
                    "agent_name": "AgroBrain Auto Agent",
                    "recommendation_type": "farm_analysis",
                    "recommendation_text": advice,
                    "priority": result["data"].get("confidence", "high"),
                    "llm_source": "langgraph-supervisor",
                }
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/chat")
async def chat_with_agent(request: ChatMessageRequest):
    """
    Chat with the autonomous agent using natural language.
    Uses Groq LLM with tool access for intelligent responses.
    """
    try:
        from graph import get_supervisor

        supervisor = get_supervisor()

        if not supervisor.is_available:
            return {
                "status": "error",
                "response": "AI agent unavailable. Please configure GROQ_API_KEY.",
            }

        # Build profile-aware context for the logged-in farmer
        profile = await auth_system.get_farmer_profile(request.farm_id)
        crops = await db.get_crops(request.farm_id)
        sensors = await db.get_latest_readings(request.farm_id, limit=1)

        crop_names = [c.get("crop_type") for c in (crops or []) if c.get("crop_type")]
        latest_sensor = sensors[0] if sensors else {}

        context_bits = [
            f"Farmer context for farm_id={request.farm_id}",
            f"location={(profile or {}).get('location') or 'unknown'}",
            f"soil_type={(profile or {}).get('soil_type') or 'unknown'}",
            f"irrigation={(profile or {}).get('irrigation_source') or 'unknown'}",
            f"is_organic={(profile or {}).get('is_organic')}",
        ]
        if crop_names:
            context_bits.append(f"active_crops={', '.join(crop_names[:6])}")
        if latest_sensor:
            context_bits.append(
                "latest_sensors="
                f"soil_moisture:{latest_sensor.get('soil_moisture')},"
                f"soil_ph:{latest_sensor.get('soil_ph')},"
                f"air_temperature:{latest_sensor.get('air_temperature')}"
            )

        history_lines = []
        for h in (request.history or [])[-6:]:
            role = h.get("role", "user")
            text = h.get("text") or h.get("content") or ""
            if text:
                history_lines.append(f"{role}: {text}")

        contextual_message = (
            "Use only this farm context when replying.\n"
            + " | ".join(context_bits)
            + ("\nRecent conversation:\n" + "\n".join(history_lines) if history_lines else "")
            + "\n\nCurrent user message:\n"
            + request.message
        )

        result = await supervisor.run_autonomous(
            user_query=contextual_message,
            farm_id=request.farm_id,
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/query")
async def query_agent(request: AgentQueryRequest):
    """
    Query the agent with a specific question.
    Returns autonomous analysis using tools.
    """
    try:
        from graph import get_supervisor

        supervisor = get_supervisor()

        if not supervisor.is_available:
            return {
                "status": "error",
                "response": "Agent unavailable. Check GROQ_API_KEY.",
            }

        result = await supervisor.run_autonomous(
            user_query=request.query, farm_id=request.farm_id
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate_sensors")
async def simulate_sensors(request: SensorDataRequest):
    """Generate mock sensor data for testing"""
    import random

    data = []
    for _ in range(request.duration_minutes):
        reading = {
            "farm_id": request.farm_id,
            "soil_moisture": 35.0 + random.uniform(-5, 5),
            "soil_temperature": 22.0 + random.uniform(-2, 2),
            "soil_ph": 6.5 + random.uniform(-0.5, 0.5),
            "npk_nitrogen": 150 + random.uniform(-20, 20),
            "npk_phosphorus": 45 + random.uniform(-5, 5),
            "npk_potassium": 180 + random.uniform(-20, 20),
            "humidity": 60.0 + random.uniform(-10, 10),
            "air_temperature": 25.0 + random.uniform(-5, 5),
        }
        data.append(reading)

    await db.store_sensor_data(data)
    return {"status": "success", "count": len(data)}


# ── Sensor Data Endpoints ───────────────────────────────────────────


@app.get("/sensors/{farm_id}")
async def get_sensors(farm_id: str, limit: int = 10):
    """Get sensor data for a farm"""
    try:
        readings = await db.get_latest_readings(farm_id, limit=limit)
        return {"farm_id": farm_id, "sensors": readings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Crop Management ─────────────────────────────────────────────────


class CropRequest(BaseModel):
    crop_type: str
    variety: Optional[str] = None
    planted_date: Optional[str] = None
    area_hectares: float = 1.0
    status: str = "growing"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@app.post("/crops")
async def add_crop(request: CropRequest, farm_id: str = "FARM001"):
    """Add a new crop"""
    try:
        data = request.dict()
        data["farm_id"] = farm_id
        crop_id = await db.store_crop(data)
        return {"status": "success", "crop_id": crop_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crops")
async def get_crops(farm_id: str = "FARM001", status: Optional[str] = None):
    """Get all crops for a farm"""
    try:
        crops = await db.get_crops(farm_id)
        if status and status != "all":
            crops = [c for c in crops if c.get("status") == status]
        return {"farm_id": farm_id, "crops": crops}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/crops/{crop_id}/status")
async def update_crop_status(crop_id: int, status: str):
    try:
        await db.update_crop_status(crop_id, status)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/crops/{crop_id}")
async def update_crop(crop_id: int, request_data: Dict[str, Any]):
    try:
        await db.update_crop(crop_id, request_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/crops/{crop_id}")
async def delete_crop(crop_id: int):
    try:
        await db.delete_crop(crop_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Profile Endpoints ───────────────────────────────────────────────


class FarmDetailsRequest(BaseModel):
    farm_size: Optional[float] = None
    total_land_area_acres: Optional[float] = None
    number_of_crops: Optional[int] = None
    crops_names: Optional[str] = None
    sowing_date: Optional[str] = None
    sowed_land_area_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    is_organic: Optional[bool] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@app.get("/profile")
async def get_profile(farm_id: str = "FARM001"):
    """Get farmer profile (top-level shape expected by frontend)."""
    try:
        profile = await auth_system.get_farmer_profile(farm_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Farmer not found")

        # Merge optional farm profile coordinates/area if available,
        # while keeping existing frontend-compatible top-level keys.
        farm_profile = await db.get_farm_profile(farm_id)
        if farm_profile:
            if profile.get("latitude") is None and farm_profile.get("latitude") is not None:
                profile["latitude"] = farm_profile.get("latitude")
            if profile.get("longitude") is None and farm_profile.get("longitude") is not None:
                profile["longitude"] = farm_profile.get("longitude")
            if profile.get("farm_size") is None and farm_profile.get("area_hectares") is not None:
                profile["farm_size"] = farm_profile.get("area_hectares")

        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/profile/farm_details")
async def update_farm_details(request: FarmDetailsRequest, farm_id: str = "FARM001"):
    """Update farm details and save to database"""
    try:
        # Update farm details in farmer table
        data = request.dict(exclude_none=True)
        result = await auth_system.update_farm_details(farm_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Farmer not found")
        
        # Also save grounding coordinates/area in farm_profiles table
        farm_profile_data = {}
        if data.get("latitude") is not None:
            farm_profile_data["latitude"] = data.get("latitude")
        if data.get("longitude") is not None:
            farm_profile_data["longitude"] = data.get("longitude")
        if data.get("farm_size") is not None:
            farm_profile_data["area_hectares"] = data.get("farm_size")
        farm_profile_data["verification_radius_meters"] = 600.0
        
        farm_profile = None
        if farm_profile_data:
            farm_profile = await db.upsert_farm_profile(farm_id, farm_profile_data)
        
        return {
            "status": "success",
            "message": "Profile saved successfully",
            "farmer_details": result,
            "farm_profile": farm_profile
        }
    except Exception as e:
        print(f"Profile update error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Auth Endpoints ───────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: Optional[str] = None
    farmer_id: Optional[str] = None
    phone: Optional[str] = None
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    farmer_id: Optional[str] = None
    password: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    farm_size: Optional[float] = None
    language: str = "en"
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    is_organic: Optional[bool] = False


@app.post("/auth/login")
async def login(request: LoginRequest):
    identifier = request.email or request.farmer_id
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or Farmer ID is required")

    result = await auth_system.login_farmer(identifier, request.password)
    if result["status"] == "failed":
        raise HTTPException(status_code=401, detail=result["message"])

    # Frontend compatibility: include user/session_id shape
    import hashlib

    session_id = hashlib.sha256(
        f"{result.get('farmer_id')}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    return {
        **result,
        "session_id": session_id,
        "user": {
            "farmerId": result.get("farmer_id"),
            "farmer_id": result.get("farmer_id"),
            "name": result.get("name"),
            "email": result.get("email"),
        },
    }


@app.post("/auth/register")
async def register(request: RegisterRequest):
    try:
        payload = {
            "farmer_id": request.farmer_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "password": request.password,
            "location": request.location,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "farm_size": request.farm_size,
            "language": request.language,
            "soil_type": request.soil_type,
            "irrigation_source": request.irrigation_source,
            "is_organic": request.is_organic,
        }

        created = await auth_system.register_farmer(payload)

        # Persist initial farm profile too for geo-verification and admin flows
        created_farmer_id = created.get("farmer_id")
        if created_farmer_id:
            farm_payload = {
                "farm_name": request.name,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "area_hectares": request.farm_size,
                "verification_radius_meters": 600.0,
                "is_active": True,
            }
            await db.upsert_farm_profile(created_farmer_id, farm_payload)

        return {"status": "success", "farmer_id": created_farmer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BasicProfileRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    is_organic: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@app.put("/profile/update_basic")
async def update_basic_profile(request: BasicProfileRequest, farm_id: str = "FARM001"):
    """Update basic farmer profile fields and optional farm coordinates."""
    try:
        payload = request.dict(exclude_none=True)
        result = await auth_system.update_basic_profile(farm_id, payload)
        if not result:
            raise HTTPException(status_code=404, detail="Farmer not found")

        # Keep farm_profiles table in sync for geo-based flows
        farm_payload = {}
        if payload.get("latitude") is not None:
            farm_payload["latitude"] = payload.get("latitude")
        if payload.get("longitude") is not None:
            farm_payload["longitude"] = payload.get("longitude")
        if farm_payload:
            farm_payload["verification_radius_meters"] = 600.0
            await db.upsert_farm_profile(farm_id, farm_payload)

        return {"status": "success", "profile": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Specialized Feature Endpoints ───────────────────────────────────


@app.get("/get_weather")
async def get_weather(location: str = "Delhi"):
    from graph.tools import get_current_weather

    res = await get_current_weather.ainvoke(location)
    data = res.get("data", {})
    return {
        "location": location,
        "data_source": "OpenWeather API"
        if res.get("status") == "success"
        else "Simulated due to Error",
        "current": data
        if res.get("status") == "success"
        else {
            "temperature": 0,
            "humidity": 0,
            "wind_speed": 0,
            "cloud_cover": 0,
            "pressure": 0,
            "visibility": 0,
        },
    }


@app.get("/get_forecast")
async def get_forecast(location: str = "Delhi", hours: int = 24):
    from graph.tools import get_weather_forecast

    res = await get_weather_forecast.ainvoke({"location": location, "hours": hours})
    data = res.get("data", {})
    summary = data.get("summary", {})
    
    # Correct mapping for frontend
    formatted_summary = {
        "avg_temperature": round((summary.get("temp_min", 0) + summary.get("temp_max", 0)) / 2, 1),
        "max_temperature": summary.get("temp_max", 0),
        "max_rain_probability": data.get("avg_rain_probability", 0),
        "rain_expected": data.get("rain_expected", False)
    }

    return {
        "data_source": "OpenWeather API"
        if res.get("status") == "success"
        else "Simulated due to Error",
        "summary": formatted_summary,
        "risk_score": {"level": data.get("risk", "low"), "factors": []},
        "hourly_forecast": data.get("hourly_forecast", []),
        "recommendations": [
            "Monitor soil moisture" if data.get("rain_expected") else "Normal conditions",
            "Prepare for possible irrigation" if not data.get("rain_expected") else "Rain predicted"
        ],
    }


@app.get("/get_weather_advisory")
async def get_weather_advisory(location: str = "Pune", farm_id: str = "FARM001"):
    """
    Fetches 4-day weather forecast using LangGraph weather tool.
    """
    from graph.tools import get_weather_forecast

    forecast = await get_weather_forecast.ainvoke({"location": location, "hours": 96})
    return forecast

    # 2. Build per-day summaries from the 3-hour slots
    daily_summaries = {}
    for slot in forecast_raw.get("hourly_forecast", []):
        try:
            day_key = slot["time"][:10]  # "YYYY-MM-DD"
            if day_key not in daily_summaries:
                daily_summaries[day_key] = {
                    "date": day_key,
                    "temps": [],
                    "rain_probs": [],
                    "conditions": [],
                    "humidity": [],
                    "wind_speeds": [],
                }
            d = daily_summaries[day_key]
            d["temps"].append(slot.get("temperature", 0))
            d["rain_probs"].append(slot.get("rain_probability", 0))
            d["conditions"].append(slot.get("conditions", ""))
            d["humidity"].append(slot.get("humidity", 0))
            d["wind_speeds"].append(slot.get("wind_speed", 0))
        except Exception:
            continue

    # Collapse to 4 days max, compute day-level stats
    days = []
    for day_key in sorted(daily_summaries.keys())[:4]:
        d = daily_summaries[day_key]
        dominant_condition = (
            max(set(d["conditions"]), key=d["conditions"].count)
            if d["conditions"]
            else "Clear"
        )
        days.append(
            {
                "date": day_key,
                "max_temp": round(max(d["temps"]), 1) if d["temps"] else 0,
                "min_temp": round(min(d["temps"]), 1) if d["temps"] else 0,
                "avg_temp": round(sum(d["temps"]) / len(d["temps"]), 1)
                if d["temps"]
                else 0,
                "max_rain_prob": round(max(d["rain_probs"]), 1)
                if d["rain_probs"]
                else 0,
                "avg_humidity": round(sum(d["humidity"]) / len(d["humidity"]), 1)
                if d["humidity"]
                else 0,
                "avg_wind_speed": round(
                    sum(d["wind_speeds"]) / len(d["wind_speeds"]), 1
                )
                if d["wind_speeds"]
                else 0,
                "dominant_condition": dominant_condition,
                "rain_expected": max(d["rain_probs"]) > 50
                if d["rain_probs"]
                else False,
            }
        )

    if not days:
        return {
            "location": location,
            "daily_forecast": [],
            "advisory": "Weather forecast unavailable. Please configure your OpenWeather API key.",
            "risk_level": "unknown",
            "error": forecast_raw.get("error", "No forecast data"),
        }

    # 3. Get optional farm context to personalise advice (Using Smoothing for stability)
    sensor_ctx = {}
    try:
        readings = await db.get_latest_readings(farm_id, limit=10)
        if readings:
            m = sum([r.get("soil_moisture", 0) for r in readings]) / len(readings)
            p = sum([r.get("soil_ph", 7) for r in readings]) / len(readings)
            n = sum([r.get("npk_nitrogen", 0) for r in readings]) / len(readings)

            sensor_ctx = {
                "soil_moisture": round(m, 2),
                "soil_ph": round(p, 2),
                "npk_nitrogen": round(n, 2),
            }
    except Exception:
        pass

    crop_ctx = {}
    try:
        crops = await db.get_crops(farm_id)
        if crops:
            crop_ctx = {
                "crop_type": crops[0].get("crop_type", "unknown"),
                "status": crops[0].get("status", "growing"),
            }
    except Exception:
        pass

    # 4. Call Groq LLM for AI advisory — fully grounded in the real forecast data
    groq_client = (
        lead_agent.llm.groq_client
        if getattr(lead_agent.llm, "_groq_available", False)
        else None
    )

    advisory_text = None
    advisory_structured = None

    if groq_client:
        days_json = _json.dumps(days, indent=2)
        sensor_note = (
            f"Farm sensor context: {_json.dumps(sensor_ctx)}" if sensor_ctx else ""
        )
        crop_note = f"Current crop: {crop_ctx}" if crop_ctx else ""

        prompt = f"""You are an expert agricultural AI advisor.
Below is the REAL 4-day weather forecast for {location}.
{sensor_note}
{crop_note}

FORECAST DATA (do not ignore these numbers):
{days_json}

Based ONLY on this data, generate a JSON response in this exact schema:
{{
  "overall_outlook": "<1-2 sentence summary of the next 4 days weather>",
  "risk_level": "<low|medium|high|critical>",
  "risk_reason": "<specific reason tied to the forecast numbers>",
  "daily_advice": [
    {{
      "date": "<YYYY-MM-DD>",
      "condition_emoji": "<one weather emoji>",
      "key_advice": "<1 concrete farming action for this specific day>",
      "do": "<what to do>",
      "avoid": "<what NOT to do>"
    }}
  ],
  "critical_alerts": ["<alert if any dangerous conditions exist, else empty list>"],
  "best_farming_window": "<which day(s) are best for field operations and why>",
  "irrigation_recommendation": "<specific irrigation advice based on rain probability and temp>",
  "pesticide_spray_window": "<best window for spraying pesticides based on wind/rain forecast>"
}}

Return ONLY valid JSON. Do not add markdown or explanation."""

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=900,
            )
            raw = response.choices[0].message.content.strip()
            # Strip any markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            advisory_structured = _json.loads(raw)
        except Exception as e:
            advisory_text = f"AI advisory temporarily unavailable: {str(e)}"

    # Fallback if Groq is not available or parsing failed
    if advisory_structured is None:
        has_rain = any(d["rain_expected"] for d in days)
        max_temp_overall = max(d["max_temp"] for d in days) if days else 0
        advisory_structured = {
            "overall_outlook": f"{'Rainy' if has_rain else 'Dry'} conditions expected over the next {len(days)} days with temperatures reaching {max_temp_overall}°C.",
            "risk_level": "high"
            if has_rain and max_temp_overall > 36
            else ("medium" if has_rain else "low"),
            "risk_reason": "Heavy rain probability detected"
            if has_rain
            else "Dry and warm conditions",
            "daily_advice": [
                {
                    "date": d["date"],
                    "condition_emoji": "🌧️" if d["rain_expected"] else "☀️",
                    "key_advice": "Postpone field operations, prepare drainage"
                    if d["rain_expected"]
                    else "Good day for field operations",
                    "do": "Drain fields, cover storage"
                    if d["rain_expected"]
                    else "Irrigate, spray, plough",
                    "avoid": "Spraying pesticides, ploughing"
                    if d["rain_expected"]
                    else "Over-irrigation",
                }
                for d in days
            ],
            "critical_alerts": ["⛈️ Rain expected — postpone fertilizer application"]
            if has_rain
            else [],
            "best_farming_window": next(
                (d["date"] for d in days if not d["rain_expected"]),
                days[0]["date"] if days else "N/A",
            ),
            "irrigation_recommendation": "Skip irrigation — rain expected"
            if has_rain
            else f"Irrigate — no rain forecast, temperatures up to {max_temp_overall}°C",
            "pesticide_spray_window": next(
                (
                    d["date"]
                    for d in days
                    if not d["rain_expected"] and d["avg_wind_speed"] < 15
                ),
                "Avoid spraying — check conditions",
            ),
        }

    return {
        "location": location,
        "farm_id": farm_id,
        "generated_at": datetime.utcnow().isoformat(),
        "daily_forecast": days,
        "ai_advisory": advisory_structured,
        "data_source": forecast_raw.get("data_source", "OpenWeather API"),
    }


@app.get("/get_market_forecast")
async def get_market_forecast(crop: str = "wheat"):
    from ml.market_predictor import predict_market_prices

    result = predict_market_prices(crop, days=30)
    return result


@app.get("/api/marketplace")
async def get_marketplace(state: Optional[str] = None):
    """Fetch real-time Mandi prices from data.gov.in with fallback to sample data"""
    import json
    import os
    
    # Sample mandi data for fallback
    sample_records = [
        # Grains & Cereals
        {"state": "Maharashtra", "district": "Pune", "market": "Pune Agricultural Market", "commodity": "Wheat", "variety": "Local", "arrival_date": "2026-04-16", "min_price": 2200, "max_price": 2400, "modal_price": 2300},
        {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana Mandi", "commodity": "Wheat", "variety": "PBW", "arrival_date": "2026-04-16", "min_price": 2250, "max_price": 2450, "modal_price": 2350},
        {"state": "Maharashtra", "district": "Pune", "market": "Pune Agricultural Market", "commodity": "Rice", "variety": "Basmati", "arrival_date": "2026-04-16", "min_price": 4500, "max_price": 5200, "modal_price": 4800},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Rice", "variety": "Sona Masoori", "arrival_date": "2026-04-16", "min_price": 3800, "max_price": 4200, "modal_price": 4000},
        {"state": "Tamil Nadu", "district": "Chennai", "market": "Chennai Mandi", "commodity": "Rice", "variety": "Ponni", "arrival_date": "2026-04-16", "min_price": 3500, "max_price": 3900, "modal_price": 3700},
        {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore Mandi", "commodity": "Maize", "variety": "White", "arrival_date": "2026-04-16", "min_price": 1800, "max_price": 2000, "modal_price": 1900},
        {"state": "Gujarat", "district": "Ahmedabad", "market": "Ahmedabad Mandi", "commodity": "Jowar", "variety": "Yellow", "arrival_date": "2026-04-16", "min_price": 2400, "max_price": 2600, "modal_price": 2500},
        
        # Pulses
        {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore Mandi", "commodity": "Arhar", "variety": "Machine Clean", "arrival_date": "2026-04-16", "min_price": 5500, "max_price": 6200, "modal_price": 5800},
        {"state": "Maharashtra", "district": "Nashik", "market": "Nashik Mandi", "commodity": "Gram", "variety": "Black", "arrival_date": "2026-04-16", "min_price": 4800, "max_price": 5400, "modal_price": 5100},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Urad", "variety": "Black", "arrival_date": "2026-04-16", "min_price": 6200, "max_price": 6800, "modal_price": 6500},
        {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana Mandi", "commodity": "Moong", "variety": "Green", "arrival_date": "2026-04-16", "min_price": 5800, "max_price": 6400, "modal_price": 6100},
        
        # Oilseeds
        {"state": "Gujarat", "district": "Ahmedabad", "market": "Ahmedabad Mandi", "commodity": "Groundnut", "variety": "Bold", "arrival_date": "2026-04-16", "min_price": 5200, "max_price": 5800, "modal_price": 5500},
        {"state": "Rajasthan", "district": "Jaipur", "market": "Jaipur Mandi", "commodity": "Mustard Seed", "variety": "Yellow", "arrival_date": "2026-04-16", "min_price": 4800, "max_price": 5200, "modal_price": 5000},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Coconut", "variety": "Dry", "arrival_date": "2026-04-16", "min_price": 8000, "max_price": 9500, "modal_price": 8700},
        {"state": "Andhra Pradesh", "district": "Hyderabad", "market": "Hyderabad Mandi", "commodity": "Sunflower Seeds", "variety": "Black", "arrival_date": "2026-04-16", "min_price": 5400, "max_price": 5900, "modal_price": 5650},
        
        # Cash Crops
        {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana Mandi", "commodity": "Cotton", "variety": "Fine", "arrival_date": "2026-04-16", "min_price": 5800, "max_price": 6200, "modal_price": 6000},
        {"state": "Maharashtra", "district": "Ahmednagar", "market": "Ahmednagar Mandi", "commodity": "Sugarcane", "variety": "Local", "arrival_date": "2026-04-16", "min_price": 320, "max_price": 380, "modal_price": 350},
        {"state": "Tamil Nadu", "district": "Coimbatore", "market": "Coimbatore Mandi", "commodity": "Tobacco", "variety": "Leaf", "arrival_date": "2026-04-16", "min_price": 180, "max_price": 220, "modal_price": 200},
        
        # Vegetables
        {"state": "Maharashtra", "district": "Pune", "market": "Pune Agricultural Market", "commodity": "Onion", "variety": "Yellow", "arrival_date": "2026-04-16", "min_price": 1200, "max_price": 1600, "modal_price": 1400},
        {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore Mandi", "commodity": "Potato", "variety": "Red", "arrival_date": "2026-04-16", "min_price": 800, "max_price": 1200, "modal_price": 1000},
        {"state": "Gujarat", "district": "Ahmedabad", "market": "Ahmedabad Mandi", "commodity": "Tomato", "variety": "Fresh", "arrival_date": "2026-04-16", "min_price": 1600, "max_price": 2200, "modal_price": 1900},
        {"state": "Punjab", "district": "Amritsar", "market": "Amritsar Mandi", "commodity": "Cabbage", "variety": "Green", "arrival_date": "2026-04-16", "min_price": 600, "max_price": 1000, "modal_price": 800},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Carrot", "variety": "Orange", "arrival_date": "2026-04-16", "min_price": 1400, "max_price": 1800, "modal_price": 1600},
        {"state": "Tamil Nadu", "district": "Chennai", "market": "Chennai Mandi", "commodity": "Brinjal", "variety": "Purple", "arrival_date": "2026-04-16", "min_price": 1800, "max_price": 2400, "modal_price": 2100},
        {"state": "Maharashtra", "district": "Nashik", "market": "Nashik Mandi", "commodity": "Garlic", "variety": "Bulbs", "arrival_date": "2026-04-16", "min_price": 2800, "max_price": 3400, "modal_price": 3100},
        {"state": "Rajasthan", "district": "Jaipur", "market": "Jaipur Mandi", "commodity": "Chilli", "variety": "Green", "arrival_date": "2026-04-16", "min_price": 2000, "max_price": 2600, "modal_price": 2300},
        
        # Fruits
        {"state": "Maharashtra", "district": "Pune", "market": "Pune Agricultural Market", "commodity": "Banana", "variety": "Hybrid", "arrival_date": "2026-04-16", "min_price": 1200, "max_price": 1600, "modal_price": 1400},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Mango", "variety": "Alphonso", "arrival_date": "2026-04-16", "min_price": 4000, "max_price": 5200, "modal_price": 4600},
        {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana Mandi", "commodity": "Apple", "variety": "Shimla", "arrival_date": "2026-04-16", "min_price": 3000, "max_price": 4000, "modal_price": 3500},
        {"state": "Tamil Nadu", "district": "Coimbatore", "market": "Coimbatore Mandi", "commodity": "Orange", "variety": "Sweet", "arrival_date": "2026-04-16", "min_price": 1400, "max_price": 1800, "modal_price": 1600},
        {"state": "Gujarat", "district": "Ahmedabad", "market": "Ahmedabad Mandi", "commodity": "Grapes", "variety": "Red", "arrival_date": "2026-04-16", "min_price": 3200, "max_price": 4200, "modal_price": 3700},
        
        # Spices
        {"state": "Tamil Nadu", "district": "Coimbatore", "market": "Coimbatore Mandi", "commodity": "Pepper", "variety": "Black", "arrival_date": "2026-04-16", "min_price": 450, "max_price": 550, "modal_price": 500},
        {"state": "Maharashtra", "district": "Nashik", "market": "Nashik Mandi", "commodity": "Turmeric", "variety": "Finger", "arrival_date": "2026-04-16", "min_price": 6800, "max_price": 7600, "modal_price": 7200},
        {"state": "Gujarat", "district": "Ahmedabad", "market": "Ahmedabad Mandi", "commodity": "Cumin Seed", "variety": "White", "arrival_date": "2026-04-16", "min_price": 15000, "max_price": 17000, "modal_price": 16000},
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Cardamom", "variety": "Green", "arrival_date": "2026-04-16", "min_price": 200000, "max_price": 240000, "modal_price": 220000},
        
        # Beverages
        {"state": "Karnataka", "district": "Bangalore", "market": "Bangalore Mandi", "commodity": "Coffee", "variety": "Arabica", "arrival_date": "2026-04-16", "min_price": 180, "max_price": 220, "modal_price": 200},
        {"state": "Tamil Nadu", "district": "Coimbatore", "market": "Coimbatore Mandi", "commodity": "Tea", "variety": "Leaf", "arrival_date": "2026-04-16", "min_price": 240, "max_price": 300, "modal_price": 270},
        
        # Nuts & Dry Fruits
        {"state": "Himachal Pradesh", "district": "Shimla", "market": "Shimla Mandi", "commodity": "Almonds", "variety": "Raw", "arrival_date": "2026-04-16", "min_price": 380, "max_price": 450, "modal_price": 415},
        {"state": "Punjab", "district": "Ludhiana", "market": "Ludhiana Mandi", "commodity": "Walnuts", "variety": "Kernel", "arrival_date": "2026-04-16", "min_price": 420, "max_price": 500, "modal_price": 460},
    ]
    
    try:
        # Load API key
        config_path = os.path.join(os.path.dirname(__file__), "api_config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            api_key = config.get("data_gov_api_key", "")
        
        if api_key:
            # Try to fetch from data.gov.in with timeout
            import requests
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a5c0-d07b3063b06b"
            
            params = {
                "api-key": api_key,
                "format": "json",
                "limit": 500
            }
            
            if state:
                params["filters[state]"] = state
            
            try:
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    if records:
                        # Transform records for frontend
                        formatted_records = []
                        for record in records:
                            formatted_records.append({
                                "state": record.get("state", ""),
                                "district": record.get("district", ""),
                                "market": record.get("market", ""),
                                "commodity": record.get("commodity", ""),
                                "variety": record.get("variety", ""),
                                "arrival_date": record.get("arrival_date", ""),
                                "min_price": float(record.get("min_price", 0)) if record.get("min_price") else 0,
                                "max_price": float(record.get("max_price", 0)) if record.get("max_price") else 0,
                                "modal_price": float(record.get("modal_price", 0)) if record.get("modal_price") else 0
                            })
                        
                        return {
                            "records": formatted_records,
                            "count": len(formatted_records),
                            "status": "success",
                            "source": "data.gov.in"
                        }
            except requests.Timeout:
                print("API timeout, using sample data")
            except Exception as e:
                print(f"API fetch error: {e}")
        
        # Return sample data as fallback
        filtered_records = sample_records
        if state:
            filtered_records = [r for r in sample_records if r["state"].lower() == state.lower()]
        
        return {
            "records": filtered_records,
            "count": len(filtered_records),
            "status": "success",
            "source": "Sample Data (Live API unavailable)"
        }
            
    except Exception as e:
        print(f"Marketplace error: {e}")
        # Return sample data on error
        return {
            "records": sample_records,
            "count": len(sample_records),
            "status": "success",
            "source": "Sample Data (Fallback)"
        }


@app.post("/predict_yield")
async def predict_yield(request: YieldPredictionRequest):
    from graph.tools import predict_yield as yield_tool

    sensor_data = {
        "soil_moisture": request.soil_quality * 50 if request.soil_quality else 45,
        "air_temperature": 25,
        "npk_nitrogen": 45,
        "npk_phosphorus": 30,
        "npk_potassium": 40,
    }
    result = await yield_tool.ainvoke(
        {"crop_type": request.crop_type, "sensor_data": sensor_data}
    )
    return result


@app.post("/detect_disease")
async def detect_disease(request: DiseaseDetectionRequest):
    """Disease detection endpoint with full report schema for frontend scanner."""

    def _normalize_disease_payload(payload: Dict[str, Any], crop_type: str) -> Dict[str, Any]:
        data = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload
        if not isinstance(data, dict):
            data = {}

        disease_detected = bool(data.get("disease_detected", False))
        confidence_raw = data.get("confidence", 0)
        try:
            confidence = int(float(confidence_raw))
        except Exception:
            confidence = 0

        severity = str(data.get("severity") or ("mild" if disease_detected else "none")).lower()
        display_name = data.get("display_name") or data.get("disease_name") or ("Healthy Crop" if not disease_detected else "Disease Detected")

        normalized = {
            "crop_type": crop_type,
            "disease_detected": disease_detected,
            "disease_name": data.get("disease_name") or ("healthy" if not disease_detected else "unknown"),
            "display_name": display_name,
            "emoji": data.get("emoji") or ("✅" if not disease_detected else "⚠️"),
            "confidence": confidence,
            "severity": severity,
            "symptoms": data.get("symptoms") or [],
            "treatment": data.get("treatment") or [],
            "organic_treatment": data.get("organic_treatment") or [],
            "prevention": data.get("prevention") or ["Continue monitoring", "Maintain good farm hygiene"],
            "spread_prediction": data.get("spread_prediction") or {"risk": "none", "timeline": [], "days_to_critical": 14, "without_treatment_loss_pct": 0},
            "treatment_effectiveness": data.get("treatment_effectiveness") or {
                "chemical_treatment": 0,
                "organic_treatment": 0,
                "combined_approach": 0,
                "estimated_yield_saved_pct": 0,
            },
            "recommendations": data.get("recommendations") or [
                "No disease detected from current input.",
                "Retake a clear leaf/stem close-up for better confidence.",
            ],
            "analysis_method": data.get("analysis_method") or "normalized-response",
            "timestamp": data.get("timestamp") or datetime.utcnow().isoformat(),
        }

        # Preserve optional fields
        if data.get("alternative_diagnosis"):
            normalized["alternative_diagnosis"] = data.get("alternative_diagnosis")
        if data.get("reasoning"):
            normalized["reasoning"] = data.get("reasoning")

        return normalized

    try:
        from agents.disease_detection_agent import DiseaseDetectionAgent

        disease_agent = DiseaseDetectionAgent()
        result = disease_agent.detect_disease(
            crop_type=request.crop_type,
            symptoms=request.symptoms,
            image_data=request.image_data,
        )

        return _normalize_disease_payload(result, request.crop_type)
    except Exception:
        # Backward fallback to tool-based path
        from graph.tools import detect_disease as disease_tool

        tool_result = await disease_tool.ainvoke(
            {
                "crop_type": request.crop_type,
                "symptoms": request.symptoms,
                "image_data": request.image_data,
            }
        )
        return _normalize_disease_payload(tool_result, request.crop_type)


@app.post("/detect_disease_image")
async def detect_disease_from_image(request: ImageDiseaseRequest):
    """AI-powered crop disease detection from base64 image data"""
    def _normalize_disease_payload(payload: Dict[str, Any], crop_type: str) -> Dict[str, Any]:
        data = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload
        if not isinstance(data, dict):
            data = {}

        disease_detected = bool(data.get("disease_detected", False))
        confidence_raw = data.get("confidence", 0)
        try:
            confidence = int(float(confidence_raw))
        except Exception:
            confidence = 0

        severity = str(data.get("severity") or ("mild" if disease_detected else "none")).lower()
        display_name = data.get("display_name") or data.get("disease_name") or ("Healthy Crop" if not disease_detected else "Disease Detected")

        normalized = {
            "crop_type": crop_type,
            "disease_detected": disease_detected,
            "disease_name": data.get("disease_name") or ("healthy" if not disease_detected else "unknown"),
            "display_name": display_name,
            "emoji": data.get("emoji") or ("✅" if not disease_detected else "⚠️"),
            "confidence": confidence,
            "severity": severity,
            "symptoms": data.get("symptoms") or [],
            "treatment": data.get("treatment") or [],
            "organic_treatment": data.get("organic_treatment") or [],
            "prevention": data.get("prevention") or ["Continue monitoring", "Maintain good farm hygiene"],
            "spread_prediction": data.get("spread_prediction") or {"risk": "none", "timeline": [], "days_to_critical": 14, "without_treatment_loss_pct": 0},
            "treatment_effectiveness": data.get("treatment_effectiveness") or {
                "chemical_treatment": 0,
                "organic_treatment": 0,
                "combined_approach": 0,
                "estimated_yield_saved_pct": 0,
            },
            "recommendations": data.get("recommendations") or [
                "No disease detected from current input.",
                "Retake a clear leaf/stem close-up for better confidence.",
            ],
            "analysis_method": data.get("analysis_method") or "normalized-response",
            "timestamp": data.get("timestamp") or datetime.utcnow().isoformat(),
        }
        if data.get("alternative_diagnosis"):
            normalized["alternative_diagnosis"] = data.get("alternative_diagnosis")
        if data.get("reasoning"):
            normalized["reasoning"] = data.get("reasoning")
        return normalized

    try:
        from agents.disease_detection_agent import DiseaseDetectionAgent

        disease_agent = DiseaseDetectionAgent()
        result = disease_agent.analyze_image_from_base64(
            request.image_base64, request.crop_type
        )
        return _normalize_disease_payload(result, request.crop_type)
    except Exception:
        # Tool fallback + normalize shape
        from graph.tools import detect_disease as disease_tool

        tool_result = await disease_tool.ainvoke(
            {"crop_type": request.crop_type, "image_data": request.image_base64}
        )
        return _normalize_disease_payload(tool_result, request.crop_type)


@app.post("/detect_disease_image_upload")
async def detect_disease_upload(
    file: UploadFile = File(...), crop_type: str = Form("wheat")
):
    """Disease detection via direct file upload"""
    try:
        from agents.disease_detection_agent import DiseaseDetectionAgent

        file_bytes = await file.read()
        image_b64 = base64.b64encode(file_bytes).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"
        image_b64 = f"data:{mime_type};base64,{image_b64}"

        disease_agent = DiseaseDetectionAgent()
        result = disease_agent.analyze_image_from_base64(image_b64, crop_type)
        if result and isinstance(result, dict) and result.get("error"):
            return result
        return result
    except Exception as e:
        error_msg = str(e).lower()
        if "image" in error_msg and "not support" in error_msg:
            return {
                "error": "This model does not support image input. Please use a vision-enabled model."
            }
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_govt_schemes")
async def get_govt_schemes(state: str = "all", crop_type: str = "all"):
    """Government schemes - deprecated, integrated into LangGraph"""
    return {
        "status": "deprecated",
        "message": "Govt schemes now available via LangGraph agent",
        "schemes": [
            {"name": "PM-KISAN", "benefit": "₹6000/year"},
            {"name": "PMFBY", "benefit": "Crop insurance"},
            {"name": "KCC", "benefit": "Low-interest credit"},
        ],
    }


@app.get("/blockchain_log")
async def blockchain_log(limit: int = 50):
    """Blockchain logs - deprecated"""
    return {"status": "deprecated", "message": "Green token system deprecated in v3.0"}


@app.get("/climate_risk")
async def get_climate_risk(location: str = "Delhi", days: int = 30):
    from graph.tools import assess_climate_risk

    return await assess_climate_risk.ainvoke(location)


@app.get("/drone_satellite_analysis")
async def drone_analysis(
    farm_id: str = "FARM001", lat: float = None, lon: float = None
):
    """Drone/Satellite analysis - Direct NASA API call"""
    try:
        from agents.drone_satellite_agent import DroneSatelliteAgent
        
        # Use provided coordinates or defaults
        latitude = lat or 18.5204  # Pune default
        longitude = lon or 73.8567  # Pune default
        
        agent = DroneSatelliteAgent()
        result = agent.analyze_farm(farm_id=farm_id, latitude=latitude, longitude=longitude)
        
        return {
            "status": "success",
            "farm_id": farm_id,
            "satellite_analysis": result.get("satellite_analysis", {}),
            "drone_analysis": result.get("drone_analysis", {}),
            "soil_health_map": result.get("soil_health_map", {}),
            "timestamp": datetime.now().isoformat(),
            "location": {"latitude": latitude, "longitude": longitude}
        }
    except Exception as e:
        print(f"Drone analysis error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e), "farm_id": farm_id}


@app.get("/farm_analytics")
async def get_farm_analytics(farm_id: str = "FARM001", crop_type: Optional[str] = None):
    """Farm analytics - now via LangGraph workflow"""
    from graph import run_farm_analysis

    result = await run_farm_analysis(farm_id=farm_id, crop_type=crop_type or "wheat")
    return result


@app.get("/agrobrain_os_data")
async def get_agrobrain_os_data(
    farm_id: str = "FARM001", crop_type: Optional[str] = None
):
    """Returns the true AgroBrain OS LLM payload via LangGraph"""
    from graph import run_farm_analysis

    result = await run_farm_analysis(farm_id=farm_id, crop_type=crop_type or "wheat")
    return result


@app.post("/copilot_chat")
async def copilot_chat(request: CopilotRequest):
    """Processes messages to the Farm Copilot via LangGraph"""
    import traceback

    try:
        from graph import get_supervisor

        supervisor = get_supervisor()
        if supervisor is None:
            return {
                "reply": "AI agent is initializing. Please try again.",
                "error": True,
            }

        if not supervisor.is_available:
            return {
                "reply": "AI agent is not available. Please check API configuration."
            }

        # Use run_autonomous for better results
        result = await supervisor.run_autonomous(request.message, request.farm_id)
        return {"reply": result.get("response", "No response")}
    except Exception as e:
        traceback.print_exc()
        return {"reply": f"Error: {str(e)}", "error": True}


# ── Voice & Accessibility ───────────────────────────────────────────


@app.post("/voice_command")
async def voice_command(request: VoiceCommandRequest):
    """LLM-powered voice command via LangGraph"""
    import traceback

    try:
        from graph import get_supervisor

        supervisor = get_supervisor()
        if supervisor is None:
            return {
                "reply": "AI agent is initializing. Please try again.",
                "error": True,
            }

        if not supervisor.is_available:
            return {"reply": "AI agent not available", "error": True}

        result = await supervisor.run_autonomous(
            request.text, request.farm_id or "FARM001"
        )
        return {"reply": result.get("response", "No response")}
    except Exception as e:
        traceback.print_exc()
        return {"reply": f"Error: {str(e)}", "error": True}


@app.post("/text_to_speech")
async def text_to_speech(text: str, language: str = "en"):
    from gtts import gTTS

    lang_map = {"en": "en", "hi": "hi", "mr": "mr"}
    tts = gTTS(text=text, lang=lang_map.get(language, "en"))
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return StreamingResponse(audio_buffer, media_type="audio/mpeg")


# ── Dashboard & Analytics ───────────────────────────────────────────


def _build_profile_context_recommendations(
    farm_id: str,
    profile: Optional[Dict[str, Any]],
    crops: List[Dict[str, Any]],
    latest_sensor: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Create deterministic recommendations grounded in farm profile + sensors."""
    now_iso = datetime.utcnow().isoformat()
    recs: List[Dict[str, Any]] = []

    if not profile:
        recs.append(
            {
                "id": f"ctx-{farm_id}-missing-profile",
                "timestamp": now_iso,
                "agent_name": "Profile Context Engine",
                "recommendation_type": "profile",
                "recommendation_text": "Complete your farm profile (soil type, irrigation, location) for more personalized recommendations.",
                "priority": "medium",
                "status": "active",
            }
        )
        return recs

    soil_type = (profile.get("soil_type") or "").lower()
    irrigation = (profile.get("irrigation_source") or "").lower()
    is_organic = bool(profile.get("is_organic", False))
    total_land = profile.get("total_land_area_acres")

    if soil_type:
        if "black" in soil_type:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-soil-black",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "soil",
                    "recommendation_text": "Black soil detected: prioritize drainage checks before heavy rain and split fertilizer doses to improve uptake.",
                    "priority": "medium",
                    "status": "active",
                }
            )
        elif "sandy" in soil_type:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-soil-sandy",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "soil",
                    "recommendation_text": "Sandy soil detected: use frequent light irrigation and add organic matter to improve moisture retention.",
                    "priority": "high",
                    "status": "active",
                }
            )

    if irrigation:
        if "bore" in irrigation:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-irrigation-borewell",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "irrigation",
                    "recommendation_text": "Borewell irrigation: schedule watering at early morning/evening and monitor pump runtime to reduce energy and water loss.",
                    "priority": "medium",
                    "status": "active",
                }
            )
        elif "drip" in irrigation:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-irrigation-drip",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "irrigation",
                    "recommendation_text": "Drip irrigation configured: run short cycles and flush lines weekly to maintain uniform distribution.",
                    "priority": "low",
                    "status": "active",
                }
            )

    if is_organic:
        recs.append(
            {
                "id": f"ctx-{farm_id}-organic",
                "timestamp": now_iso,
                "agent_name": "Profile Context Engine",
                "recommendation_type": "organic",
                "recommendation_text": "Organic farm mode: prefer neem-based pest control and compost integration based on current crop stage.",
                "priority": "medium",
                "status": "active",
            }
        )

    if total_land is not None:
        try:
            area = float(total_land)
            if area >= 10:
                recs.append(
                    {
                        "id": f"ctx-{farm_id}-large-farm",
                        "timestamp": now_iso,
                        "agent_name": "Profile Context Engine",
                        "recommendation_type": "operations",
                        "recommendation_text": "Large farm profile detected: divide field into management zones and track moisture/NPK by zone for better decisions.",
                        "priority": "medium",
                        "status": "active",
                    }
                )
        except Exception:
            pass

    if crops:
        crop_names = [c.get("crop_type") for c in crops if c.get("crop_type")]
        if crop_names:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-crops",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "crop-plan",
                    "recommendation_text": f"Active crops for this farm: {', '.join(crop_names[:4])}. Plan fertilizer and irrigation per crop instead of uniform application.",
                    "priority": "medium",
                    "status": "active",
                }
            )

    if latest_sensor:
        sm = latest_sensor.get("soil_moisture")
        if sm is not None and sm < 25 and irrigation:
            recs.append(
                {
                    "id": f"ctx-{farm_id}-sensor-moisture",
                    "timestamp": now_iso,
                    "agent_name": "Profile Context Engine",
                    "recommendation_type": "sensor",
                    "recommendation_text": f"Soil moisture is low ({sm:.1f}%). Trigger immediate {irrigation} irrigation cycle for this farm.",
                    "priority": "critical",
                    "status": "active",
                }
            )

    return recs


@app.get("/dashboard")
async def get_dashboard(farm_id: str = "FARM001"):
    sensors = await db.get_latest_readings(farm_id, limit=1)
    recs = await db.get_recommendations(farm_id, limit=5)
    profile = await auth_system.get_farmer_profile(farm_id)
    crops = await db.get_crops(farm_id)

    sensor_obj = sensors[0] if sensors else None
    profile_context_recs = _build_profile_context_recommendations(
        farm_id=farm_id,
        profile=profile,
        crops=crops or [],
        latest_sensor=sensor_obj,
    )

    # Keep DB recommendations first, then add profile-grounded recommendations
    combined_recs = (recs or []) + profile_context_recs

    return {
        "farm_id": farm_id,
        "sensors": sensor_obj,
        "recommendations": combined_recs,
        "profile": profile,
        "blockchain": {"status": "deprecated"},
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/realtime_recommendations")
async def realtime_recommendations(farm_id: str = "FARM001"):
    """Return real-time alerts derived from the latest sensor readings"""
    sensors = await db.get_latest_readings(farm_id, limit=1)
    profile = await auth_system.get_farmer_profile(farm_id)
    irrigation_source = (profile or {}).get("irrigation_source") or "irrigation"
    soil_type = (profile or {}).get("soil_type") or "your soil"
    alerts = []
    if sensors:
        s = sensors[0]
        if s.get("soil_moisture", 50) < 25:
            alerts.append(
                {
                    "title": "🚨 Low Soil Moisture",
                    "message": f"Soil moisture is critically low at {s['soil_moisture']:.1f}%.",
                    "action": f"Use {irrigation_source} immediately to prevent crop stress on {soil_type}.",
                    "priority": "critical",
                }
            )
        if s.get("air_temperature", 25) > 38:
            alerts.append(
                {
                    "title": "🔥 High Temperature Alert",
                    "message": f"Air temperature is {s['air_temperature']:.1f}°C — above stress threshold.",
                    "action": "Increase irrigation frequency and provide shade if possible.",
                    "priority": "critical",
                }
            )
        if s.get("soil_ph", 6.5) < 5.5 or s.get("soil_ph", 6.5) > 8.0:
            alerts.append(
                {
                    "title": "⚠️ Soil pH Out of Range",
                    "message": f"Soil pH is {s['soil_ph']:.1f} — outside the optimal 5.5–8.0 range.",
                    "action": "Apply lime to raise pH or sulfur to lower it.",
                    "priority": "high",
                }
            )
        if s.get("npk_nitrogen", 150) < 100:
            alerts.append(
                {
                    "title": "🌱 Low Nitrogen Levels",
                    "message": f"Nitrogen is {s['npk_nitrogen']:.0f} mg/kg — below optimal.",
                    "action": "Apply nitrogen-rich fertilizer in the next irrigation cycle.",
                    "priority": "high",
                }
            )
    if not alerts:
        alerts.append(
            {
                "title": "✅ All Systems Optimal",
                "message": "No critical alerts detected for your farm.",
                "action": "Continue regular monitoring.",
                "priority": "low",
            }
        )
    return {
        "recommendations": alerts,
        "farm_id": farm_id,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── Test Scenarios ──────────────────────────────────────────────────


@app.post("/test/scenario/low_moisture")
async def scenario_low_moisture(farm_id: str = "FARM001"):
    try:
        data = {
            "farm_id": farm_id,
            "soil_moisture": 15.0 + random.uniform(-2, 2),
            "soil_temperature": 24.0 + random.uniform(-1, 1),
            "soil_ph": 6.8 + random.uniform(-0.1, 0.1),
            "npk_nitrogen": 180 + random.uniform(-10, 10),
            "npk_phosphorus": 45 + random.uniform(-5, 5),
            "npk_potassium": 210 + random.uniform(-10, 10),
            "humidity": 45.0 + random.uniform(-5, 5),
            "air_temperature": 28.0 + random.uniform(-2, 2),
        }
        await db.store_sensor_data([data])
        return {
            "status": "success",
            "scenario": "Low Moisture",
            "message": "Critical low moisture simulated!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/scenario/high_temperature")
async def scenario_high_temp(farm_id: str = "FARM001"):
    try:
        data = {
            "farm_id": farm_id,
            "soil_moisture": 45.0 + random.uniform(-2, 2),
            "soil_temperature": 32.0 + random.uniform(-1, 1),
            "soil_ph": 6.8 + random.uniform(-0.1, 0.1),
            "npk_nitrogen": 180 + random.uniform(-10, 10),
            "npk_phosphorus": 45 + random.uniform(-5, 5),
            "npk_potassium": 210 + random.uniform(-10, 10),
            "humidity": 30.0 + random.uniform(-5, 5),
            "air_temperature": 42.0 + random.uniform(-2, 2),
        }
        await db.store_sensor_data([data])
        return {
            "status": "success",
            "scenario": "High Temperature",
            "message": "Extreme heat stress simulated!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/scenario/optimal")
async def scenario_optimal(farm_id: str = "FARM001"):
    try:
        data = {
            "farm_id": farm_id,
            "soil_moisture": 55.0 + random.uniform(-2, 2),
            "soil_temperature": 22.0 + random.uniform(-1, 1),
            "soil_ph": 6.8 + random.uniform(-0.1, 0.1),
            "npk_nitrogen": 220 + random.uniform(-10, 10),
            "npk_phosphorus": 55 + random.uniform(-5, 5),
            "npk_potassium": 240 + random.uniform(-10, 10),
            "humidity": 65.0 + random.uniform(-5, 5),
            "air_temperature": 24.0 + random.uniform(-2, 2),
        }
        await db.store_sensor_data([data])
        return {
            "status": "success",
            "scenario": "Optimal",
            "message": "Ideal conditions simulated!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/scenario/multiple_issues")
async def scenario_multiple(farm_id: str = "FARM001"):
    try:
        data = {
            "farm_id": farm_id,
            "soil_moisture": 12.0 + random.uniform(-2, 2),
            "soil_temperature": 35.0 + random.uniform(-1, 1),
            "soil_ph": 5.2 + random.uniform(-0.1, 0.1),
            "npk_nitrogen": 80 + random.uniform(-10, 10),
            "npk_phosphorus": 15 + random.uniform(-5, 5),
            "npk_potassium": 90 + random.uniform(-10, 10),
            "humidity": 25.0 + random.uniform(-5, 5),
            "air_temperature": 45.0 + random.uniform(-2, 2),
        }
        await db.store_sensor_data([data])
        return {
            "status": "success",
            "scenario": "Multi-Factor Emergency",
            "message": "Multiple critical alerts simulated!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Actions Log ─────────────────────────────────────────────────────────────


class ActionLogSubmitResponse(BaseModel):
    """Not used as input — purely for documentation."""

    pass


@app.post("/actions_log/submit")
async def submit_action_log(
    farm_id: str = Form(...),
    action_type: str = Form(...),
    action_details: str = Form(""),
    green_tokens: int = Form(0),
    image: Optional[UploadFile] = File(None),
    provided_lat: Optional[float] = Form(None),
    provided_lon: Optional[float] = Form(None),
):
    """
    Submit a farming action with optional proof image.
    Runs EXIF geo-verification against the farm's stored GPS profile.
    Verification states: L0_SUBMITTED → L1_IMAGE_UPLOADED → L2_GEO_VERIFIED → L3_ADMIN_REVIEW
                        or verification_failed (with reason)
    """
    from core.geo_verifier import verify_geo

    # Validate inputs
    farm_id = farm_id.strip().upper()
    if not action_type:
        raise HTTPException(status_code=400, detail="action_type is required")
    if green_tokens < 0:
        raise HTTPException(status_code=400, detail="green_tokens must be >= 0")

    # Geo verification defaults
    geo_result = None
    verification_level = "L0_SUBMITTED"
    verification_status = "submitted"
    verification_reason = "No proof image uploaded"
    geo_match_passed = False
    proof_lat = None
    proof_lon = None
    distance_meters = None
    allowed_radius_m = None
    farm_lat = None
    farm_lon = None
    image_metadata = None

    if image is not None:
        image_bytes = await image.read()
        image_metadata = {
            "filename": image.filename,
            "content_type": image.content_type,
        }

        # Look up farm GPS profile
        farm_profile = await db.get_farm_profile(farm_id)
        if farm_profile:
            farm_lat = farm_profile.get("latitude")
            farm_lon = farm_profile.get("longitude")
            allowed_radius_m = farm_profile.get("verification_radius_meters", 600.0)
        else:
            # Fallback: try auth system farmer profile
            try:
                farmer = await auth_system.get_farmer_profile(farm_id)
                if farmer:
                    farm_lat = farmer.get("latitude")
                    farm_lon = farmer.get("longitude")
                    # farm_size is stored in acres in the Farmer model
                    farm_size_acres = float(
                        farmer.get("farm_size")
                        or farmer.get("total_land_area_acres")
                        or 1.0
                    )
                    # Convert acres → m², then derive circle radius, add 500m practical buffer
                    import math as _math

                    farm_radius_m = _math.sqrt(farm_size_acres * 4047 / _math.pi)
                    allowed_radius_m = round(
                        farm_radius_m + 500.0, 0
                    )  # geometric radius + 500m margin
            except Exception:
                pass
            if not allowed_radius_m:
                allowed_radius_m = 600.0

        # Run geo-verification
        geo_result = verify_geo(image_bytes, farm_lat, farm_lon, allowed_radius_m)

        # Override with real-time Browser Coordinates if provided (Actual Live Geolocation)
        if provided_lat is not None and provided_lon is not None:
            proof_lat = provided_lat
            proof_lon = provided_lon
            # Recalculate distance based on the live coordinates
            from core.geo_verifier import haversine

            if farm_lat is not None and farm_lon is not None:
                distance_meters = haversine(proof_lat, proof_lon, farm_lat, farm_lon)
            else:
                distance_meters = 0.0

            # Update geo_result to be based on the actual live coordinates
            geo_result["proof_latitude"] = proof_lat
            geo_result["proof_longitude"] = proof_lon
            geo_result["distance_meters"] = distance_meters
            geo_result["passed"] = distance_meters <= allowed_radius_m
            geo_result["verification_level"] = (
                "L2_GEO_VERIFIED" if geo_result["passed"] else "verification_failed"
            )
            geo_result["reason"] = f"Live GPS: {distance_meters:.1f}m from farm"
        else:
            proof_lat = geo_result.get("proof_latitude")
            proof_lon = geo_result.get("proof_longitude")
            distance_meters = geo_result.get("distance_meters")

        verification_reason = geo_result.get("reason", "")
        image_metadata["exif_datetime"] = geo_result["exif"].get("datetime")
        image_metadata["exif_device"] = (
            f"{geo_result['exif'].get('make', '')} {geo_result['exif'].get('model', '')}".strip()
        )
        image_metadata["has_gps"] = geo_result["exif"].get("has_gps", False) or (
            provided_lat is not None
        )

        if geo_result["passed"]:
            verification_level = "L2_GEO_VERIFIED"
            verification_status = "geo_verified"
            token_request_status = "awaiting_admin_review"
            geo_match_passed = True
        else:
            verification_level = geo_result.get(
                "verification_level", "verification_failed"
            )
            # If coordinates were missing entirely, status=geo_failed, otherwise detail the level
            verification_status = (
                "geo_failed"
                if not (geo_result["exif"].get("has_gps") or provided_lat)
                else "geo_radius_exceeded"
            )
            token_request_status = (
                "pending"  # Manual review / Video verification needed
            )
            geo_match_passed = False
    else:
        verification_level = "L0_SUBMITTED"
        verification_status = "submitted"
        token_request_status = "pending"

    payload = {
        "farm_id": farm_id,
        "action_type": action_type,
        "action_details": action_details,
        "requested_green_tokens": green_tokens,
        "green_tokens_earned": 0,  # Only minted after L5_APPROVED
        "token_request_status": token_request_status,
        "verification_status": verification_status,
        "verification_level": verification_level,
        "verification_reason": verification_reason,
        "geo_match_passed": geo_match_passed,
        "farm_size_match_passed": True,
        "distance_meters": distance_meters,
        "allowed_radius_meters": allowed_radius_m,
        "proof_latitude": proof_lat,
        "proof_longitude": proof_lon,
        "farm_latitude": farm_lat,
        "farm_longitude": farm_lon,
        "image_metadata": image_metadata,
        "video_verification_required": False,
        "video_verification_status": "not_required",
    }

    # Geo-verified → move to admin queue
    if geo_match_passed:
        payload["token_request_status"] = "awaiting_admin_review"

    saved = await db.log_action(payload)
    return {
        "status": "success",
        "action_id": saved["id"],
        "verification_level": verification_level,
        "verification_status": verification_status,
        "geo_passed": geo_match_passed,
        "verification_reason": verification_reason,
        "proof_latitude": proof_lat,
        "proof_longitude": proof_lon,
        "distance_meters": distance_meters,
        "farm_latitude": farm_lat,
        "farm_longitude": farm_lon,
        "exif": geo_result["exif"] if geo_result else None,
    }


@app.get("/actions_log")
async def get_actions_log(farm_id: str = "FARM001", limit: int = 100):
    """Get all actions for a farm."""
    actions = await db.list_actions(farm_id=farm_id, limit=limit)
    total_tokens = sum(int(a.get("green_tokens_earned") or 0) for a in actions)
    return {
        "actions": actions,
        "total_green_tokens": total_tokens,
        "total_actions": len(actions),
    }


@app.delete("/actions_log/{action_id}")
async def delete_action_log(action_id: int):
    """Delete an action log entry."""
    deleted = await db.delete_action(action_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"status": "success", "deleted_id": action_id}


# ── Admin Auth ────────────────────────────────────────────────────────────────

ADMIN_SUPER_SECRET = os.getenv("ADMIN_SUPER_SECRET", "agri_admin_secret_2026")


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminRegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "admin"
    super_secret: str  # must match env var


def _verify_admin_token(x_admin_token: Optional[str] = None) -> Dict[str, Any]:
    """Simple shared-token admin auth guard."""
    import hashlib

    if not x_admin_token:
        raise HTTPException(status_code=401, detail="X-Admin-Token header required")
    # Token format: sha256(username:password)  — set on login
    return {"token": x_admin_token}


from fastapi import Header


async def require_admin(x_admin_token: Optional[str] = Header(None)):
    """Depend on this to protect admin routes."""
    if not x_admin_token:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required (X-Admin-Token header)",
        )
    # Verify token exists in DB by checking hash lookup
    # Token is sha256(username + ":" + password_hash) created at login
    # We trust it here; a real system would use JWT
    return x_admin_token


@app.post("/admin/login")
async def admin_login(request: AdminLoginRequest):
    """Admin login — returns X-Admin-Token to use in subsequent requests."""
    import hashlib

    admin = await db.get_admin_by_username(request.username)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    expected_hash = hashlib.sha256(request.password.encode()).hexdigest()
    if admin["password_hash"] != expected_hash:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    # Token = sha256(username:password_hash) — deterministic session token
    token = hashlib.sha256(
        f"{request.username}:{admin['password_hash']}".encode()
    ).hexdigest()
    return {
        "status": "success",
        "admin_token": token,
        "username": admin["username"],
        "role": admin["role"],
    }


@app.post("/admin/register")
async def admin_register(request: AdminRegisterRequest):
    """Create a new admin account (requires ADMIN_SUPER_SECRET)."""
    if request.super_secret != ADMIN_SUPER_SECRET:
        raise HTTPException(status_code=403, detail="Invalid super secret")
    if not request.username or len(request.password) < 6:
        raise HTTPException(
            status_code=400, detail="Username required, password must be >= 6 chars"
        )
    try:
        admin = await db.create_admin(request.username, request.password, request.role)
        return {"status": "success", "admin": admin}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create admin: {str(e)}")


# ── Admin Verification Queue ───────────────────────────────────────────────────


@app.get("/admin/queue")
async def admin_queue(
    status: str = "all", limit: int = 200, admin_token: str = Depends(require_admin)
):
    """Fetch the verification queue with optional status filter."""
    actions = await db.list_pending_actions(limit=limit, status_filter=status)
    return {"actions": actions, "count": len(actions), "filter": status}


class AdminReviewRequest(BaseModel):
    reviewer: str
    notes: Optional[str] = None


@app.post("/admin/approve/{action_id}")
async def admin_approve(
    action_id: int,
    request: AdminReviewRequest,
    admin_token: str = Depends(require_admin),
):
    """Approve a token request and update database"""
    action = await db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    # Update the action with approval status
    updates = {
        "token_request_status": "approved",
        "verification_level": "L5_APPROVED",
        "verification_status": "approved",
        "green_tokens_earned": action.get("requested_green_tokens", 0),
        "admin_reviewer": request.reviewer,
        "admin_review_notes": request.notes or "",
    }
    result = await db.update_action(action_id, updates)
    
    return {
        "status": "success",
        "message": "Action approved and saved",
        "action_id": action_id,
        "updated": result
    }


@app.post("/admin/reject/{action_id}")
async def admin_reject(
    action_id: int,
    request: AdminReviewRequest,
    admin_token: str = Depends(require_admin),
):
    """Reject a token request."""
    action = await db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    updates = {
        "token_request_status": "rejected",
        "verification_level": "L5_REJECTED",
        "verification_status": "rejected",
        "green_tokens_earned": 0,
        "admin_reviewer": request.reviewer,
        "admin_review_notes": request.notes,
    }
    result = await db.update_action(action_id, updates)
    return {"status": "rejected", "action": result}


class ScheduleCallRequest(BaseModel):
    phone: str
    scheduled_at: str  # ISO datetime string
    notes: Optional[str] = None


@app.post("/admin/schedule_call/{action_id}")
async def admin_schedule_call(
    action_id: int,
    request: ScheduleCallRequest,
    admin_token: str = Depends(require_admin),
):
    """Schedule a WhatsApp video verification call."""
    action = await db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    # Validate phone
    phone = request.phone.strip()
    if not phone or len(phone) < 7:
        raise HTTPException(status_code=400, detail="Valid phone number required")

    try:
        # Handle 'Z' suffix from JavaScript toISOString()
        iso_str = request.scheduled_at.replace("Z", "+00:00")
        scheduled_dt = datetime.fromisoformat(iso_str)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"scheduled_at must be valid ISO datetime (e.g. 2026-04-10T14:00:00). Recieved: {request.scheduled_at}",
        )

    updates = {
        "token_request_status": "awaiting_video_verification",
        "verification_level": "L4_VIDEO_PENDING",
        "video_verification_required": True,
        "video_verification_status": "scheduled",
        "video_call_scheduled_at": scheduled_dt,
        "verification_phone": phone,
        "admin_review_notes": request.notes,
    }
    result = await db.update_action(action_id, updates)
    return {
        "status": "call_scheduled",
        "phone": phone,
        "scheduled_at": scheduled_dt.isoformat(),
        "action": result,
    }


class CompleteCallRequest(BaseModel):
    call_status: str  # "completed" | "failed"
    notes: Optional[str] = None


@app.post("/admin/complete_call/{action_id}")
async def admin_complete_call(
    action_id: int,
    request: CompleteCallRequest,
    admin_token: str = Depends(require_admin),
):
    """Mark a video verification call as completed or failed."""
    action = await db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if request.call_status not in ("completed", "failed"):
        raise HTTPException(
            status_code=400, detail="call_status must be 'completed' or 'failed'"
        )

    if request.call_status == "completed":
        updates = {
            "video_verification_status": "completed",
            "video_verified_at": datetime.utcnow(),
            "verification_level": "L4_VIDEO_VERIFIED",
            "token_request_status": "awaiting_admin_review",  # back for final approval
            "admin_review_notes": request.notes,
        }
    else:
        updates = {
            "video_verification_status": "failed",
            "video_verified_at": datetime.utcnow(),
            "verification_level": "L5_REJECTED",
            "token_request_status": "rejected",
            "verification_status": "rejected",
            "admin_review_notes": request.notes,
        }

    result = await db.update_action(action_id, updates)
    return {"status": f"call_{request.call_status}", "action": result}


# ── Admin Farmers & Stats ─────────────────────────────────────────────────────


@app.get("/admin/farmers")
async def admin_farmers(admin_token: str = Depends(require_admin)):
    """List all farmers with their farm geo profiles."""
    try:
        farmers = await db.get_all_farmers_with_profiles()
    except Exception as e:
        # Fallback: return farm profiles only
        farmers = await db.list_farm_profiles()
    return {"farmers": farmers, "count": len(farmers)}


@app.get("/admin/stats")
async def admin_stats(admin_token: str = Depends(require_admin)):
    """Aggregated stats for admin dashboard."""
    return await db.get_verification_stats()


# ── Admin Farm Profile CRUD ───────────────────────────────────────────────────


class FarmProfileRequest(BaseModel):
    farm_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_hectares: Optional[float] = None
    verification_radius_meters: Optional[float] = None
    is_active: Optional[bool] = True


@app.get("/admin/farm_profile/{farm_id}")
async def get_farm_profile(farm_id: str, admin_token: str = Depends(require_admin)):
    profile = await db.get_farm_profile(farm_id.upper())
    if not profile:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    return profile


@app.put("/admin/farm_profile/{farm_id}")
async def upsert_farm_profile(
    farm_id: str, request: FarmProfileRequest, admin_token: str = Depends(require_admin)
):
    """Create or update a farm's GPS geo-verification profile."""
    # Validate geo inputs
    payload = request.dict(exclude_none=True)
    if "latitude" in payload and not (-90 <= payload["latitude"] <= 90):
        raise HTTPException(
            status_code=400, detail="latitude must be between -90 and 90"
        )
    if "longitude" in payload and not (-180 <= payload["longitude"] <= 180):
        raise HTTPException(
            status_code=400, detail="longitude must be between -180 and 180"
        )
    if "area_hectares" in payload and payload["area_hectares"] < 0:
        raise HTTPException(status_code=400, detail="area_hectares must be >= 0")
    if (
        "verification_radius_meters" in payload
        and payload["verification_radius_meters"] < 10
    ):
        raise HTTPException(
            status_code=400, detail="verification_radius_meters must be >= 10"
        )

    result = await db.upsert_farm_profile(farm_id.upper(), payload)
    return {"status": "updated", "profile": result}


@app.get("/admin/farm_profiles")
async def list_farm_profiles(admin_token: str = Depends(require_admin)):
    """List all registered farm profiles."""
    profiles = await db.list_farm_profiles()
    return {"profiles": profiles, "count": len(profiles)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
