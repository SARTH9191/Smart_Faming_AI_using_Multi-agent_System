import asyncio
import hashlib
from sqlalchemy import select, update
from core.database import AsyncDatabase, Admin
from config import DATABASE_URL

async def reset():
    db = AsyncDatabase(DATABASE_URL)
    new_password = "admin123"
    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    async with db.session_factory() as session:
        stmt = update(Admin).where(Admin.username == "admin").values(password_hash=new_hash)
        await session.execute(stmt)
        await session.commit()
    print(f"Password for user 'admin' has been reset to: {new_password}")

if __name__ == "__main__":
    asyncio.run(reset())
