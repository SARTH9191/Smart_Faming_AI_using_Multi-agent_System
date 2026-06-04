"""
Speech Recognition Agent
Converts spoken audio (Marathi/Hindi/English) to text using Google Speech Recognition
"""
import speech_recognition as sr
from typing import Dict, Any, Optional
import io
import base64

class SpeechRecognitionAgent:
    """
    Agent for converting speech to text in multiple languages
    Supports: English, Hindi, Marathi
    """
    
    def __init__(self):
        self.name = "Speech Recognition Agent"
        self.recognizer = sr.Recognizer()
        
        # Language codes for Google Speech Recognition
        self.language_codes = {
            "en": "en-US",      # English (US)
            "hi": "hi-IN",      # Hindi (India)
            "mr": "mr-IN"       # Marathi (India)
        }
        
        # Configure recognizer for better accuracy
        self.recognizer.energy_threshold = 4000  # Adjust based on ambient noise
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider end of speech
    
    def recognize_from_microphone(self, language: str = "en", duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Capture audio from microphone and convert to text
        
        Args:
            language (str): Language code (en/hi/mr)
            duration (int): Recording duration in seconds (None for auto-stop)
            
        Returns:
            Dict with recognized text and metadata
        """
        try:
            # Get language code
            lang_code = self.language_codes.get(language, "en-US")
            
            # Use microphone as audio source
            with sr.Microphone() as source:
                print(f"🎤 Listening in {language.upper()}... Speak now!")
                
                # Adjust for ambient noise
                print("⏳ Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                if duration:
                    audio = self.recognizer.record(source, duration=duration)
                else:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("🔄 Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language=lang_code)
                
                return {
                    "status": "success",
                    "text": text,
                    "language": language,
                    "language_code": lang_code,
                    "confidence": "high",
                    "agent": self.name
                }
                
        except sr.WaitTimeoutError:
            return {
                "status": "error",
                "error": "Listening timed out. No speech detected.",
                "text": "",
                "language": language
            }
        except sr.UnknownValueError:
            return {
                "status": "error",
                "error": "Could not understand audio. Please speak clearly.",
                "text": "",
                "language": language
            }
        except sr.RequestError as e:
            return {
                "status": "error",
                "error": f"Speech recognition service error: {str(e)}",
                "text": "",
                "language": language
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "text": "",
                "language": language
            }
    
    def recognize_from_audio_file(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Convert audio file to text
        
        Args:
            audio_file_path (str): Path to audio file (WAV format)
            language (str): Language code (en/hi/mr)
            
        Returns:
            Dict with recognized text and metadata
        """
        try:
            lang_code = self.language_codes.get(language, "en-US")
            
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                print(f"📂 Loading audio file: {audio_file_path}")
                audio = self.recognizer.record(source)
                
                print("🔄 Processing audio file...")
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio, language=lang_code)
                
                return {
                    "status": "success",
                    "text": text,
                    "language": language,
                    "language_code": lang_code,
                    "source": "audio_file",
                    "file_path": audio_file_path,
                    "agent": self.name
                }
                
        except sr.UnknownValueError:
            return {
                "status": "error",
                "error": "Could not understand audio from file.",
                "text": "",
                "language": language
            }
        except sr.RequestError as e:
            return {
                "status": "error",
                "error": f"Speech recognition service error: {str(e)}",
                "text": "",
                "language": language
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "error": f"Audio file not found: {audio_file_path}",
                "text": "",
                "language": language
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "text": "",
                "language": language
            }
    
    def recognize_from_audio_data(self, audio_base64: str, language: str = "en") -> Dict[str, Any]:
        """
        Convert base64 encoded audio to text (for web uploads)
        
        Args:
            audio_base64 (str): Base64 encoded audio data (WAV format)
            language (str): Language code (en/hi/mr)
            
        Returns:
            Dict with recognized text and metadata
        """
        try:
            lang_code = self.language_codes.get(language, "en-US")
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Convert to AudioData
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio = self.recognizer.record(source)
                
                print("🔄 Processing uploaded audio...")
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio, language=lang_code)
                
                return {
                    "status": "success",
                    "text": text,
                    "language": language,
                    "language_code": lang_code,
                    "source": "upload",
                    "agent": self.name
                }
                
        except sr.UnknownValueError:
            return {
                "status": "error",
                "error": "Could not understand the uploaded audio.",
                "text": "",
                "language": language
            }
        except sr.RequestError as e:
            return {
                "status": "error",
                "error": f"Speech recognition service error: {str(e)}",
                "text": "",
                "language": language
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "text": "",
                "language": language
            }
    
    def test_microphone(self) -> Dict[str, Any]:
        """
        Test if microphone is working
        
        Returns:
            Dict with microphone status
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone is working!")
                
                return {
                    "status": "success",
                    "message": "Microphone is working properly",
                    "available_microphones": sr.Microphone.list_microphone_names()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Microphone test failed: {str(e)}",
                "available_microphones": []
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages
        
        Returns:
            Dict of language codes and names
        """
        return {
            "en": "English (US)",
            "hi": "Hindi (India)",
            "mr": "Marathi (India)"
        }


# Example usage
if __name__ == "__main__":
    agent = SpeechRecognitionAgent()
    
    # Test microphone
    print("\n=== Testing Microphone ===")
    result = agent.test_microphone()
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        # Test English
        print("\n=== Test 1: English Speech Recognition ===")
        print("Say something in English...")
        result_en = agent.recognize_from_microphone("en")
        print(f"Recognized: {result_en.get('text', 'N/A')}")
        
        # Test Hindi
        print("\n=== Test 2: Hindi Speech Recognition ===")
        print("हिंदी में कुछ बोलें...")
        result_hi = agent.recognize_from_microphone("hi")
        print(f"Recognized: {result_hi.get('text', 'N/A')}")
        
        # Test Marathi
        print("\n=== Test 3: Marathi Speech Recognition ===")
        print("मराठीत काहीतरी बोला...")
        result_mr = agent.recognize_from_microphone("mr")
        print(f"Recognized: {result_mr.get('text', 'N/A')}")
