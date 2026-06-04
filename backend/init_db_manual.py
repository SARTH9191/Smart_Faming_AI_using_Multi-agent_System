import asyncio
import os
from dotenv import load_dotenv

# Load .env from root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from core.database import AsyncDatabase, Base
from config import API_CONFIG

async def init():
    print(f"Connecting to: {API_CONFIG['database_url']}")
    db = AsyncDatabase(API_CONFIG["database_url"])
    print("Initializing tables...")
    await db.init_db()
    
    # Create a default test user
    from core.auth_system import AuthSystem
    auth = AuthSystem(db)
    try:
        test_user = {
            "farmer_id": "FARM001",
            "name": "Agri Farmer",
            "email": "farmer@example.com",
            "phone": "1234567890",
            "password": "admin123",
            "location": "Pune",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "farm_size": 5.0,
            "soil_type": "Black Soil",
            "irrigation_source": "Well",
            "is_organic": True
        }
        await auth.register_farmer(test_user)
        print("Default test user created: FARM001 / admin123")
    except Exception as e:
        if "already registered" in str(e):
            print("Default test user already exists.")
        else:
            print(f"Error creating test user: {e}")
            
    print("DONE! Database ready.")

if __name__ == "__main__":
    asyncio.run(init())
