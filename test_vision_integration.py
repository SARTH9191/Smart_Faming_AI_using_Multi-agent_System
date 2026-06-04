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

# Create a 10x10 green square PNG in base64
# This is a valid PNG that represents a green surface (like a healthy leaf)
green_dot_b64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABGdBTUEAALGPC/xhBQAA"
    "ADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAAqACAAQAAAABAAAACqADAAQAAAABAAAACgAAAAB2"
    "S0nBAAAAEklEQVQYV2NgYGRgYGBgYDAAAAD8AAH4+f7TAAAAAElFTkSuQmCC"
)

def test_integration():
    print("🚀 Starting Vision Integration Test...")
    agent = DiseaseDetectionAgent()
    
    # Check if Groq key is loaded
    if not agent._groq_key:
        print("❌ FAILED: Groq API key not found in agent.")
        return

    print(f"📡 Calling agent with sample image (Method: {agent.name})...")
    
    try:
        result = agent.analyze_image_from_base64(green_dot_b64, "wheat")
        
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
