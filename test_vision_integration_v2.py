import os
import json
import base64
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from agents.disease_detection_agent import DiseaseDetectionAgent
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

# Using a slightly larger (64x64) solid green PNG
# This one is verified to be valid
green_64x64_b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABGdBTUEAALGPC/xhBQAAADhlWElmTU0AKgAAAAgAAYdpAAQA"
    "AAABAAAAGgAAAAAAAqACAAQAAAABAAAAQKADAAQAAAABAAAAQAAAAAB6mU6uAAAAL0lEQVR4Ae3BAQ0AAADCoPdPbQ43oAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF4Mu6YAAfcyS9oAAAAASUVORK5CYII="
)

def test_integration():
    print("🚀 Starting Vision Integration Test (64x64 image)...")
    agent = DiseaseDetectionAgent()
    
    if not agent._groq_key:
        print("❌ FAILED: Groq API key not found in agent.")
        return

    full_uri = f"data:image/png;base64,{green_64x64_b64}"
    print(f"📡 Calling agent with sample image (URI length: {len(full_uri)})...")
    
    try:
        # We need to simulate the environment enough for the agent
        # The agent uses _load_groq_key internally, which we've confirmed works.
        
        result = agent.analyze_image_from_base64(full_uri, "wheat")
        
        print("\n✅ API Response Received:")
        print(json.dumps(result, indent=2))
        
        if result.get("method") == "Groq Llama-4-Scout Vision":
            print("\n✨ SUCCESS: Agent used Groq Vision successfully!")
        else:
            print(f"\n⚠️ WARNING: Agent used method '{result.get('method')}' instead of Groq Vision.")
            
    except Exception as e:
        print(f"\n❌ ERROR: Integration test failed with exception: {e}")

if __name__ == "__main__":
    test_integration()
