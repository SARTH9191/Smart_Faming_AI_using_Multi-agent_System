import requests
import json

tests = [
    ("Soil health EN", {"text": "How is my soil health today?", "language": "en", "farm_id": "FARM001"}),
    ("Off-topic block", {"text": "Tell me a joke about cricket", "language": "en", "farm_id": "FARM001"}),
    ("Hindi question", {"text": "मेरी मिट्टी की नमी कितनी है?", "language": "hi", "farm_id": "FARM001"}),
]

results = {}
for name, body in tests:
    try:
        r = requests.post("http://localhost:8000/voice_command", json=body, timeout=20)
        d = r.json()
        results[name] = {
            "llm_used": d.get("llm_used"),
            "language": d.get("language"),
            "detected_language": d.get("detected_language"),
            "response": d.get("voice_summary") or d.get("response_text", ""),
        }
    except Exception as e:
        results[name] = {"error": str(e)}

with open("voice_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Done - results written to voice_test_results.json")
