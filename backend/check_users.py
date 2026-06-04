import asyncio
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from core.database import AsyncDatabase
from core.auth_system import Farmer
from sqlalchemy import select

async def check_users():
    db_url = os.getenv("DATABASE_URL")
    print(f"Checking DB: {db_url}")
    db = AsyncDatabase(db_url)
    async with db.session_factory() as session:
        stmt = select(Farmer)
        result = await session.execute(stmt)
        farmers = result.scalars().all()
        if not farmers:
            print("No farmers found.")
        for f in farmers:
            print(f"ID: {f.farmer_id}, Name: {f.name}, Email: {f.email}")

if __name__ == "__main__":
    asyncio.run(check_users())
