import asyncio
from core.database import AsyncDatabase
from agents.agrobrain_agent import AgroBrainAgent
# LeadAgent not needed for this numerical stability test

async def verify():
    db = AsyncDatabase("sqlite+aiosqlite:///d:/Agri AI/agri_ai/backend/agri_ai.db")
    # Clean/Reset for predictable test
    # Actually just insert 10 specific noisy readings
    farm_id = "STABILITY_TEST_001"
    
    # 1. Insert 10 readings with wild moisture swings (10% to 90%)
    # Average should be 50%
    readings = []
    for i in range(10):
        m = 10 if i % 2 == 0 else 90
        readings.append({
            "farm_id": farm_id,
            "soil_moisture": m,
            "soil_temperature": 25.0,
            "soil_ph": 7.0,
            "npk_nitrogen": 50.0,
            "npk_phosphorus": 30.0,
            "npk_potassium": 40.0,
            "humidity": 60.0,
            "air_temperature": 25.0
        })
    
    print(f"Injecting 10 noisy readings for {farm_id}...")
    await db.store_sensor_data(readings)
    
    # 2. Call AgroBrain Agent (Fallback mode is fine)
    agent = AgroBrainAgent(db, None) 
    dashboard = await agent.generate_os_dashboard(farm_id)
    
    moisture = dashboard["data"]["agent_data"]["soil_analysis"]["moisture"]
    score = dashboard["data"]["health_score"]["score"]
    
    print(f"--- RESULTS ---")
    print(f"Moisture used: {moisture} (Expected: ~50.0%)")
    print(f"Health Score: {score}")
    
    if "50.0" in str(moisture) or "50.00" in str(moisture):
        print("✅ SUCCESS: Stabilization / Moving Average is working.")
    else:
        print("❌ FAILURE: Stabilization not working as expected.")

if __name__ == "__main__":
    asyncio.run(verify())
