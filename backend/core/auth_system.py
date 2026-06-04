import os
import asyncio
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Float,
    Integer,
    Date,
    select,
    update,
    Text,
)
from .database import Base, AsyncDatabase
from config import DATABASE_URL

# ── Farmer Model ──────────────────────────────────────────────────


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    farmer_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Metadata
    location: Mapped[str] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    farm_size: Mapped[float] = mapped_column(Float, nullable=True)  # In hectares
    language: Mapped[str] = mapped_column(String(10), default="en")

    sowed_land_area_acres: Mapped[float] = mapped_column(Float, nullable=True)
    total_land_area_acres: Mapped[float] = mapped_column(Float, nullable=True)
    number_of_crops: Mapped[int] = mapped_column(Integer, nullable=True)
    crops_names: Mapped[str] = mapped_column(Text, nullable=True)
    sowing_date: Mapped[date] = mapped_column(Date, nullable=True)

    # Enhanced AI Context Fields
    soil_type: Mapped[str] = mapped_column(String(100), nullable=True)
    irrigation_source: Mapped[str] = mapped_column(String(100), nullable=True)
    is_organic: Mapped[bool] = mapped_column(Boolean, default=False)


# ── Auth System Class ───────────────────────────────────────────


class AuthSystem:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def register_farmer(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new farmer"""
        async with self.db.session_factory() as session:
            # Normalize and provide defaults expected by current frontend
            farmer_id = (farmer_data.get("farmer_id") or f"F_{int(datetime.utcnow().timestamp())}").upper()
            email = farmer_data.get("email") or f"{farmer_id.lower()}@farm.local"
            phone = farmer_data.get("phone") or "0000000000"

            # Check if farmer_id exists
            stmt = select(Farmer).where(Farmer.farmer_id == farmer_id)
            result = await session.execute(stmt)
            if result.scalars().first():
                raise Exception("Farmer ID already registered")

            # Check if email exists
            stmt = select(Farmer).where(Farmer.email == email)
            result = await session.execute(stmt)
            if result.scalars().first():
                raise Exception("Email already registered")

            import hashlib
            hashed_pw = hashlib.sha256(farmer_data["password"].encode()).hexdigest()

            new_farmer = Farmer(
                farmer_id=farmer_id,
                name=farmer_data["name"],
                email=email,
                phone=phone,
                password_hash=hashed_pw,
                location=farmer_data.get("location"),
                latitude=farmer_data.get("latitude"),
                longitude=farmer_data.get("longitude"),
                farm_size=farmer_data.get("farm_size"),
                language=farmer_data.get("language", "en"),
                soil_type=farmer_data.get("soil_type"),
                irrigation_source=farmer_data.get("irrigation_source"),
                is_organic=farmer_data.get("is_organic", False),
            )
            session.add(new_farmer)
            await session.commit()
            return {
                "status": "success",
                "farmer_id": new_farmer.farmer_id,
                "name": new_farmer.name,
            }

    async def login_farmer(self, identifier: str, password: str) -> Dict[str, Any]:
        """Verify login credentials (email or farmer_id)"""
        import hashlib

        async with self.db.session_factory() as session:
            # Check by email or farmer_id (case-insensitive)
            from sqlalchemy import or_, func

            stmt = select(Farmer).where(
                or_(
                    func.lower(Farmer.email) == identifier.lower(),
                    func.lower(Farmer.farmer_id) == identifier.lower(),
                )
            )
            result = await session.execute(stmt)
            farmer = result.scalars().first()

            if not farmer:
                return {"status": "failed", "message": "Invalid email/ID or password"}

            # Hash the input password and compare
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if farmer.password_hash != password_hash:
                return {"status": "failed", "message": "Invalid email/ID or password"}

            return {
                "status": "success",
                "farmer_id": farmer.farmer_id,
                "name": farmer.name,
                "email": farmer.email,
            }

    async def get_farmer_profile(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Get farmer details"""
        async with self.db.session_factory() as session:
            stmt = select(Farmer).where(Farmer.farmer_id == farmer_id)
            result = await session.execute(stmt)
            farmer = result.scalars().first()
            if not farmer:
                return None
            return {
                "farmer_id": farmer.farmer_id,
                "name": farmer.name,
                "email": farmer.email,
                "phone": farmer.phone,
                "language": farmer.language,
                "location": farmer.location,
                "latitude": farmer.latitude,
                "longitude": farmer.longitude,
                "total_land_area_acres": farmer.total_land_area_acres,
                "number_of_crops": farmer.number_of_crops,
                "crops_names": farmer.crops_names,
                "sowing_date": farmer.sowing_date.isoformat()
                if farmer.sowing_date
                else None,
                "sowed_land_area_acres": farmer.sowed_land_area_acres,
                "soil_type": farmer.soil_type,
                "irrigation_source": farmer.irrigation_source,
                "is_organic": farmer.is_organic,
            }

    async def update_farm_details(
        self, farmer_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update farm details"""
        async with self.db.session_factory() as session:
            stmt = select(Farmer).where(Farmer.farmer_id == farmer_id)
            result = await session.execute(stmt)
            farmer = result.scalars().first()
            if not farmer:
                return None

            if data.get("total_land_area_acres") is not None:
                farmer.total_land_area_acres = data["total_land_area_acres"]
            if data.get("number_of_crops") is not None:
                farmer.number_of_crops = data["number_of_crops"]
            if data.get("crops_names") is not None:
                farmer.crops_names = data["crops_names"]
            if data.get("sowing_date") is not None:
                try:
                    farmer.sowing_date = datetime.strptime(
                        data["sowing_date"], "%Y-%m-%d"
                    ).date()
                except:
                    pass
            if data.get("sowed_land_area_acres") is not None:
                farmer.sowed_land_area_acres = data["sowed_land_area_acres"]

            await session.commit()

            return {
                "farmer_id": farmer.farmer_id,
                "total_land_area_acres": farmer.total_land_area_acres,
                "number_of_crops": farmer.number_of_crops,
                "crops_names": farmer.crops_names,
                "sowing_date": farmer.sowing_date.isoformat()
                if farmer.sowing_date
                else None,
                "sowed_land_area_acres": farmer.sowed_land_area_acres,
            }

    async def update_basic_profile(
        self, farmer_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update basic profile - name, phone, email"""
        async with self.db.session_factory() as session:
            stmt = select(Farmer).where(Farmer.farmer_id == farmer_id)
            result = await session.execute(stmt)
            farmer = result.scalars().first()
            if not farmer:
                return None

            if data.get("name") is not None:
                farmer.name = data["name"]
            if data.get("phone") is not None:
                farmer.phone = data["phone"]
            if data.get("email") is not None:
                farmer.email = data["email"]
            if data.get("location") is not None:
                farmer.location = data["location"]
            if data.get("soil_type") is not None:
                farmer.soil_type = data["soil_type"]
            if data.get("irrigation_source") is not None:
                farmer.irrigation_source = data["irrigation_source"]
            if data.get("is_organic") is not None:
                farmer.is_organic = data["is_organic"]
            if data.get("latitude") is not None:
                farmer.latitude = data["latitude"]
            if data.get("longitude") is not None:
                farmer.longitude = data["longitude"]

            await session.commit()

            return {
                "farmer_id": farmer.farmer_id,
                "name": farmer.name,
                "phone": farmer.phone,
                "email": farmer.email,
                "location": farmer.location,
                "soil_type": farmer.soil_type,
                "irrigation_source": farmer.irrigation_source,
                "is_organic": farmer.is_organic,
                "latitude": farmer.latitude,
                "longitude": farmer.longitude,
            }
