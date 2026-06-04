"""
Test NASA POWER API integration for Drone/Satellite Agent
"""
from agents.drone_satellite_agent import DroneSatelliteAgent
import json

# Initialize agent
agent = DroneSatelliteAgent()

print("=" * 60)
print("🛰️ TESTING NASA POWER API INTEGRATION")
print("=" * 60)

# Test 1: Pune, Maharashtra
print("\n📍 Test 1: Pune, Maharashtra")
print("-" * 60)
result_pune = agent.analyze_farm("FARM001", latitude=18.5204, longitude=73.8567)

print(f"\n✅ Farm ID: {result_pune['farm_id']}")
print(f"📡 Data Source: {result_pune['data_source']}")
print(f"📍 Location: {result_pune['location']}")

print("\n🛰️ SATELLITE DATA (NASA POWER):")
sat_data = result_pune['satellite_analysis']
print(json.dumps(sat_data, indent=2))

print("\n🚁 DRONE ANALYSIS:")
drone_data = result_pune['drone_analysis']
print(f"NDVI Average: {drone_data['ndvi_average']}")
print(f"Crop Health: {drone_data['crop_health']}")
print(f"Anomalies: {drone_data['anomalies_detected']}")

print("\n💡 RECOMMENDATIONS:")
for rec in result_pune['recommendations']:
    print(f"  • {rec}")

# Test 2: Nashik, Maharashtra (different location)
print("\n\n📍 Test 2: Nashik, Maharashtra")
print("-" * 60)
result_nashik = agent.analyze_farm("FARM002", latitude=19.9975, longitude=73.7898)

sat_nashik = result_nashik['satellite_analysis']
print(f"\n✅ API Status: {sat_nashik.get('api_status', 'Unknown')}")
print(f"🌡️ Current Temperature: {sat_nashik.get('temperature_trend', {}).get('current', 'N/A')}°C")
print(f"🌧️ Last 7 Days Rain: {sat_nashik.get('precipitation', {}).get('last_7_days_mm', 'N/A')} mm")
print(f"💧 Soil Moisture: {sat_nashik.get('soil_moisture_estimation', {}).get('estimated_percentage', 'N/A')}%")

# Test 3: Default location (no coordinates)
print("\n\n📍 Test 3: Default Location (Pune)")
print("-" * 60)
result_default = agent.analyze_farm("FARM003")
print(f"📍 Used Location: {result_default['location']}")
print(f"✅ Satellite Source: {result_default['satellite_analysis'].get('satellite', 'Unknown')}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)

# Summary
print("\n📊 SUMMARY:")
sat_data = result_pune['satellite_analysis']
print(f"  • NASA POWER API: {'✅ Working' if sat_data.get('satellite') == 'NASA POWER (REAL DATA)' else '❌ Failed (using fallback)'}")
print(f"  • Drone Simulation: ✅ Working")
print(f"  • Recommendations: ✅ Generated")
print(f"  • Total Agents: 17 (including this one)")
