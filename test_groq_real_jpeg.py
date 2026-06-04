import os
import base64
import io
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv("GROQ_API_KEY")

# Generate a small red 100x100 JPEG
img = Image.new('RGB', (100, 100), color=(255, 0, 0))
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
                    {"type": "text", "text": "What is the color of the square in this image?"},
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
    )
    print("Real JPEG Success:")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Real JPEG Failed: {e}")
