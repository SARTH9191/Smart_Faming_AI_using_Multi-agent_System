"""
Quick script to create test user FARM001
Run this before trying to login
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.auth_system import AuthenticationSystem
import asyncio

def create_test_user_sync():
    asyncio.run(create_test_user())

async def create_test_user():
    print("=" * 60)
    print("Creating Test User for Smart Farming AI")
    print("=" * 60)
    
    # Initialize authentication system
    auth = AuthenticationSystem()
    
    # Create test user
    print("\n≡ƒô¥ Registering user: FARM001...")
    result = await auth.register_user(
        farmer_id="FARM001",
        password="secure123",
        name="Ravi Kumar",
        email="ravi@example.com",
        phone="+919876543210",
        language="en"
    )
    
    if result["success"]:
        print("Γ£à SUCCESS!")
        print(f"   {result['message']}")
        print("\n≡ƒöæ Login Credentials:")
        print("   Username: FARM001")
        print("   Password: secure123")
        print("\nΓ£¿ You can now login on the frontend!")
    else:
        print("Γ¥î FAILED!")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        
        if "already exists" in result.get('error', ''):
            print("\n≡ƒÆí User already exists! Try logging in with:")
            print("   Username: FARM001")
            print("   Password: secure123")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    create_test_user_sync()
