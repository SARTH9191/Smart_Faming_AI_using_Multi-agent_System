import requests
import json

print("=" * 60)
print("🧪 TESTING PUNE WEATHER")
print("=" * 60)

try:
    response = requests.get("http://localhost:8000/get_weather?location=Pune", timeout=10)
    data = response.json()
    
    print(f"\n📍 Location: {data.get('location', 'Unknown')}")
    print(f"🌡️ Backend Temperature: {data.get('current', {}).get('temperature', 'N/A')}°C")
    print(f"🌡️ Feels Like: {data.get('current', {}).get('feels_like', 'N/A')}°C")
    print(f"💧 Humidity: {data.get('current', {}).get('humidity', 'N/A')}%")
    print(f"📊 Data Source: {data.get('data_source', 'Unknown')}")
    print(f"🕐 Timestamp: {data.get('timestamp', 'Unknown')}")
    
    if 'coordinates' in data:
        print(f"📍 Coordinates: {data['coordinates']['lat']:.2f}°N, {data['coordinates']['lon']:.2f}°E")
    
    print("\n" + "=" * 60)
    print("⚠️ IMPORTANT:")
    print("- Backend returns LIVE data from OpenWeather/Open-Meteo")
    print("- Google shows retail weather (may differ slightly)")
    print("- Temperature can vary by:")
    print("  * Time of API call")
    print("  * Weather station location")
    print("  * Update frequency")
    print("=" * 60)
    
    print("\nFull API Response:")
    print(json.dumps(data, indent=2))
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
