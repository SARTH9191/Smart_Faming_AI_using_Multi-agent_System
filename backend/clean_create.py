import asyncio
import os
import sys

# we are already in backend, so current directory has core
from core.database import AsyncDatabase
from core.auth_system import AuthSystem, Farmer
from sqlalchemy import delete
from config import DATABASE_URL

async def main():
    db = AsyncDatabase(DATABASE_URL)
    async with db.session_factory() as s:
        await s.execute(delete(Farmer).where(Farmer.farmer_id == "FARM001"))
        await s.commit()

    auth = AuthSystem(db)
    user_data = {
        "farmer_id": "FARM001",
        "name": "Ravi Kumar",
        "email": "ravi@example.com",
        "phone": "+919876543210",
        "password": "secure123",
        "location": "Pune, Maharashtra, India",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "farm_size": 12.5,
        "language": "en"
    }

    try:
        result = await auth.register_farmer(user_data)
        print("✅ SUCCESS!", result)
    except Exception as e:
        print("❌ ERROR:", e)

asyncio.run(main())
