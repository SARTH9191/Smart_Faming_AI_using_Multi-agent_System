import asyncio
import os
from sqlalchemy import select
from core.database import AsyncDatabase, Admin
from config import DATABASE_URL

async def check():
    db = AsyncDatabase(DATABASE_URL)
    async with db.session_factory() as session:
        stmt = select(Admin)
        result = await session.execute(stmt)
        admins = result.scalars().all()
        for idx, a in enumerate(admins):
            print(f"[{idx}] ID: {a.id}, Username: {a.username}, Role: {a.role}, Active: {a.is_active}")
        if not admins:
            print("No admin users found.")

if __name__ == "__main__":
    asyncio.run(check())
