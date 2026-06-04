"""
SQLAlchemy ORM Models — Smart Farming AI System
================================================
10 tables designed following database-design + postgres-best-practices skills:
  • UUIDs for distributed-ready PKs
  • TIMESTAMPTZ on every table
  • JSONB for flexible payloads
  • pgvector for semantic search over recommendations
  • Proper FKs with ON DELETE CASCADE
"""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from core.db_session import Base


# ── Helper ──────────────────────────────────────────────────────────
def gen_uuid():
    return uuid.uuid4()


# ====================================================================
# 1. FARMERS  (replaces old `users` table in auth_system)
# ====================================================================
class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    farmer_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g. FARM001
    password_hash = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    language = Column(String(5), default="en")  # en / hi / mr
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Farm Details
    total_land_area_acres = Column(Float, nullable=True)
    number_of_crops = Column(Integer, nullable=True)
    crops_names = Column(Text, nullable=True)  # Comma-separated crop names
    sowing_date = Column(Date, nullable=True)
    sowed_land_area_acres = Column(Float, nullable=True)

    # Relationships
    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="farmer", cascade="all, delete-orphan")


# ====================================================================
# 2. FIELDS  (NEW — each farmer can have multiple fields)
# ====================================================================
class Field(Base):
    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(200), nullable=False)  # e.g. "North Plot"
    area_hectares = Column(Float, default=1.0)
    soil_type = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(200), nullable=True)  # e.g. "Pune"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="fields")
    crop_cycles = relationship("CropCycle", back_populates="field", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="field", cascade="all, delete-orphan")
    api_cache = relationship("ExternalApiCache", back_populates="field", cascade="all, delete-orphan")
    agent_memory_logs = relationship("AgentMemoryLog", back_populates="field", cascade="all, delete-orphan")
    agent_recommendations = relationship("AgentRecommendation", back_populates="field", cascade="all, delete-orphan")
    actions_log = relationship("ActionLog", back_populates="field", cascade="all, delete-orphan")
    llm_history = relationship("LlmConversationHistory", back_populates="field", cascade="all, delete-orphan")


# ====================================================================
# 3. CROP CYCLES  (replaces old `crops` table — richer timeline)
# ====================================================================
class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String(100), nullable=False)  # wheat, rice, tomato
    planted_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    actual_harvest_date = Column(Date, nullable=True)
    growth_stage = Column(String(50), default="seedling")  # seedling / vegetative / flowering / maturity
    status = Column(String(20), default="active")  # active / harvested / failed
    metadata_ = Column("metadata", JSONB, default=dict)  # variety, seed source, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    field = relationship("Field", back_populates="crop_cycles")

    __table_args__ = (
        Index("ix_crop_cycles_field_status", "field_id", "status"),
    )


# ====================================================================
# 4. SENSOR READINGS  (time-series — replaces old `sensor_data`)
# ====================================================================
class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    reading_time = Column(DateTime(timezone=True), server_default=func.now())
    soil_moisture = Column(Float, nullable=True)
    soil_ph = Column(Float, nullable=True)
    soil_temperature = Column(Float, nullable=True)
    air_temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    light_intensity = Column(Float, nullable=True)
    npk_nitrogen = Column(Float, nullable=True)
    npk_phosphorus = Column(Float, nullable=True)
    npk_potassium = Column(Float, nullable=True)
    source = Column(String(50), default="simulator")  # simulator / iot_device
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    field = relationship("Field", back_populates="sensor_readings")

    __table_args__ = (
        Index("ix_sensor_field_time", "field_id", "reading_time"),
    )


# ====================================================================
# 5. EXTERNAL API CACHE  (NEW — persists weather, market API responses)
# ====================================================================
class ExternalApiCache(Base):
    __tablename__ = "external_api_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(50), nullable=False)    # openweather / data_gov_in / nasa
    endpoint = Column(String(100), nullable=False)  # current_weather / forecast / market_prices
    location = Column(String(200), nullable=True)
    response_payload = Column(JSONB, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    ttl_seconds = Column(Integer, default=1800)  # 30 min default

    # Relationships
    field = relationship("Field", back_populates="api_cache")

    __table_args__ = (
        Index("ix_api_cache_source_loc_time", "source", "location", "fetched_at"),
    )


# ====================================================================
# 6. AGENT MEMORY LOGS  (NEW — every agent run is recorded)
# ====================================================================
class AgentMemoryLog(Base):
    __tablename__ = "agent_memory_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    agent_name = Column(String(100), nullable=False)  # SoilAgent, WeatherAgent, etc.
    action = Column(String(50), nullable=False)  # analyze, recommend, detect
    input_context = Column(JSONB, default=dict)  # what the agent received
    output_result = Column(JSONB, default=dict)  # what the agent produced
    summary = Column(Text, nullable=True)  # human-readable one-liner
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    field = relationship("Field", back_populates="agent_memory_logs")

    __table_args__ = (
        Index("ix_agent_memory_field_agent_time", "field_id", "agent_name", "created_at"),
    )


# ====================================================================
# 7. AGENT RECOMMENDATIONS  (replaces old `recommendations` — richer)
# ====================================================================
class AgentRecommendation(Base):
    __tablename__ = "agent_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    recommendation_type = Column(String(50), nullable=True)  # irrigation / fertilizer / disease / global
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # critical / high / medium / low / info
    status = Column(String(20), default="pending")  # pending / accepted / dismissed / expired
    context_snapshot = Column(JSONB, default=dict)  # shared_context at time of generation
    llm_source = Column(String(20), default="rule_based")  # llm / rule_based
    # pgvector embedding for semantic search
    embedding = Column(Vector(384), nullable=True)  # 384-dim (all-MiniLM-L6-v2)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    field = relationship("Field", back_populates="agent_recommendations")

    __table_args__ = (
        Index("ix_rec_field_status_time", "field_id", "status", "created_at"),
    )


# ====================================================================
# 8. ACTIONS LOG  (same as before, now linked to fields)
# ====================================================================
class ActionLog(Base):
    __tablename__ = "actions_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False)
    action_details = Column(Text, nullable=True)
    green_tokens_earned = Column(Integer, default=0)
    blockchain_tx_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    field = relationship("Field", back_populates="actions_log")


# ====================================================================
# 9. SESSIONS  (replaces old sessions in auth_system.db)
# ====================================================================
class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="sessions")


# ====================================================================
# 10. LLM CONVERSATION HISTORY  (NEW — every Mistral call logged)
# ====================================================================
class LlmConversationHistory(Base):
    __tablename__ = "llm_conversation_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    prompt_sent = Column(Text, nullable=False)
    response_received = Column(Text, nullable=True)
    model_used = Column(String(100), default="mistral:latest")
    context_used = Column(JSONB, default=dict)
    prompt_tokens = Column(Integer, nullable=True)
    response_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    field = relationship("Field", back_populates="llm_history")

    __table_args__ = (
        Index("ix_llm_history_field_time", "field_id", "created_at"),
    )
