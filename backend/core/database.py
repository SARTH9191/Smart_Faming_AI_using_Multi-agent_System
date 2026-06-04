import os
import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, Text, ForeignKey, select, desc, JSON, Integer, Boolean, update, func
from pathlib import Path

# ── Base Model ──────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Models ─────────────────────────────────────────────────────────

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Soil Data
    soil_moisture: Mapped[float] = mapped_column(Float)
    soil_temperature: Mapped[float] = mapped_column(Float)
    soil_ph: Mapped[float] = mapped_column(Float)
    
    # Nutrients
    npk_nitrogen: Mapped[float] = mapped_column(Float)
    npk_phosphorus: Mapped[float] = mapped_column(Float)
    npk_potassium: Mapped[float] = mapped_column(Float)
    
    # Environment
    humidity: Mapped[float] = mapped_column(Float)
    air_temperature: Mapped[float] = mapped_column(Float)
    rainfall: Mapped[float] = mapped_column(Float, nullable=True)
    light_intensity: Mapped[float] = mapped_column(Float, nullable=True)

class AgentRecommendation(Base):
    __tablename__ = "agent_recommendations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    agent_name: Mapped[str] = mapped_column(String(100))
    recommendation_type: Mapped[str] = mapped_column(String(50)) # irrigation, fertilizer, pest, harvest
    recommendation_text: Mapped[Text] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20)) # critical, high, medium, low
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, applied, dismissed
    
    llm_source: Mapped[str] = mapped_column(String(100), nullable=True) # e.g. "mistral:latest"
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

class LLMConversation(Base):
    __tablename__ = "llm_conversation_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    prompt_sent: Mapped[Text] = mapped_column(Text)
    response_received: Mapped[Text] = mapped_column(Text)
    model_used: Mapped[str] = mapped_column(String(100))
    metadata_used: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)

class Crop(Base):
    __tablename__ = "crops"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), index=True)
    crop_type: Mapped[str] = mapped_column(String(100))
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    planted_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expected_harvest: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    area_hectares: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="growing") # growing, ready, harvested
    yield_estimate: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)


class ActionLogRecord(Base):
    __tablename__ = "actions_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    action_type: Mapped[str] = mapped_column(String(100))
    action_details: Mapped[str] = mapped_column(Text, nullable=True)

    requested_green_tokens: Mapped[int] = mapped_column(Integer, default=0)
    green_tokens_earned: Mapped[int] = mapped_column(Integer, default=0)
    token_request_status: Mapped[str] = mapped_column(String(50), default="pending")

    verification_status: Mapped[str] = mapped_column(String(50), default="submitted")
    verification_level: Mapped[str] = mapped_column(String(50), default="L0_SUBMITTED")
    verification_reason: Mapped[str] = mapped_column(Text, nullable=True)

    geo_match_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    farm_size_match_passed: Mapped[bool] = mapped_column(Boolean, default=True)
    distance_meters: Mapped[float] = mapped_column(Float, nullable=True)
    allowed_radius_meters: Mapped[float] = mapped_column(Float, nullable=True)

    proof_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    proof_longitude: Mapped[float] = mapped_column(Float, nullable=True)
    farm_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    farm_longitude: Mapped[float] = mapped_column(Float, nullable=True)

    image_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    admin_reviewer: Mapped[str] = mapped_column(String(100), nullable=True)
    admin_review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    video_verification_required: Mapped[bool] = mapped_column(Boolean, default=False)
    video_verification_status: Mapped[str] = mapped_column(String(50), default="pending")
    video_call_scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    video_verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    blockchain_tx_hash: Mapped[str] = mapped_column(String(128), nullable=True)
    verification_phone: Mapped[str] = mapped_column(String(30), nullable=True)  # WhatsApp call number


