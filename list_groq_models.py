import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load .env from backend and root
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    # Try looking in backend/api_config.json
    cfg_path = os.path.join(os.getcwd(), 'backend', 'api_config.json')
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            api_key = json.load(f).get("groq_api_key")

if not api_key:
    print("No Groq API Key found.")
    exit(1)

client = Groq(api_key=api_key)
try:
    models = client.models.list()
    print("Available Models:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error fetching models: {e}")
