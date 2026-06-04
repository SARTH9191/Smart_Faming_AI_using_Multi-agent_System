import asyncio
import os
from sqlalchemy import select
from core.database import AsyncDatabase
from core.auth_system import Farmer
from config import DATABASE_URL

async def check():
    db = AsyncDatabase(DATABASE_URL)
    async with db.session_factory() as session:
        stmt = select(Farmer)
        result = await session.execute(stmt)
        farmers = result.scalars().all()
        for idx, f in enumerate(farmers):
            print(f"[{idx}] Farmer ID: {f.farmer_id}, Password: {f.password_hash}")
        if not farmers:
            print("No farmers found.")

if __name__ == "__main__":
    asyncio.run(check())
