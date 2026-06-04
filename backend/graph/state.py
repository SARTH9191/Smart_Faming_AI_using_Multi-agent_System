"""
Farm State - TypedDict for LangGraph State
==========================================
Defines the state structure that flows through the agent workflow.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class FarmState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    Each node can read/write to these fields.
    """

    # Input
    farm_id: str
    user_query: str

    # Sensor data (from DB)
    sensors: Optional[Dict[str, Any]]

    # Weather data
    weather_current: Optional[Dict[str, Any]]
    weather_forecast: Optional[Dict[str, Any]]

    # Agent outputs
    soil_analysis: Optional[Dict[str, Any]]
    irrigation_decision: Optional[Dict[str, Any]]
    fertilizer_recommendation: Optional[Dict[str, Any]]
    disease_detection: Optional[Dict[str, Any]]
    yield_prediction: Optional[Dict[str, Any]]
    market_forecast: Optional[Dict[str, Any]]
    climate_risk: Optional[Dict[str, Any]]

    # Meta
    conflicts: List[str]
    reasoning_trace: List[str]
    final_advice: str
    confidence: str
    timestamp: str

    # Error tracking
    errors: List[str]
    failed_tools: List[str]


class AgentRequest(BaseModel):
    """Request model for running agents"""

    farm_id: str
    query: str = "Analyze my farm and provide recommendations"
    location: str = "Pune"


class ChatRequest(BaseModel):
    """Request model for chat"""

    message: str
    farm_id: str = "FARM001"
    history: List[Dict[str, str]] = []


class ToolResult(BaseModel):
    """Standard tool result format"""

    tool_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
