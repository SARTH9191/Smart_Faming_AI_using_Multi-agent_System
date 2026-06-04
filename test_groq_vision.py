import os
import json
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    cfg_path = os.path.join(os.getcwd(), 'backend', 'api_config.json')
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            api_key = json.load(f).get("groq_api_key")

if not api_key:
    print("No Groq API Key found.")
    exit(1)

client = Groq(api_key=api_key)
# meta-llama/llama-4-scout-17b-16e-instruct

# Create a tiny dummy image (1x1 transparent pixel) B64
dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

try:
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what you see in this image briefly."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{dummy_image}",
                        },
                    },
                ],
            }
        ],
        temperature=0,
        max_tokens=100
    )
    print("Vision Call Successful:")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Vision Call Failed: {e}")
