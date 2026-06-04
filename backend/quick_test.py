import requests
import json

print("=" * 60)
print("🧪 TESTING BACKEND WEATHER API")
print("=" * 60)

try:
    # Test 1: Check if backend is running
    print("\n1. Checking if backend is online...")
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"✅ Backend is online: {response.json()['status']}")
    
    # Test 2: Get weather for Delhi
    print("\n2. Testing weather API for Delhi...")
    response = requests.get("http://localhost:8000/get_weather?location=Delhi", timeout=10)
    data = response.json()
    
    print(f"\n📍 Location: {data.get('location', 'Unknown')}")
    print(f"🌡️ Temperature: {data.get('current', {}).get('temperature', 'N/A')}°C")
    print(f"💧 Humidity: {data.get('current', {}).get('humidity', 'N/A')}%")
    print(f"📊 Data Source: {data.get('data_source', 'Unknown')}")
    
    if 'Open-Meteo' in data.get('data_source', ''):
        print("\n✅ Using Open-Meteo API (Free)")
    elif 'OpenWeather' in data.get('data_source', ''):
        print("\n✅ Using OpenWeather API (Premium)")
    else:
        print("\n⚠️ Unknown data source")
    
    print("\n" + "=" * 60)
    print("Full Response:")
    print(json.dumps(data, indent=2))
    
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Backend is NOT running!")
    print("\nTo start backend:")
    print("1. Open PowerShell in backend folder")
    print("2. Run: python main.py")
    print("3. Wait for 'Uvicorn running on http://0.0.0.0:8000'")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
