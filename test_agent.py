import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend.core.database import Database
from backend.agents.lead_agent import LeadAgent
import json

db = Database()
# ensure there's at least one sensor reading
from backend.core.sensor_simulator import SensorSimulator
sim = SensorSimulator()
sensor_data = sim.generate_sensor_data(farm_id="FARM001", duration_minutes=1)
db.store_sensor_data(sensor_data)

agent = LeadAgent(db)
result = agent.orchestrate_all_agents("FARM001")

print("--- GLOBAL RECOMMENDATIONS ---")
print(json.dumps(result.get("global_recommendations"), indent=2))
