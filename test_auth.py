"""
Test Authentication System
Run this to verify registration and login work correctly
"""
import sys
sys.path.append('backend')

from core.auth_system import AuthenticationSystem

# Initialize auth system
auth = AuthenticationSystem()

print("=" * 60)
print("TESTING AUTHENTICATION SYSTEM")
print("=" * 60)

# Test 1: Register a new user
print("\n1. Testing User Registration...")
result = auth.register_user(
    farmer_id="TEST001",
    password="test123456",
    name="Test Farmer",
    email="test@farm.com",
    phone="+919876543210",
    language="en"
)
print(f"   Result: {result}")

# Test 2: Try to register same user again (should fail)
print("\n2. Testing Duplicate Registration (should fail)...")
result = auth.register_user(
    farmer_id="TEST001",
    password="different",
    name="Another User",
    language="en"
)
print(f"   Result: {result}")

# Test 3: Login with correct credentials
print("\n3. Testing Login with Correct Credentials...")
result = auth.login_user(
    farmer_id="TEST001",
    password="test123456"
)
if result["success"]:
    print(f"   ✓ Login successful!")
    print(f"   Session ID: {result['session_id'][:20]}...")
    print(f"   User: {result['user']['name']}")
else:
    print(f"   ✗ Login failed: {result['error']}")

# Test 4: Login with wrong password (should fail)
print("\n4. Testing Login with Wrong Password (should fail)...")
result = auth.login_user(
    farmer_id="TEST001",
    password="wrongpassword"
)
print(f"   Result: {result}")

# Test 5: Login with non-existent user (should fail)
print("\n5. Testing Login with Non-existent User (should fail)...")
result = auth.login_user(
    farmer_id="NOTEXIST",
    password="anypassword"
)
print(f"   Result: {result}")

# Test 6: List all users
print("\n6. Listing All Registered Users...")
result = auth.get_all_users()
if result["success"]:
    print(f"   Total users: {result['count']}")
    for user in result['users']:
        print(f"   - {user['farmer_id']}: {user['name']} ({user['language']})")
else:
    print(f"   Error: {result['error']}")

print("\n" + "=" * 60)
print("TESTS COMPLETED!")
print("=" * 60)
print("\nIf all tests passed, your authentication system is working!")
print("Now start the backend server: cd backend && python -m uvicorn main:app --reload")
