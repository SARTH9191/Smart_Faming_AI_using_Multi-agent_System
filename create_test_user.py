"""
Quick script to create test user FARM001
Run this before trying to login
"""
import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_path))

from core.database import AsyncDatabase
from core.auth_system import AuthSystem
from config import DATABASE_URL

async def create_test_user():
    print("=" * 60)
    print("Creating Test User for Smart Farming AI")
    print("=" * 60)
    
    # Initialize components
    db = AsyncDatabase(DATABASE_URL)
    await db.init_db()
    auth = AuthSystem(db)
    
    # Create test user data
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

    print(f"\n📝 Registering user: {user_data['email']}...")
    try:
        result = await auth.register_farmer(user_data)
        
        if result["status"] == "success":
            print("✅ SUCCESS!")
            print(f"   Farmer ID: {result['farmer_id']}")
            print("\n🔑 Login Credentials:")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print("\n✨ You can now login on the frontend!")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if "already registered" in str(e).lower():
            print("\n💡 User already exists! Try logging in with:")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(create_test_user())
