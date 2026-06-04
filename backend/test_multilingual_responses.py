"""
Test Voice Assistant - Marathi and Hindi Responses
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.voice_assistant_agent import VoiceAssistantAgent
from core.database import Database

def test_responses():
    """Test voice assistant responses in all languages"""
    
    db = Database()
    agent = VoiceAssistantAgent(db)
    
    print("=" * 80)
    print("🧪 TESTING VOICE ASSISTANT MULTILINGUAL RESPONSES")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        # English tests
        {
            "text": "What's the weather today?",
            "language": "en",
            "description": "English weather query"
        },
        {
            "text": "I installed solar pump",
            "language": "en",
            "description": "English eco-action"
        },
        
        # Hindi tests
        {
            "text": "मौसम कैसा है",
            "language": "hi",
            "description": "Hindi weather query"
        },
        {
            "text": "मैंने सौर पंप लगाया",
            "language": "hi",
            "description": "Hindi eco-action (solar pump)"
        },
        {
            "text": "पानी की जरूरत है क्या",
            "language": "hi",
            "description": "Hindi water/irrigation query"
        },
        {
            "text": "मिट्टी की जांच करो",
            "language": "hi",
            "description": "Hindi soil query"
        },
        {
            "text": "बाजार का भाव क्या है",
            "language": "hi",
            "description": "Hindi market price query"
        },
        
        # Marathi tests
        {
            "text": "आजचा हवा कसा आहे",
            "language": "mr",
            "description": "Marathi weather query"
        },
        {
            "text": "मी सौर पंप लावला",
            "language": "mr",
            "description": "Marathi eco-action (solar pump)"
        },
        {
            "text": "पाण्याची गरज आहे का",
            "language": "mr",
            "description": "Marathi water/irrigation query"
        },
        {
            "text": "मातीची तपासणी करा",
            "language": "mr",
            "description": "Marathi soil query"
        },
        {
            "text": "बाजार किंमत काय आहे",
            "language": "mr",
            "description": "Marathi market price query"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"📝 TEST {i}: {test['description']}")
        print(f"{'─' * 80}")
        print(f"📥 Input ({test['language'].upper()}): {test['text']}")
        
        # Process command
        result = agent.process_command(test['text'], test['language'])
        
        print(f"🎯 Intent: {result['intent']}")
        print(f"📤 Response: {result['response_text']}")
        
        if result.get('voice_summary'):
            print(f"🔊 Voice Summary: {result['voice_summary']}")
        
        if result.get('green_tokens_earned', 0) > 0:
            print(f"🪙 Tokens Earned: {result['green_tokens_earned']}")
        
        # Verify language consistency
        response = result['response_text']
        voice_summary = result.get('voice_summary', '')
        
        if test['language'] == 'hi':
            # Check for Hindi Devanagari characters
            has_hindi = any('\u0900' <= char <= '\u097F' for char in response + voice_summary)
            status = "✅ PASS" if has_hindi or 'Green Tokens' in response else "❌ FAIL"
            print(f"{status} - Hindi response check")
        
        elif test['language'] == 'mr':
            # Check for Marathi/Devanagari characters
            has_marathi = any('\u0900' <= char <= '\u097F' for char in response + voice_summary)
            status = "✅ PASS" if has_marathi or 'Green Tokens' in response else "❌ FAIL"
            print(f"{status} - Marathi response check")
        
        elif test['language'] == 'en':
            # Check for English
            has_english = response.replace(' ', '').replace('.', '').isascii()
            status = "✅ PASS" if has_english else "❌ FAIL"
            print(f"{status} - English response check")
    
    print(f"\n{'=' * 80}")
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY:")
    print("✅ Hindi responses should be in Devanagari script")
    print("✅ Marathi responses should be in Devanagari script")
    print("✅ English responses should be in Latin script")
    print("✅ All eco-actions should award tokens")
    print("✅ Voice summaries should match the language")

if __name__ == "__main__":
    try:
        test_responses()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
