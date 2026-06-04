import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import delete
from core.database import AsyncDatabase
from core.auth_system import Farmer
from config import DATABASE_URL

async def main():
    db = AsyncDatabase(DATABASE_URL)
    async with db.session_factory() as s:
        await s.execute(delete(Farmer).where(Farmer.email == "ravi@example.com"))
        await s.commit()

asyncio.run(main())
