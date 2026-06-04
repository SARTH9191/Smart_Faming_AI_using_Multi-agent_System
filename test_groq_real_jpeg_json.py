import os
import base64
import io
import json
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv("GROQ_API_KEY")

img = Image.new('RGB', (100, 100), color=(0, 255, 0))
buf = io.BytesIO()
img.save(buf, format='JPEG')
jpeg_data = buf.getvalue()
base64_image = base64.b64encode(jpeg_data).decode('utf-8')

client = Groq(api_key=api_key)

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the image and return a JSON object with a field 'color'."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        response_format={"type": "json_object"}
    )
    print("JSON JPEG Success:")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"JSON JPEG Failed: {e}")
