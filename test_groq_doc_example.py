import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv("GROQ_API_KEY")

# Create a 64x64 green square
green_64x64_b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABGdBTUEAALGPC/xhBQAAADhlWElmTU0AKgAAAAgAAYdpAAQA"
    "AAABAAAAGgAAAAAAAqACAAQAAAABAAAAQKADAAQAAAABAAAAQAAAAAB6mU6uAAAAL0lEQVR4Ae3BAQ0AAADCoPdPbQ43oAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF4Mu6YAAfcyS9oAAAAASUVORK5CYII="
)

client = Groq(api_key=api_key)

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{green_64x64_b64}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    print("Direct Doc Example Success:")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Direct Doc Example Failed: {e}")
