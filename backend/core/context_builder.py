"""
🧠 CONTEXT BUILDER — The Brain's Long-Term Memory
==================================================
Assembles a rich context object from PostgreSQL to feed into the LLM prompt.
Queries sensor trends, crop timelines, past recommendations, recent actions,
and cached API data to build a comprehensive picture for the AI.

This is the KEY component that transforms the system from "reactive" to "reflective".
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_models import (
    SensorReading, CropCycle, AgentMemoryLog,
    AgentRecommendation, ActionLog, ExternalApiCache,
    LlmConversationHistory, Field, Farmer,
)
from core.db_session import get_db_context


class ContextBuilder:
    """
    Builds a rich context dictionary for any field, pulling from multiple
    PostgreSQL tables. The output is designed to be injected directly
    into an LLM prompt.
    """

    async def build_context(
        self,
        farm_id: str,
        depth: str = "full",
        session: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Build the full context for a field.

        Args:
            farm_id:  Legacy farm_id (e.g. "FARM001") or field UUID
            depth:    "full" (all sections) | "light" (current + crop only)
            session:  Optional existing AsyncSession

        Returns:
            Rich context dict ready for LLM prompt injection.
        """
        async def _do(s: AsyncSession):
            field_id = await self._resolve_field_id(s, farm_id)
            if not field_id:
                return {"error": "Field not found", "farm_id": farm_id}

            context = {
                "farm_id": farm_id,
                "field_id": str(field_id),
                "built_at": datetime.now(timezone.utc).isoformat(),
            }

            # Always include: current snapshot + crop timeline
            context["current_snapshot"] = await self._get_current_snapshot(s, field_id)
            context["crop_timeline"] = await self._get_crop_timeline(s, field_id)

            if depth == "full":
                context["sensor_trends_7d"] = await self._get_sensor_trends(s, field_id, days=7)
                context["recent_weather_api"] = await self._get_recent_weather(s, field_id)
                context["recent_market_api"] = await self._get_recent_market(s)
                context["past_recommendations"] = await self._get_past_recommendations(s, field_id, limit=5)
                context["past_actions"] = await self._get_past_actions(s, field_id, limit=5)
                context["agent_memory_summary"] = await self._get_agent_memory_summary(s, field_id, limit=5)

            return context

        if session:
            return await _do(session)
        async with get_db_context() as s:
            return await _do(s)

    # ── Section Builders ───────────────────────────────────────────

    async def _get_current_snapshot(
        self, s: AsyncSession, field_id: UUID
    ) -> Dict[str, Any]:
        """Latest sensor reading — the 'now'."""
        stmt = (
            select(SensorReading)
            .where(SensorReading.field_id == field_id)
            .order_by(desc(SensorReading.reading_time))
            .limit(1)
        )
        result = await s.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            return {"status": "no_sensor_data"}

        return {
            "reading_time": row.reading_time.isoformat() if row.reading_time else None,
            "soil_moisture": row.soil_moisture,
            "soil_ph": row.soil_ph,
            "soil_temperature": row.soil_temperature,
            "air_temperature": row.air_temperature,
            "humidity": row.humidity,
            "rainfall": row.rainfall,
            "light_intensity": row.light_intensity,
            "npk_nitrogen": row.npk_nitrogen,
            "npk_phosphorus": row.npk_phosphorus,
            "npk_potassium": row.npk_potassium,
        }

    async def _get_crop_timeline(
        self, s: AsyncSession, field_id: UUID
    ) -> Dict[str, Any]:
        """Active crop cycle — what is currently planted and its timeline."""
        stmt = (
            select(CropCycle)
            .where(CropCycle.field_id == field_id, CropCycle.status == "active")
            .order_by(desc(CropCycle.planted_date))
            .limit(1)
        )
        result = await s.execute(stmt)
        crop = result.scalar_one_or_none()

        if not crop:
            return {"status": "no_active_crop"}

        today = datetime.now(timezone.utc).date()
        days_since_planting = (today - crop.planted_date).days if crop.planted_date else 0
        days_to_harvest = (
            (crop.expected_harvest_date - today).days
            if crop.expected_harvest_date
            else None
        )

        return {
            "crop": crop.crop_name,
            "planted_date": crop.planted_date.isoformat() if crop.planted_date else None,
            "days_since_planting": days_since_planting,
            "growth_stage": crop.growth_stage,
            "expected_harvest": crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None,
            "days_to_harvest": days_to_harvest,
            "status": crop.status,
        }

    async def _get_sensor_trends(
        self, s: AsyncSession, field_id: UUID, days: int = 7
    ) -> Dict[str, Any]:
        """Sensor aggregates over the last N days — trends and averages."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Aggregation query
        stmt = select(
            func.avg(SensorReading.soil_moisture).label("avg_moisture"),
            func.min(SensorReading.soil_moisture).label("min_moisture"),
            func.max(SensorReading.soil_moisture).label("max_moisture"),
            func.avg(SensorReading.soil_ph).label("avg_ph"),
            func.avg(SensorReading.air_temperature).label("avg_temp"),
            func.min(SensorReading.air_temperature).label("min_temp"),
            func.max(SensorReading.air_temperature).label("max_temp"),
            func.avg(SensorReading.humidity).label("avg_humidity"),
            func.avg(SensorReading.npk_nitrogen).label("avg_nitrogen"),
            func.avg(SensorReading.npk_phosphorus).label("avg_phosphorus"),
            func.avg(SensorReading.npk_potassium).label("avg_potassium"),
            func.sum(SensorReading.rainfall).label("total_rainfall"),
            func.count(SensorReading.id).label("reading_count"),
        ).where(
            SensorReading.field_id == field_id,
            SensorReading.reading_time >= cutoff,
        )

        result = await s.execute(stmt)
        row = result.first()

        if not row or row.reading_count == 0:
            return {"status": "no_data", "period_days": days}

        # Determine trend direction by comparing first-half avg vs second-half avg
        midpoint = datetime.now(timezone.utc) - timedelta(days=days / 2)
        moisture_trend = await self._calc_trend(s, field_id, "soil_moisture", cutoff, midpoint)

        return {
            "period_days": days,
            "reading_count": row.reading_count,
            "soil_moisture": {
                "avg": round(row.avg_moisture, 1) if row.avg_moisture else None,
                "min": round(row.min_moisture, 1) if row.min_moisture else None,
                "max": round(row.max_moisture, 1) if row.max_moisture else None,
                "trend": moisture_trend,
            },
            "air_temperature": {
                "avg": round(row.avg_temp, 1) if row.avg_temp else None,
                "min": round(row.min_temp, 1) if row.min_temp else None,
                "max": round(row.max_temp, 1) if row.max_temp else None,
            },
            "soil_ph": {"avg": round(row.avg_ph, 2) if row.avg_ph else None},
            "humidity": {"avg": round(row.avg_humidity, 1) if row.avg_humidity else None},
            "npk": {
                "nitrogen_avg": round(row.avg_nitrogen, 0) if row.avg_nitrogen else None,
                "phosphorus_avg": round(row.avg_phosphorus, 0) if row.avg_phosphorus else None,
                "potassium_avg": round(row.avg_potassium, 0) if row.avg_potassium else None,
            },
            "total_rainfall_mm": round(row.total_rainfall, 1) if row.total_rainfall else 0,
        }

    async def _calc_trend(
        self, s: AsyncSession, field_id: UUID,
        column_name: str, start: datetime, midpoint: datetime,
    ) -> str:
        """Compare first-half vs second-half average to determine trend."""
        col = getattr(SensorReading, column_name)

        # First half average
        stmt1 = select(func.avg(col)).where(
            SensorReading.field_id == field_id,
            SensorReading.reading_time >= start,
            SensorReading.reading_time < midpoint,
        )
        r1 = await s.execute(stmt1)
        avg1 = r1.scalar()

        # Second half average
        stmt2 = select(func.avg(col)).where(
            SensorReading.field_id == field_id,
            SensorReading.reading_time >= midpoint,
        )
        r2 = await s.execute(stmt2)
        avg2 = r2.scalar()

        if avg1 is None or avg2 is None:
            return "insufficient_data"
        diff = avg2 - avg1
        if abs(diff) < 2:
            return "stable"
        return "rising" if diff > 0 else "declining"

    async def _get_recent_weather(
        self, s: AsyncSession, field_id: UUID
    ) -> Dict[str, Any]:
        """Recent weather API data from cache."""
        # Get field location
        stmt_field = select(Field.location_name).where(Field.id == field_id)
        result = await s.execute(stmt_field)
        location = result.scalar_one_or_none() or "Delhi"

        # Get latest cached weather
        stmt = (
            select(ExternalApiCache)
            .where(
                ExternalApiCache.source == "openweather",
                ExternalApiCache.location == location,
            )
            .order_by(desc(ExternalApiCache.fetched_at))
            .limit(1)
        )
        result = await s.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            return {"status": "no_cached_weather"}

        payload = row.response_payload or {}
        return {
            "fetched_at": row.fetched_at.isoformat() if row.fetched_at else None,
            "location": location,
            "data_summary": {
                "temperature": payload.get("temperature") or payload.get("main", {}).get("temp"),
                "humidity": payload.get("humidity") or payload.get("main", {}).get("humidity"),
                "description": payload.get("description") or payload.get("weather", [{}])[0].get("description") if payload.get("weather") else None,
                "rain_probability": payload.get("rain_probability", payload.get("pop", 0)),
            },
        }

    async def _get_recent_market(self, s: AsyncSession) -> Dict[str, Any]:
        """Recent market price API data from cache."""
        stmt = (
            select(ExternalApiCache)
            .where(ExternalApiCache.source == "data_gov_in")
            .order_by(desc(ExternalApiCache.fetched_at))
            .limit(1)
        )
        result = await s.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            return {"status": "no_cached_market_data"}

        return {
            "fetched_at": row.fetched_at.isoformat() if row.fetched_at else None,
            "endpoint": row.endpoint,
            "has_data": bool(row.response_payload),
        }

    async def _get_past_recommendations(
        self, s: AsyncSession, field_id: UUID, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recent agent recommendations — the AI's past advice."""
        stmt = (
            select(AgentRecommendation)
            .where(AgentRecommendation.field_id == field_id)
            .order_by(desc(AgentRecommendation.created_at))
            .limit(limit)
        )
        result = await s.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "agent": r.agent_name,
                "type": r.recommendation_type,
                "text": r.recommendation_text,
                "priority": r.priority,
                "status": r.status,
                "source": r.llm_source,
                "date": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            }
            for r in rows
        ]

    async def _get_past_actions(
        self, s: AsyncSession, field_id: UUID, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recent farmer actions — what was actually done."""
        stmt = (
            select(ActionLog)
            .where(ActionLog.field_id == field_id)
            .order_by(desc(ActionLog.created_at))
            .limit(limit)
        )
        result = await s.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "action": r.action_type,
                "details": r.action_details,
                "tokens": r.green_tokens_earned,
                "date": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            }
            for r in rows
        ]

    async def _get_agent_memory_summary(
        self, s: AsyncSession, field_id: UUID, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recent agent memory logs — summaries of what agents computed."""
        stmt = (
            select(AgentMemoryLog)
            .where(AgentMemoryLog.field_id == field_id)
            .order_by(desc(AgentMemoryLog.created_at))
            .limit(limit)
        )
        result = await s.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "agent": r.agent_name,
                "action": r.action,
                "summary": r.summary,
                "date": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            }
            for r in rows
        ]

    # ── Field Resolution (shared with database.py) ─────────────────

    async def _resolve_field_id(self, s: AsyncSession, farm_id: str) -> Optional[UUID]:
        """Resolve legacy farm_id to field UUID."""
        if isinstance(farm_id, UUID):
            return farm_id
        try:
            return UUID(farm_id)
        except (ValueError, AttributeError):
            pass

        stmt = select(Farmer).where(Farmer.farmer_id == farm_id.upper())
        result = await s.execute(stmt)
        farmer = result.scalar_one_or_none()
        if not farmer:
            return None

        stmt2 = select(Field).where(Field.farmer_id == farmer.id).limit(1)
        result2 = await s.execute(stmt2)
        field = result2.scalar_one_or_none()
        return field.id if field else None


# ── Singleton instance ─────────────────────────────────────────────
context_builder = ContextBuilder()
