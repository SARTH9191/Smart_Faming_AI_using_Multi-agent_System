"""
Register user via API call
Make sure backend is running first!
"""
import requests
import json

def register_user():
    print("=" * 60)
    print("Registering User via API")
    print("=" * 60)
    
    url = "http://localhost:8000/auth/register"
    
    user_data = {
        "farmer_id": "FARM001",
        "password": "secure123",
        "name": "Ravi Kumar",
        "email": "ravi@example.com",
        "phone": "+919876543210",
        "language": "en"
    }
    
    print("\n📡 Sending registration request to:", url)
    print("📝 User data:", json.dumps(user_data, indent=2))
    
    try:
        response = requests.post(url, json=user_data)
        result = response.json()
        
        print("\n" + "=" * 60)
        if result.get("success"):
            print("✅ SUCCESS!")
            print(f"   {result.get('message')}")
            print("\n🔑 Login Credentials:")
            print("   Username: FARM001")
            print("   Password: secure123")
            print("\n✨ You can now login on the frontend!")
        else:
            print("❌ FAILED!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            if "already exists" in result.get('error', ''):
                print("\n💡 User already exists! You can login with:")
                print("   Username: FARM001")
                print("   Password: secure123")
        
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("   Make sure backend is running at http://localhost:8000")
        print("\n   Run this command in another terminal:")
        print("   cd backend")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    register_user()
