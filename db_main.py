"""
Smart Farming Agentic AI System ΓÇö Main Backend Server
=====================================================
FastAPI Application Entry Point
Now fully async with PostgreSQL + SQLAlchemy
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import configuration
from config import API_CONFIG

# Import all agents
from agents.lead_agent import LeadAgent
from agents.soil_agent import SoilAgent
from agents.weather_collector_agent import WeatherCollectorAgent
from agents.weather_forecast_agent import WeatherForecastAgent
from agents.water_management_agent import WaterManagementAgent
from agents.fertilizer_agent import FertilizerAgent
from agents.disease_detection_agent import DiseaseDetectionAgent
from agents.yield_prediction_agent import YieldPredictionAgent
from agents.market_forecast_agent import MarketForecastAgent
from agents.market_integration_agent import MarketIntegrationAgent
from agents.govt_scheme_agent import GovtSchemeAgent
from agents.blockchain_agent import BlockchainAgent
from agents.sustainability_agent import SustainabilityAgent
from agents.drone_satellite_agent import DroneSatelliteAgent
from agents.climate_risk_agent import ClimateRiskAgent
from agents.voice_assistant_agent import VoiceAssistantAgent
from agents.speech_recognition_agent import SpeechRecognitionAgent

from core.database import Database
from core.sensor_simulator import SensorSimulator
from core.auth_system import AuthenticationSystem
from core.db_session import init_db, close_db
from core.context_builder import context_builder

# Initialize FastAPI
app = FastAPI(
    title="Smart Farming AI System",
    description="Agentic AI System for Precision Agriculture ΓÇö PostgreSQL + Async",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
sensor_sim = SensorSimulator()
lead_agent = LeadAgent(db)
auth_system = AuthenticationSystem()

# Initialize ML-powered Market Forecast Agent with API key
market_forecast_agent = MarketForecastAgent(api_key=API_CONFIG.get('data_gov_api_key'))

# Initialize Weather Agents with OpenWeather API key
weather_collector_agent = WeatherCollectorAgent(api_key=API_CONFIG.get('openweather_api_key'))
weather_forecast_agent = WeatherForecastAgent(api_key=API_CONFIG.get('openweather_api_key'))

# ΓöÇΓöÇ Request Models ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SensorDataRequest(BaseModel):
    farm_id: str = "FARM001"
    duration_minutes: int = 1

class VoiceCommandRequest(BaseModel):
    text: str
    language: str = "en"

class SpeechRecognitionRequest(BaseModel):
    audio_base64: str
    language: str = "en"

class DiseaseDetectionRequest(BaseModel):
    image_data: Optional[str] = None
    crop_type: str = "wheat"
    symptoms: List[str] = []

class YieldPredictionRequest(BaseModel):
    crop_type: str
    area_hectares: float
    soil_quality: str = "medium"

class CropRequest(BaseModel):
    farm_id: str
    crop_type: str
    planted_date: str
    expected_harvest_date: str
    area_hectares: float
    status: str = "active"

class ActionLogRequest(BaseModel):
    farm_id: str
    action_type: str
    action_details: str
    green_tokens: int = 0

class RegisterRequest(BaseModel):
    farmer_id: str
    password: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    language: str = "en"

class LoginRequest(BaseModel):
    farmer_id: str
    password: str

class SessionVerifyRequest(BaseModel):
    session_id: str

class ChangePasswordRequest(BaseModel):
    farmer_id: str
    old_password: str
    new_password: str

class FieldRequest(BaseModel):
    farmer_id: str
    field_name: str
    area_hectares: float = 1.0
    soil_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None


# ΓöÇΓöÇ Health Check ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Smart Farming AI System",
        "version": "2.0.0",
        "database": "PostgreSQL (async)",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system_status")
async def system_status():
    """Check if system is using 100% live APIs"""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "apis": {
            "market_prices": {
                "agent": market_forecast_agent.name,
                "data_source": "data.gov.in (100% Live API)",
                "api_key_configured": bool(API_CONFIG.get('data_gov_api_key')),
                "no_base_prices": True
            },
            "weather": {
                "collector": weather_collector_agent.name,
                "forecaster": weather_forecast_agent.name,
                "data_source": "OpenWeather API (100% Live)",
                "api_key_configured": bool(API_CONFIG.get('openweather_api_key')),
                "no_simulations": True
            }
        },
        "database": "PostgreSQL (async + pgvector)",
        "backend_version": "2.0 - PostgreSQL + Agent Memory",
        "last_restart": datetime.now().isoformat()
    }


# ΓöÇΓöÇ Startup / Shutdown ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

@app.on_event("startup")
async def startup_event():
    """Initialize database and default data on startup"""
    try:
        print("≡ƒùä∩╕Å Initializing PostgreSQL database...")
        await init_db()
        print("Γ£à PostgreSQL tables created/verified")

        # Ensure default field exists
        await db.ensure_default_field("FARM001")

        # Generate initial sensor data if none exists
        sensor_data = await db.get_latest_sensor_data("FARM001", limit=1)
        if not sensor_data:
            print("≡ƒî▒ Initializing default sensor data...")
            data = sensor_sim.generate_sensor_data(farm_id="FARM001", duration_minutes=5)
            await db.store_sensor_data(data)
            print("Γ£à Default sensor data created")
    except Exception as e:
        print(f"ΓÜá∩╕Å Startup initialization warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections"""
    await close_db()
    print("≡ƒöî Database connections closed")


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        result = await auth_system.register_user(
            farmer_id=request.farmer_id,
            password=request.password,
            name=request.name,
            email=request.email,
            phone=request.phone,
            language=request.language
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login user and create session"""
    try:
        result = await auth_system.login_user(
            farmer_id=request.farmer_id,
            password=request.password
        )
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/verify")
async def verify_session(request: SessionVerifyRequest):
    """Verify if session is valid"""
    try:
        result = await auth_system.verify_session(request.session_id)
        if not result["valid"]:
            raise HTTPException(status_code=401, detail=result.get("error", "Invalid session"))
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/logout")
async def logout(request: SessionVerifyRequest):
    """Logout user"""
    try:
        result = await auth_system.logout_user(request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/change_password")
async def change_password(request: ChangePasswordRequest):
    """Change user password"""
    try:
        result = await auth_system.change_password(
            farmer_id=request.farmer_id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/users")
async def get_users():
    """Get list of all registered users (admin endpoint)"""
    try:
        users = await auth_system.get_all_users()
        return {"users": users, "count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DATA ENDPOINTS
# ============================================

@app.post("/simulate_sensors")
async def simulate_sensors(request: SensorDataRequest):
    """Generate and store simulated sensor data"""
    try:
        data = sensor_sim.generate_sensor_data(
            farm_id=request.farm_id,
            duration_minutes=request.duration_minutes
        )
        await db.store_sensor_data(data)
        return {
            "status": "success",
            "farm_id": request.farm_id,
            "readings_generated": len(data),
            "latest_reading": data[-1] if data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_agents")
async def run_agents(farm_id: str = "FARM001"):
    """Execute all AI agents and get recommendations"""
    try:
        sensor_data = await db.get_latest_sensor_data(farm_id, limit=1)
        if not sensor_data:
            data = sensor_sim.generate_sensor_data(farm_id=farm_id, duration_minutes=1)
            await db.store_sensor_data(data)

        result = await lead_agent.orchestrate_all_agents(farm_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agents: {str(e)}")

# Weather Data
@app.get("/get_weather")
async def get_weather(location: str = "Delhi"):
    """Get current weather data from OpenWeather API"""
    try:
        data = weather_collector_agent.collect_weather(location)
        # Cache to PostgreSQL
        try:
            await db.cache_api_response(
                source="openweather", endpoint="current_weather",
                location=location, response_payload=data, ttl_seconds=1800,
            )
        except Exception:
            pass  # Non-critical
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weather Forecast
@app.get("/get_forecast")
async def get_forecast(location: str = "Delhi", hours: int = 24):
    """Get weather forecast"""
    try:
        forecast = weather_forecast_agent.predict_weather(location, hours)
        try:
            await db.cache_api_response(
                source="openweather", endpoint="forecast",
                location=location, response_payload=forecast, ttl_seconds=1800,
            )
        except Exception:
            pass
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Yield Prediction
@app.post("/predict_yield")
async def predict_yield(request: YieldPredictionRequest):
    """Predict crop yield"""
    try:
        yield_agent = YieldPredictionAgent(db)
        prediction = yield_agent.predict_yield(
            crop_type=request.crop_type,
            area_hectares=request.area_hectares,
            soil_quality=request.soil_quality
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Disease Detection
@app.post("/detect_disease")
async def detect_disease(request: DiseaseDetectionRequest):
    """Detect crop diseases"""
    try:
        disease_agent = DiseaseDetectionAgent()
        result = disease_agent.detect_disease(
            crop_type=request.crop_type,
            symptoms=request.symptoms
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market Forecast
@app.get("/get_market_forecast")
async def get_market_forecast(crop: str = "wheat"):
    """Get ML-based market price forecast"""
    try:
        forecast = market_forecast_agent.forecast_prices(crop)
        try:
            await db.cache_api_response(
                source="data_gov_in", endpoint="market_prices",
                location=crop, response_payload=forecast, ttl_seconds=3600,
            )
        except Exception:
            pass
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/model_accuracy")
async def get_model_accuracy():
    """Get ML model accuracy metrics"""
    try:
        return {
            "success": True,
            "metrics": market_forecast_agent.accuracy_metrics,
            "explanation": {
                "r2_score": "Overall prediction accuracy (0-1 scale)",
                "mae": "Mean Absolute Error - Average price difference in Γé╣",
                "rmse": "Root Mean Squared Error - Prediction error margin in Γé╣",
                "mape": "Mean Absolute Percentage Error (%)",
                "accuracy_percentage": "Model accuracy as a percentage"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market/train_model")
async def train_model(crop: str):
    """Train ML model for a specific crop"""
    try:
        result = market_forecast_agent.train_ml_model(crop)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Government Schemes
@app.get("/get_govt_schemes")
async def get_govt_schemes(state: str = "all", crop_type: str = "all"):
    """Get applicable government schemes"""
    try:
        govt_agent = GovtSchemeAgent()
        schemes = govt_agent.get_applicable_schemes(state, crop_type)
        return schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blockchain Logs
@app.get("/blockchain_log")
async def blockchain_log(limit: int = 50):
    """Get blockchain transaction history"""
    try:
        blockchain_agent = BlockchainAgent()
        logs = blockchain_agent.get_recent_logs(limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice Command
@app.post("/voice_command")
async def voice_command(request: VoiceCommandRequest):
    """Process voice commands from text"""
    try:
        voice_agent = VoiceAssistantAgent(db)
        response = voice_agent.process_command(request.text, request.language)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Text-to-Speech
from fastapi.responses import StreamingResponse
import io

@app.post("/text_to_speech")
async def text_to_speech(text: str, language: str = "en"):
    """Convert text to speech audio"""
    try:
        from gtts import gTTS
        lang_map = {"en": "en", "hi": "hi", "mr": "mr"}
        lang_code = lang_map.get(language, "en")
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return StreamingResponse(
            audio_buffer, media_type="audio/mpeg",
            headers={"Content-Disposition": f"inline; filename=speech_{language}.mp3"}
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="gTTS not installed. Run: pip install gtts")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Speech Recognition
@app.post("/speech_to_text")
async def speech_to_text(request: SpeechRecognitionRequest):
    """Convert speech audio to text"""
    try:
        speech_agent = SpeechRecognitionAgent()
        speech_result = speech_agent.recognize_from_audio_data(request.audio_base64, request.language)
        if speech_result["status"] == "success":
            voice_agent = VoiceAssistantAgent(db)
            voice_response = voice_agent.process_command(speech_result["text"], request.language)
            return {
                "speech_recognition": speech_result,
                "voice_assistant_response": voice_response,
                "recognized_text": speech_result["text"],
                "status": "success"
            }
        else:
            return {
                "speech_recognition": speech_result,
                "status": "error",
                "error": speech_result.get("error", "Speech recognition failed")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard Data
@app.get("/dashboard")
async def get_dashboard_data(farm_id: str = "FARM001"):
    """Get complete dashboard data"""
    try:
        sensor_data = await db.get_latest_sensor_data(farm_id)
        recommendations = await lead_agent.get_latest_recommendations(farm_id)
        blockchain_agent = BlockchainAgent()
        blockchain_stats = blockchain_agent.get_stats()
        return {
            "farm_id": farm_id,
            "timestamp": datetime.now().isoformat(),
            "sensors": sensor_data,
            "recommendations": recommendations,
            "blockchain": blockchain_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Recommendations
@app.get("/realtime_recommendations")
async def get_realtime_recommendations(farm_id: str = "FARM001"):
    """Get real-time recommendations based on current sensor data"""
    try:
        realtime_recs = await lead_agent.generate_realtime_recommendations(farm_id)
        return {
            "farm_id": farm_id,
            "timestamp": datetime.now().isoformat(),
            "recommendations": realtime_recs,
            "count": len(realtime_recs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Green Token Balance
@app.get("/green_tokens/{farm_id}")
async def get_green_tokens(farm_id: str):
    """Get Green Token balance"""
    try:
        blockchain_agent = BlockchainAgent()
        balance = blockchain_agent.get_balance(farm_id)
        return {"farm_id": farm_id, "balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sync Actions to Blockchain
@app.post("/sync_actions_to_blockchain")
async def sync_actions_to_blockchain(farm_id: str = "FARM001"):
    """Sync all database actions to blockchain"""
    try:
        actions = await db.get_actions_log(farm_id=farm_id, limit=1000)
        blockchain_agent = BlockchainAgent()
        synced_count = 0
        errors = []
        chain = blockchain_agent.get_full_chain()
        existing_actions = set()
        for block in chain:
            if block.get("index", 0) > 0:
                data = block.get("data", {})
                action_id = f"{data.get('farm_id')}_{data.get('action_type')}_{data.get('timestamp')}"
                existing_actions.add(action_id)

        for action in actions:
            try:
                action_id = f"{farm_id}_{action.get('action_type')}_{action.get('timestamp')}"
                if action_id in existing_actions:
                    continue
                result = blockchain_agent.add_transaction(
                    farm_id=farm_id,
                    action_type=action.get('action_type', 'unknown'),
                    action_details=action.get('action_details', ''),
                    green_tokens=action.get('green_tokens_earned', 0)
                )
                if result.get("status") == "success":
                    synced_count += 1
                else:
                    errors.append(f"Failed to sync action {action.get('id')}")
            except Exception as e:
                errors.append(f"Error syncing: {str(e)}")

        new_balance = blockchain_agent.get_balance(farm_id)
        return {
            "status": "success",
            "message": f"Synced {synced_count} actions to blockchain",
            "synced_count": synced_count,
            "total_actions": len(actions),
            "new_balance": new_balance,
            "errors": errors if errors else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Verify Blockchain
@app.get("/verify_blockchain")
async def verify_blockchain():
    """Verify blockchain integrity"""
    try:
        blockchain_agent = BlockchainAgent()
        is_valid = blockchain_agent.validate_chain()
        chain_data = blockchain_agent.get_full_chain()
        return {
            "is_valid": is_valid,
            "total_blocks": len(chain_data),
            "message": "Blockchain is valid and secure!" if is_valid else "Blockchain integrity compromised!",
            "chain": chain_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Green Token Summary
@app.get("/green_token_summary")
async def green_token_summary(farm_id: str = "FARM001"):
    """Get comprehensive Green Token summary"""
    try:
        blockchain_agent = BlockchainAgent()
        balance = blockchain_agent.get_balance(farm_id)
        chain = blockchain_agent.get_full_chain()
        logs = [block for block in chain if block.get("index", 0) > 0]

        total_earned = sum([
            block.get("data", {}).get("green_tokens_earned", 0)
            for block in logs
            if block.get("data", {}).get("green_tokens_earned", 0) > 0
        ])
        total_spent = sum([
            abs(block.get("data", {}).get("green_tokens_earned", 0))
            for block in logs
            if block.get("data", {}).get("green_tokens_earned", 0) < 0
        ])

        action_counts = {}
        for block in logs:
            action = block.get("data", {}).get("action_type", "Unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        earning_actions = {}
        for block in logs:
            tokens = block.get("data", {}).get("green_tokens_earned", 0)
            if tokens > 0:
                action = block.get("data", {}).get("action_type", "Unknown")
                earning_actions[action] = earning_actions.get(action, 0) + tokens
        top_earners = sorted(earning_actions.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "farm_id": farm_id,
            "current_balance": balance,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "net_tokens": total_earned - total_spent,
            "total_transactions": len(logs),
            "action_breakdown": action_counts,
            "top_earning_actions": [{"action": a, "tokens": t} for a, t in top_earners],
            "sustainability_level": "Excellent" if balance > 200 else "Good" if balance > 100 else "Fair" if balance > 50 else "Improving"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blockchain Blocks
@app.get("/blockchain_blocks")
async def get_blockchain_blocks():
    """Get all blockchain blocks"""
    try:
        blockchain_agent = BlockchainAgent()
        chain = blockchain_agent.get_full_chain()
        enriched_blocks = []
        for i, block in enumerate(chain):
            block_data = block.get("data", {})
            action = block_data.get("action_type", "Genesis Block" if i == 0 else "Unknown")
            tokens = block_data.get("green_tokens_earned", 0)
            farm_id = block_data.get("farm_id", "FARM001")
            enriched_blocks.append({
                "block_number": i,
                "timestamp": block.get("timestamp", "N/A"),
                "action": action,
                "agent_responsible": block_data.get("agent", "System"),
                "tokens_awarded": tokens,
                "previous_hash": block.get("previous_hash", "0"),
                "current_hash": block.get("hash", "N/A"),
                "farm_id": farm_id,
                "data": block_data
            })
        return {
            "total_blocks": len(enriched_blocks),
            "blocks": enriched_blocks,
            "chain_valid": blockchain_agent.validate_chain()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Auto-reward eco-friendly action
@app.post("/reward_action")
async def reward_action(request: Dict[str, Any]):
    """Automatically reward eco-friendly farming actions"""
    try:
        blockchain_agent = BlockchainAgent()
        action_type = request.get("action_type", "")
        farm_id = request.get("farm_id", "FARM001")
        details = request.get("details", {})
        tokens = blockchain_agent.calculate_green_tokens(action_type, details)
        transaction_data = {"action": action_type, "farm_id": farm_id, "details": details, "green_tokens": tokens}
        blockchain_agent.add_transaction(transaction_data)
        return {
            "success": True,
            "action": action_type,
            "tokens_awarded": tokens,
            "new_balance": blockchain_agent.get_balance(farm_id),
            "message": f"Congratulations! You earned {tokens} Green Tokens for {action_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Climate Risk
@app.get("/climate_risk")
async def get_climate_risk(location: str = "Delhi", days: int = 30):
    """Get climate risk assessment"""
    try:
        climate_agent = ClimateRiskAgent()
        risk = climate_agent.assess_risk(location, days)
        return risk
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Drone/Satellite
@app.get("/drone_satellite_analysis")
async def get_drone_satellite_analysis(farm_id: str = "FARM001", latitude: float = None, longitude: float = None):
    """Get real-time NASA satellite data + drone analysis"""
    try:
        drone_agent = DroneSatelliteAgent()
        analysis = drone_agent.analyze_farm(farm_id, latitude=latitude, longitude=longitude)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drone_analysis")
async def get_drone_analysis(farm_id: str = "FARM001"):
    """Legacy endpoint"""
    return await get_drone_satellite_analysis(farm_id)


# ============================================
# CROPS MANAGEMENT ENDPOINTS
# ============================================

@app.post("/crops")
async def add_crop(request: CropRequest):
    """Add new crop"""
    try:
        crop_id = await db.add_crop(
            farm_id=request.farm_id,
            crop_type=request.crop_type,
            planted_date=request.planted_date,
            expected_harvest_date=request.expected_harvest_date,
            area_hectares=request.area_hectares,
            status=request.status
        )
        return {"status": "success", "message": "Crop added successfully", "crop_id": crop_id, "crop_type": request.crop_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crops")
async def get_crops(farm_id: str = "FARM001", status: str = None):
    """Get all crops for a farm"""
    try:
        crops = await db.get_crops(farm_id=farm_id, status=status)
        return {"status": "success", "farm_id": farm_id, "crops": crops, "count": len(crops)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/crops/{crop_id}/status")
async def update_crop_status(crop_id: str, status: str):
    """Update crop status"""
    try:
        await db.update_crop_status(crop_id=crop_id, status=status)
        return {"status": "success", "message": f"Crop {crop_id} status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/crops/{crop_id}")
async def delete_crop(crop_id: str):
    """Delete crop"""
    try:
        await db.delete_crop(crop_id=crop_id)
        return {"status": "success", "message": f"Crop {crop_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ACTIONS LOG ENDPOINTS
# ============================================

@app.post("/actions_log")
async def log_action(request: ActionLogRequest):
    """Log a farming action"""
    try:
        await db.log_action(
            farm_id=request.farm_id,
            action_type=request.action_type,
            action_details=request.action_details,
            green_tokens=request.green_tokens
        )
        blockchain_agent = BlockchainAgent()
        blockchain_result = blockchain_agent.add_transaction(
            farm_id=request.farm_id,
            action_type=request.action_type,
            action_details=request.action_details,
            green_tokens=request.green_tokens
        )
        new_balance = blockchain_agent.get_balance(request.farm_id)
        return {
            "status": "success",
            "message": "Action logged and synced to blockchain",
            "action_type": request.action_type,
            "green_tokens_earned": request.green_tokens,
            "new_balance": new_balance,
            "blockchain_synced": blockchain_result.get("status") == "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions_log")
async def get_actions_log(farm_id: str = "FARM001", limit: int = 50):
    """Get actions log with blockchain as source of truth"""
    try:
        blockchain_agent = BlockchainAgent()
        blockchain_balance = blockchain_agent.get_balance(farm_id)
        blockchain_stats = blockchain_agent.get_stats()
        chain = blockchain_agent.get_full_chain()
        blockchain_actions = []
        for block in chain:
            if block.get("index", 0) > 0:
                data = block.get("data", {})
                if data.get("farm_id") == farm_id:
                    blockchain_actions.append({
                        "id": block.get("index"),
                        "action_type": data.get("action_type", "unknown"),
                        "action_details": data.get("action_details", ""),
                        "green_tokens_earned": data.get("green_tokens_earned", 0),
                        "timestamp": data.get("timestamp", block.get("timestamp")),
                        "source": "blockchain"
                    })
        blockchain_actions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        blockchain_actions = blockchain_actions[:limit]
        total_tokens = sum(a.get('green_tokens_earned', 0) for a in blockchain_actions)
        return {
            "status": "success", "farm_id": farm_id,
            "actions": blockchain_actions, "count": len(blockchain_actions),
            "total_green_tokens": total_tokens,
            "blockchain_balance": blockchain_balance,
            "data_source": "blockchain",
            "blockchain_stats": {
                "total_blocks": blockchain_stats.get("total_blocks", 0),
                "total_transactions": blockchain_stats.get("total_transactions", 0),
                "is_valid": blockchain_stats.get("chain_valid", True)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions_log/{action_id}")
async def get_action_by_id(action_id: str):
    """Get specific action by ID"""
    try:
        action = await db.get_action_by_id(action_id=action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        return {"status": "success", "action": action}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/actions_log/{action_id}")
async def delete_action(action_id: str):
    """Delete action from log"""
    try:
        await db.delete_action(action_id=action_id)
        return {"status": "success", "message": f"Action {action_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# NEW: CONTEXT & MEMORY ENDPOINTS
# ============================================

@app.get("/api/context/{farm_id}")
async def get_context(farm_id: str):
    """
    Get the full assembled context for a farm (debugging + transparency).
    Shows exactly what the LLM sees.
    """
    try:
        context = await context_builder.build_context(farm_id, depth="full")
        return {
            "status": "success",
            "farm_id": farm_id,
            "context": context,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent_memory/{farm_id}")
async def get_agent_memory(farm_id: str, agent_name: str = None, limit: int = 20):
    """View agent memory logs ΓÇö what agents have computed and decided."""
    try:
        memory = await db.get_agent_memory(farm_id, agent_name=agent_name, limit=limit)
        return {
            "status": "success",
            "farm_id": farm_id,
            "memory_logs": memory,
            "count": len(memory),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensor_trends/{farm_id}")
async def get_sensor_trends(farm_id: str, days: int = 7):
    """Get sensor trend analysis over N days."""
    try:
        context = await context_builder.build_context(farm_id, depth="full")
        return {
            "status": "success",
            "farm_id": farm_id,
            "trends": context.get("sensor_trends_7d", {}),
            "crop_timeline": context.get("crop_timeline", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TEST SCENARIOS
# ============================================

@app.post("/test/scenario/low_moisture")
async def test_low_moisture_scenario(farm_id: str = "FARM001"):
    """TEST: Simulate low soil moisture scenario"""
    try:
        import random
        sensor_data = {
            "farm_id": farm_id, "timestamp": datetime.now().isoformat(),
            "soil_moisture": 25.0 + random.uniform(-5, 5),
            "air_temperature": 28.0 + random.uniform(-2, 2),
            "soil_temperature": 24.0 + random.uniform(-2, 2),
            "humidity": 45.0 + random.uniform(-5, 5),
            "soil_ph": 6.8 + random.uniform(-0.2, 0.2),
            "npk_nitrogen": 180 + random.uniform(-20, 20),
            "npk_phosphorus": 20 + random.uniform(-5, 5),
            "npk_potassium": 190 + random.uniform(-20, 20)
        }
        await db.store_sensor_data([sensor_data])
        return {"status": "success", "scenario": "Low Moisture (Critical)", "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/scenario/acidic_soil")
async def test_acidic_soil_scenario(farm_id: str = "FARM001"):
    """TEST: Simulate acidic soil scenario"""
    try:
        import random
        sensor_data = {
            "farm_id": farm_id, "timestamp": datetime.now().isoformat(),
            "soil_moisture": 55.0 + random.uniform(-5, 5),
            "air_temperature": 26.0 + random.uniform(-2, 2),
            "soil_temperature": 23.0 + random.uniform(-2, 2),
            "humidity": 60.0 + random.uniform(-5, 5),
            "soil_ph": 5.2 + random.uniform(-0.3, 0.3),
            "npk_nitrogen": 200 + random.uniform(-20, 20),
            "npk_phosphorus": 22 + random.uniform(-3, 3),
            "npk_potassium": 210 + random.uniform(-20, 20)
        }
        await db.store_sensor_data([sensor_data])
        return {"status": "success", "scenario": "Acidic Soil (High Priority)", "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/scenario/high_temperature")
async def test_high_temperature_scenario(farm_id: str = "FARM001"):
    """TEST: Simulate high temperature scenario"""
    try:
        import random
        sensor_data = {
            "farm_id": farm_id, "timestamp": datetime.now().isoformat(),
            "soil_moisture": 50.0 + random.uniform(-5, 5),
            "air_temperature": 42.0 + random.uniform(-2, 2),
            "soil_temperature": 35.0 + random.uniform(-2, 2),
            "humidity": 30.0 + random.uniform(-5, 5),
            "soil_ph": 7.0 + random.uniform(-0.2, 0.2),
            "npk_nitrogen": 220 + random.uniform(-20, 20),
            "npk_phosphorus": 25 + random.uniform(-3, 3),
            "npk_potassium": 230 + random.uniform(-20, 20)
        }
        await db.store_sensor_data([sensor_data])
        return {"status": "success", "scenario": "High Temperature (Critical)", "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/scenario/optimal")
async def test_optimal_scenario(farm_id: str = "FARM001"):
    """TEST: Simulate optimal conditions"""
    try:
        import random
        sensor_data = {
            "farm_id": farm_id, "timestamp": datetime.now().isoformat(),
            "soil_moisture": 55.0 + random.uniform(-3, 3),
            "air_temperature": 25.0 + random.uniform(-2, 2),
            "soil_temperature": 22.0 + random.uniform(-1, 1),
            "humidity": 65.0 + random.uniform(-5, 5),
            "soil_ph": 6.8 + random.uniform(-0.1, 0.1),
            "npk_nitrogen": 220 + random.uniform(-10, 10),
            "npk_phosphorus": 25 + random.uniform(-2, 2),
            "npk_potassium": 220 + random.uniform(-10, 10)
        }
        await db.store_sensor_data([sensor_data])
        return {"status": "success", "scenario": "Optimal Conditions", "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test/scenario/multiple_issues")
async def test_multiple_issues_scenario(farm_id: str = "FARM001"):
    """TEST: Simulate multiple issues at once"""
    try:
        import random
        sensor_data = {
            "farm_id": farm_id, "timestamp": datetime.now().isoformat(),
            "soil_moisture": 28.0 + random.uniform(-3, 3),
            "air_temperature": 41.0 + random.uniform(-2, 2),
            "soil_temperature": 34.0 + random.uniform(-2, 2),
            "humidity": 35.0 + random.uniform(-5, 5),
            "soil_ph": 5.1 + random.uniform(-0.2, 0.2),
            "npk_nitrogen": 110 + random.uniform(-10, 10),
            "npk_phosphorus": 10 + random.uniform(-2, 2),
            "npk_potassium": 120 + random.uniform(-10, 10)
        }
        await db.store_sensor_data([sensor_data])
        return {"status": "success", "scenario": "Multiple Critical Issues", "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("≡ƒî╛ Starting Smart Farming AI System v2.0...")
    print("≡ƒùä∩╕Å Database: PostgreSQL (async + pgvector)")
    print("≡ƒôí Server: http://localhost:8000")
    print("≡ƒôÜ API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