class Admin(Base):
    """Admin users for the verification dashboard."""
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(30), default="admin")  # admin | superadmin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FarmProfile(Base):
    __tablename__ = "farm_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    farm_name: Mapped[str] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=True)
    verification_radius_meters: Mapped[float] = mapped_column(Float, default=600.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ── Database Class ──────────────────────────────────────────────────

class AsyncDatabase:
    def __init__(self, database_url: str):
        # Handle SQLite for local development
        if database_url.startswith("sqlite"):
            self.engine = create_async_engine(database_url)
        else:
            self.engine = create_async_engine(database_url, pool_pre_ping=True)
            
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def init_db(self):
        """Create tables if they don't exist"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def store_sensor_data(self, readings: List[Dict[str, Any]]):
        """Store new sensor readings"""
        async with self.session_factory() as session:
            for r in readings:
                reading = SensorReading(
                    farm_id=r.get("farm_id", "default_farm"),
                    soil_moisture=r.get("soil_moisture", 0.0),
                    soil_temperature=r.get("soil_temperature", 0.0),
                    soil_ph=r.get("soil_ph", 7.0),
                    npk_nitrogen=r.get("npk_nitrogen", 0.0),
                    npk_phosphorus=r.get("npk_phosphorus", 0.0),
                    npk_potassium=r.get("npk_potassium", 0.0),
                    humidity=r.get("humidity", 0.0),
                    air_temperature=r.get("air_temperature", 0.0),
                    rainfall=r.get("rainfall"),
                    light_intensity=r.get("light_intensity")
                )
                session.add(reading)
            await session.commit()

    async def get_latest_readings(self, farm_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Get latest sensor readings for a farm"""
        async with self.session_factory() as session:
            query = select(SensorReading).where(SensorReading.farm_id == farm_id).order_by(desc(SensorReading.timestamp)).limit(limit)
            result = await session.execute(query)
            readings = result.scalars().all()
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "soil_moisture": r.soil_moisture,
                    "soil_temperature": r.soil_temperature,
                    "soil_ph": r.soil_ph,
                    "npk_nitrogen": r.npk_nitrogen,
                    "npk_phosphorus": r.npk_phosphorus,
                    "npk_potassium": r.npk_potassium,
                    "humidity": r.humidity,
                    "air_temperature": r.air_temperature,
                    "rainfall": r.rainfall,
                    "light_intensity": r.light_intensity
                } for r in readings
            ]

    async def store_recommendation(self, rec: Dict[str, Any]):
        """Store a new AI recommendation"""
        async with self.session_factory() as session:
            recommendation = AgentRecommendation(
                farm_id=rec.get("farm_id", "default_farm"),
                agent_name=rec.get("agent_name", "Unknown"),
                recommendation_type=rec.get("recommendation_type", "general"),
                recommendation_text=rec.get("recommendation_text", ""),
                priority=rec.get("priority", "medium"),
                llm_source=rec.get("llm_source"),
                metadata_json=rec.get("metadata", {})
            )
            session.add(recommendation)
            await session.commit()

    async def get_recommendations(self, farm_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent recommendations"""
        async with self.session_factory() as session:
            query = select(AgentRecommendation).where(AgentRecommendation.farm_id == farm_id).order_by(desc(AgentRecommendation.created_at)).limit(limit)
            result = await session.execute(query)
            recs = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "timestamp": r.created_at.isoformat(),
                    "agent_name": r.agent_name,
                    "recommendation_type": r.recommendation_type,
                    "recommendation_text": r.recommendation_text,
                    "priority": r.priority,
                    "status": r.status
                } for r in recs
            ]

    async def store_llm_conversation(self, farm_id: str, prompt_sent: str, response_received: str, model_used: str, context_used: Dict[str, Any], latency_ms: float = None):
        """Log LLM conversation for audit/history"""
        async with self.session_factory() as session:
            conv = LLMConversation(
                farm_id=farm_id,
                prompt_sent=prompt_sent,
                response_received=response_received,
                model_used=model_used,
                context_used=context_used,
                latency_ms=latency_ms
            )
            session.add(conv)
            await session.commit()

    # ── Crop Management ──────────────────────────────────────────────

    async def store_crop(self, crop_data: Dict[str, Any]):
        """Store a new crop record"""
        async with self.session_factory() as session:
            crop = Crop(
                farm_id=crop_data.get("farm_id"),
                crop_type=crop_data.get("crop_type"),
                variety=crop_data.get("variety"),
                planted_date=datetime.fromisoformat(crop_data["planted_date"]) if crop_data.get("planted_date") else datetime.utcnow(),
                area_hectares=float(crop_data.get("area_hectares", 1.0)),
                status=crop_data.get("status", "growing"),
                latitude=crop_data.get("latitude"),
                longitude=crop_data.get("longitude")
            )
            session.add(crop)
            await session.commit()
            return crop.id

    async def get_crops(self, farm_id: str) -> List[Dict[str, Any]]:
        """Get all crops for a farm"""
        async with self.session_factory() as session:
            stmt = select(Crop).where(Crop.farm_id == farm_id).order_by(desc(Crop.planted_date))
            result = await session.execute(stmt)
            crops = result.scalars().all()
            return [
                {
                    "id": c.id,
                    "crop_type": c.crop_type,
                    "variety": c.variety,
                    "planted_date": c.planted_date.isoformat(),
                    "expected_harvest": c.expected_harvest.isoformat() if c.expected_harvest else None,
                    "area_hectares": c.area_hectares,
                    "status": c.status,
                    "yield_estimate": c.yield_estimate,
                    "latitude": c.latitude,
                    "longitude": c.longitude
                } for c in crops
            ]

    async def update_crop(self, crop_id: int, crop_data: Dict[str, Any]):
        """Update a crop record"""
        async with self.session_factory() as session:
            stmt = select(Crop).where(Crop.id == crop_id)
            result = await session.execute(stmt)
            crop = result.scalars().first()
            if crop:
                if "crop_type" in crop_data:
                    crop.crop_type = crop_data["crop_type"]
                if "area_hectares" in crop_data:
                    crop.area_hectares = crop_data["area_hectares"]
                if "planted_date" in crop_data:
                    crop.planted_date = datetime.fromisoformat(crop_data["planted_date"])
                if "latitude" in crop_data:
                    crop.latitude = crop_data["latitude"]
                if "longitude" in crop_data:
                    crop.longitude = crop_data["longitude"]
                if "status" in crop_data:
                    crop.status = crop_data["status"]
                await session.commit()

    async def update_crop_status(self, crop_id: int, status: str):
        """Update the status of a specific crop"""
        async with self.session_factory() as session:
            stmt = update(Crop).where(Crop.id == crop_id).values(status=status)
            await session.execute(stmt)
            await session.commit()

    async def delete_crop(self, crop_id: int):
        """Delete a crop record"""
        async with self.session_factory() as session:
            from sqlalchemy import delete
            stmt = delete(Crop).where(Crop.id == crop_id)
            await session.execute(stmt)
            await session.commit()

    # ── Action Verification Workflow ───────────────────────────────

    def _action_to_dict(self, action: ActionLogRecord) -> Dict[str, Any]:
        return {
            "id": action.id,
            "farm_id": action.farm_id,
            "timestamp": action.created_at.isoformat() if action.created_at else None,
            "updated_at": action.updated_at.isoformat() if action.updated_at else None,
            "action_type": action.action_type,
            "action_details": action.action_details,
            "requested_green_tokens": action.requested_green_tokens,
            "green_tokens_earned": action.green_tokens_earned,
            "token_request_status": action.token_request_status,
            "verification_status": action.verification_status,
            "verification_level": action.verification_level,
            "verification_reason": action.verification_reason,
            "geo_match_passed": action.geo_match_passed,
            "farm_size_match_passed": action.farm_size_match_passed,
            "distance_meters": action.distance_meters,
            "allowed_radius_meters": action.allowed_radius_meters,
            "proof_latitude": action.proof_latitude,
            "proof_longitude": action.proof_longitude,
            "farm_latitude": action.farm_latitude,
            "farm_longitude": action.farm_longitude,
            "image_metadata": action.image_metadata,
            "admin_reviewer": action.admin_reviewer,
            "admin_review_notes": action.admin_review_notes,
            "video_verification_required": action.video_verification_required,
            "video_verification_status": action.video_verification_status,
            "video_call_scheduled_at": action.video_call_scheduled_at.isoformat() if action.video_call_scheduled_at else None,
            "video_verified_at": action.video_verified_at.isoformat() if action.video_verified_at else None,
            "blockchain_tx_hash": action.blockchain_tx_hash,
            "verification_phone": action.verification_phone,
        }


    async def log_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with self.session_factory() as session:
            action = ActionLogRecord(
                farm_id=payload.get("farm_id", "FARM001"),
                action_type=payload.get("action_type", "unknown"),
                action_details=payload.get("action_details"),
                requested_green_tokens=int(payload.get("requested_green_tokens", 0) or 0),
                green_tokens_earned=int(payload.get("green_tokens_earned", 0) or 0),
                token_request_status=payload.get("token_request_status", "pending"),
                verification_status=payload.get("verification_status", "submitted"),
                verification_level=payload.get("verification_level", "L0_SUBMITTED"),
                verification_reason=payload.get("verification_reason"),
                geo_match_passed=bool(payload.get("geo_match_passed", False)),
                farm_size_match_passed=bool(payload.get("farm_size_match_passed", True)),
                distance_meters=payload.get("distance_meters"),
                allowed_radius_meters=payload.get("allowed_radius_meters"),
                proof_latitude=payload.get("proof_latitude"),
                proof_longitude=payload.get("proof_longitude"),
                farm_latitude=payload.get("farm_latitude"),
                farm_longitude=payload.get("farm_longitude"),
                image_metadata=payload.get("image_metadata"),
                admin_reviewer=payload.get("admin_reviewer"),
                admin_review_notes=payload.get("admin_review_notes"),
                video_verification_required=bool(payload.get("video_verification_required", False)),
                video_verification_status=payload.get("video_verification_status", "pending"),
                video_call_scheduled_at=payload.get("video_call_scheduled_at"),
                video_verified_at=payload.get("video_verified_at"),
                blockchain_tx_hash=payload.get("blockchain_tx_hash"),
            )
            session.add(action)
            await session.commit()
            await session.refresh(action)
            return self._action_to_dict(action)

    async def get_action(self, action_id: int) -> Optional[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(ActionLogRecord).where(ActionLogRecord.id == action_id)
            result = await session.execute(stmt)
            action = result.scalars().first()
            return self._action_to_dict(action) if action else None

    async def list_actions(self, farm_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(ActionLogRecord)
            if farm_id:
                stmt = stmt.where(ActionLogRecord.farm_id == farm_id)
            stmt = stmt.order_by(desc(ActionLogRecord.created_at)).limit(limit)
            result = await session.execute(stmt)
            actions = result.scalars().all()
            return [self._action_to_dict(action) for action in actions]

    async def list_pending_actions(self, limit: int = 100, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(ActionLogRecord)
            pending_statuses = ["pending", "awaiting_review", "awaiting_admin_review", "awaiting_video_verification"]
            
            if status_filter and status_filter != "all":
                if status_filter == "pending":
                    stmt = stmt.where(ActionLogRecord.token_request_status.in_(pending_statuses))
                elif status_filter == "geo_failed":
                    stmt = stmt.where(ActionLogRecord.verification_status.in_(["geo_failed", "geo_radius_exceeded"]))
                elif status_filter == "video_pending":
                    stmt = stmt.where(ActionLogRecord.video_verification_status == "scheduled")
                elif status_filter == "approved":
                    stmt = stmt.where(ActionLogRecord.token_request_status == "approved")
                elif status_filter == "rejected":
                    stmt = stmt.where(ActionLogRecord.token_request_status == "rejected")
            # If status_filter is "all" or None, show all records (no additional where clause)

            stmt = stmt.order_by(desc(ActionLogRecord.created_at)).limit(limit)
            result = await session.execute(stmt)
            actions = result.scalars().all()
            return [self._action_to_dict(action) for action in actions]

    async def update_action(self, action_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(ActionLogRecord).where(ActionLogRecord.id == action_id)
            result = await session.execute(stmt)
            action = result.scalars().first()
            if not action:
                return None

            for key, value in updates.items():
                if hasattr(action, key):
                    setattr(action, key, value)

            action.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(action)
            return self._action_to_dict(action)

    async def delete_action(self, action_id: int) -> bool:
        async with self.session_factory() as session:
            stmt = select(ActionLogRecord).where(ActionLogRecord.id == action_id)
            result = await session.execute(stmt)
            action = result.scalars().first()
            if not action:
                return False
            await session.delete(action)
            await session.commit()
            return True

    async def get_actions_summary(self, farm_id: Optional[str] = None) -> Dict[str, Any]:
        actions = await self.list_actions(farm_id=farm_id, limit=1000)
        total_tokens = sum(int(item.get("green_tokens_earned", 0) or 0) for item in actions)
        status_counts: Dict[str, int] = {}
        level_counts: Dict[str, int] = {}
        for item in actions:
            status = item.get("token_request_status", "unknown")
            level = item.get("verification_level", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            level_counts[level] = level_counts.get(level, 0) + 1
        return {
            "total_actions": len(actions),
            "total_green_tokens": total_tokens,
            "status_counts": status_counts,
            "verification_level_counts": level_counts,
        }

    # ── Farm Profile Helpers ───────────────────────────────────────

    def _farm_profile_to_dict(self, profile: FarmProfile) -> Dict[str, Any]:
        return {
            "farm_id": profile.farm_id,
            "farm_name": profile.farm_name,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "area_hectares": profile.area_hectares,
            "verification_radius_meters": profile.verification_radius_meters,
            "is_active": profile.is_active,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    async def get_farm_profile(self, farm_id: str) -> Optional[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(FarmProfile).where(FarmProfile.farm_id == farm_id)
            result = await session.execute(stmt)
            profile = result.scalars().first()
            return self._farm_profile_to_dict(profile) if profile else None

    async def upsert_farm_profile(self, farm_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with self.session_factory() as session:
            stmt = select(FarmProfile).where(FarmProfile.farm_id == farm_id)
            result = await session.execute(stmt)
            profile = result.scalars().first()

            if not profile:
                profile = FarmProfile(farm_id=farm_id)
                session.add(profile)

            profile.farm_name = payload.get("farm_name", profile.farm_name)
            profile.latitude = payload.get("latitude", profile.latitude)
            profile.longitude = payload.get("longitude", profile.longitude)
            profile.area_hectares = payload.get("area_hectares", profile.area_hectares)
            profile.verification_radius_meters = float(payload.get("verification_radius_meters", profile.verification_radius_meters or 600.0))
            profile.is_active = bool(payload.get("is_active", True))
            profile.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(profile)
            return self._farm_profile_to_dict(profile)

    async def list_farm_profiles(self, limit: int = 200) -> List[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(FarmProfile).order_by(desc(FarmProfile.updated_at)).limit(limit)
            result = await session.execute(stmt)
            profiles = result.scalars().all()
            return [self._farm_profile_to_dict(profile) for profile in profiles]

    # ── Admin Helpers ──────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    async def get_admin_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        async with self.session_factory() as session:
            stmt = select(Admin).where(Admin.username == username, Admin.is_active == True)
            result = await session.execute(stmt)
            admin = result.scalars().first()
            if not admin:
                return None
            return {
                "id": admin.id,
                "username": admin.username,
                "password_hash": admin.password_hash,
                "role": admin.role,
                "created_at": admin.created_at.isoformat(),
            }

    async def create_admin(self, username: str, password: str, role: str = "admin") -> Dict[str, Any]:
        async with self.session_factory() as session:
            admin = Admin(
                username=username,
                password_hash=self._hash_password(password),
                role=role,
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return {"id": admin.id, "username": admin.username, "role": admin.role}

    async def get_all_farmers_with_profiles(self) -> List[Dict[str, Any]]:
        """Return all farmers joined with their FarmProfile (if any)."""
        from core.auth_system import Farmer as AuthFarmer
        async with self.session_factory() as session:
            # Fetch farmers from auth table
            from sqlalchemy import text
            try:
                farmer_stmt = select(AuthFarmer).order_by(AuthFarmer.farmer_id)
                result = await session.execute(farmer_stmt)
                farmers = result.scalars().all()
            except Exception:
                # auth_system uses a different session/engine — fall back to farm_profiles table alone
                farmers = []

            # Fetch all farm profiles as a dict
            profile_stmt = select(FarmProfile)
            profile_result = await session.execute(profile_stmt)
            profiles = {p.farm_id: self._farm_profile_to_dict(p) for p in profile_result.scalars().all()}

            rows = []
            for f in farmers:
                profile = profiles.get(f.farmer_id, {})
                rows.append({
                    "farmer_id": f.farmer_id,
                    "name": f.name,
                    "phone": f.phone,
                    "email": f.email,
                    "location": getattr(f, 'location', None),
                    "farm_latitude": profile.get("latitude") or getattr(f, 'latitude', None),
                    "farm_longitude": profile.get("longitude") or getattr(f, 'longitude', None),
                    "farm_size": profile.get("area_hectares") or getattr(f, 'farm_size', None),
                    "verification_radius_meters": profile.get("verification_radius_meters"),
                    "farm_name": profile.get("farm_name"),
                    "has_profile": bool(profile),
                })

            # Also include farm_profiles that have no matching auth farmer
            seen_ids = {f.farmer_id for f in farmers}
            for farm_id, profile in profiles.items():
                if farm_id not in seen_ids:
                    rows.append({
                        "farmer_id": farm_id,
                        "name": profile.get("farm_name", farm_id),
                        "phone": None,
                        "email": None,
                        "location": None,
                        "farm_latitude": profile.get("latitude"),
                        "farm_longitude": profile.get("longitude"),
                        "farm_size": profile.get("area_hectares"),
                        "verification_radius_meters": profile.get("verification_radius_meters"),
                        "farm_name": profile.get("farm_name"),
                        "has_profile": True,
                    })
            return rows

    async def get_verification_stats(self) -> Dict[str, Any]:
        """Aggregate counts for admin dashboard stats panel."""
        async with self.session_factory() as session:
            # Total distinct farm_ids (farmers)
            farm_count_result = await session.execute(
                select(func.count(func.distinct(ActionLogRecord.farm_id)))
            )
            total_farmers = farm_count_result.scalar() or 0

            # Total action log records
            total_result = await session.execute(select(func.count(ActionLogRecord.id)))
            total_actions = total_result.scalar() or 0

            # Pending (awaiting admin review)
            pending_result = await session.execute(
                select(func.count(ActionLogRecord.id)).where(
                    ActionLogRecord.token_request_status.in_(["pending", "awaiting_admin_review", "awaiting_video_verification"])
                )
            )
            pending = pending_result.scalar() or 0

            approved_result = await session.execute(
                select(func.count(ActionLogRecord.id)).where(ActionLogRecord.token_request_status == "approved")
            )
            approved = approved_result.scalar() or 0

            rejected_result = await session.execute(
                select(func.count(ActionLogRecord.id)).where(ActionLogRecord.token_request_status == "rejected")
            )
            rejected = rejected_result.scalar() or 0

            geo_failed_result = await session.execute(
                select(func.count(ActionLogRecord.id)).where(ActionLogRecord.verification_status == "geo_failed")
            )
            geo_failed = geo_failed_result.scalar() or 0

            token_sum_result = await session.execute(
                select(func.sum(ActionLogRecord.green_tokens_earned)).where(
                    ActionLogRecord.token_request_status == "approved"
                )
            )
            total_tokens_minted = token_sum_result.scalar() or 0

            return {
                "total_farmers": total_farmers,
                "total_actions": total_actions,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "geo_failed": geo_failed,
                "total_tokens_minted": total_tokens_minted,
            }
