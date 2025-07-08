#!/usr/bin/env python3
"""
Farmer TTS (Text-to-Speech) System
Converts LLM farming advice text to natural Hindi voice
"""

import os
import sys
import time
import threading
from datetime import datetime
import tempfile
import subprocess

# TTS Libraries
PYTTSX3_AVAILABLE = False
GTTS_AVAILABLE = False
REQUESTS_AVAILABLE = False

try:
    import pyttsx3  # Offline TTS
    PYTTSX3_AVAILABLE = True
    print("✅ pyttsx3 imported successfully")
except ImportError as e:
    print(f"⚠️ pyttsx3 not available: {e}")

try:
    from gtts import gTTS  # Google TTS (online)
    import pygame  # For audio playback
    GTTS_AVAILABLE = True
    print("✅ gTTS and pygame imported successfully")
except ImportError as e:
    print(f"⚠️ gTTS/pygame not available: {e}")

try:
    import requests  # For API-based TTS
    REQUESTS_AVAILABLE = True
    print("✅ requests imported successfully")
except ImportError as e:
    print(f"⚠️ requests not available: {e}")


class FarmerTTS:
    """Advanced TTS system for farmer responses"""
    
    def __init__(self):
        """Initialize TTS system"""
        print("🔊 Initializing Farmer TTS System...")
        
        # Available TTS engines
        self.tts_engines = {}
        self.current_engine = None
        
        # Initialize available engines
        self.initialize_engines()
        
        # TTS settings
        self.voice_settings = {
            "rate": 150,        # Words per minute
            "volume": 0.9,      # Volume level (0.0 to 1.0)
            "language": "hi",   # Hindi language
            "gender": "female"  # Voice gender preference
        }
        
        # Session tracking
        self.session_start = datetime.now()
        self.total_speeches = 0
        self.successful_speeches = 0
    
    def initialize_engines(self):
        """Initialize available TTS engines"""
        
        # 1. Initialize pyttsx3 (Offline)
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                self.tts_engines["pyttsx3"] = {
                    "engine": engine,
                    "type": "offline",
                    "quality": "medium",
                    "speed": "fast",
                    "hindi_support": "basic"
                }
                print("✅ pyttsx3 engine initialized (Offline)")
            except Exception as e:
                print(f"⚠️ pyttsx3 initialization failed: {e}")
        
        # 2. Initialize Google TTS (Online)
        if GTTS_AVAILABLE:
            try:
                # Test gTTS
                test_tts = gTTS(text="test", lang="hi")
                self.tts_engines["gtts"] = {
                    "engine": "gtts",
                    "type": "online",
                    "quality": "high",
                    "speed": "medium",
                    "hindi_support": "excellent"
                }
                print("✅ Google TTS (gTTS) available (Online)")
            except Exception as e:
                print(f"⚠️ gTTS initialization failed: {e}")
        
        # 3. Windows SAPI (if available)
        if os.name == 'nt':  # Windows
            try:
                import win32com.client
                self.tts_engines["sapi"] = {
                    "engine": "sapi",
                    "type": "offline",
                    "quality": "medium",
                    "speed": "fast",
                    "hindi_support": "limited"
                }
                print("✅ Windows SAPI available (Offline)")
            except ImportError:
                print("⚠️ Windows SAPI not available (pywin32 not installed)")
        
        # Select best available engine
        self.select_best_engine()
    
    def select_best_engine(self):
        """Select the best available TTS engine"""
        if not self.tts_engines:
            print("❌ No TTS engines available!")
            return False
        
        # Priority order: gTTS (best Hindi) > pyttsx3 > SAPI
        priority_order = ["gtts", "pyttsx3", "sapi"]
        
        for engine_name in priority_order:
            if engine_name in self.tts_engines:
                self.current_engine = engine_name
                engine_info = self.tts_engines[engine_name]
                print(f"🎯 Selected TTS Engine: {engine_name}")
                print(f"   Type: {engine_info['type']}")
                print(f"   Quality: {engine_info['quality']}")
                print(f"   Hindi Support: {engine_info['hindi_support']}")
                return True
        
        return False
    
    def configure_pyttsx3(self):
        """Configure pyttsx3 engine for Hindi"""
        if "pyttsx3" not in self.tts_engines:
            return False
        
        try:
            engine = self.tts_engines["pyttsx3"]["engine"]
            
            # Set rate (speed)
            engine.setProperty('rate', self.voice_settings["rate"])
            
            # Set volume
            engine.setProperty('volume', self.voice_settings["volume"])
            
            # Try to find Hindi voice
            voices = engine.getProperty('voices')
            hindi_voice = None
            
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['hindi', 'india', 'zira', 'ravi']):
                    hindi_voice = voice
                    break
            
            if hindi_voice:
                engine.setProperty('voice', hindi_voice.id)
                print(f"✅ Hindi voice selected: {hindi_voice.name}")
            else:
                print("⚠️ No Hindi voice found, using default")
            
            return True
            
        except Exception as e:
            print(f"❌ pyttsx3 configuration failed: {e}")
            return False
    
    def speak_with_pyttsx3(self, text: str) -> bool:
        """Speak text using pyttsx3"""
        try:
            engine = self.tts_engines["pyttsx3"]["engine"]
            
            # Configure engine
            self.configure_pyttsx3()
            
            # Speak text
            engine.say(text)
            engine.runAndWait()
            
            return True
            
        except Exception as e:
            print(f"❌ pyttsx3 speech failed: {e}")
            return False
    
    def speak_with_gtts(self, text: str) -> bool:
        """Speak text using Google TTS"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang="hi", slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_filename = tmp_file.name
                tts.save(temp_filename)
            
            # Play audio using pygame
            if GTTS_AVAILABLE:
                pygame.mixer.init()
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
            
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ gTTS speech failed: {e}")
            return False
    
    def speak_with_sapi(self, text: str) -> bool:
        """Speak text using Windows SAPI"""
        try:
            import win32com.client
            
            # Create SAPI voice object
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Set rate and volume
            voice.Rate = 0  # Normal speed
            voice.Volume = 90  # 90% volume
            
            # Speak text
            voice.Speak(text)
            
            return True
            
        except Exception as e:
            print(f"❌ SAPI speech failed: {e}")
            return False
    
    def speak_text(self, text: str) -> bool:
        """Main function to convert text to speech"""
        if not text or not text.strip():
            print("⚠️ Empty text provided")
            return False
        
        if not self.current_engine:
            print("❌ No TTS engine available")
            return False
        
        print(f"🔊 Speaking with {self.current_engine}: {text[:50]}...")
        
        start_time = time.time()
        success = False
        
        try:
            # Use selected engine
            if self.current_engine == "pyttsx3":
                success = self.speak_with_pyttsx3(text)
            elif self.current_engine == "gtts":
                success = self.speak_with_gtts(text)
            elif self.current_engine == "sapi":
                success = self.speak_with_sapi(text)
            
            speech_time = time.time() - start_time
            
            # Update statistics
            self.total_speeches += 1
            if success:
                self.successful_speeches += 1
                print(f"✅ Speech completed in {speech_time:.2f}s")
            else:
                print(f"❌ Speech failed after {speech_time:.2f}s")
            
            return success
            
        except Exception as e:
            print(f"❌ Speech error: {e}")
            return False
    
    def speak_farming_response(self, llm_response: str, metadata: dict = None) -> bool:
        """Speak LLM farming response with enhancements"""
        if not llm_response:
            return False
        
        # Clean text for better speech
        cleaned_text = self.clean_text_for_speech(llm_response)
        
        # Add intro if needed
        if metadata and metadata.get("add_intro", False):
            intro = "किसान सहायक का जवाब: "
            cleaned_text = intro + cleaned_text
        
        # Speak the text
        return self.speak_text(cleaned_text)
    
    def clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove special characters that might cause issues
        text = text.replace("💬", "")
        text = text.replace("✅", "")
        text = text.replace("❌", "")
        text = text.replace("🌾", "")
        text = text.replace("🎯", "")
        
        # Replace English words with Hindi equivalents for better pronunciation
        replacements = {
            "NPK": "एन पी के",
            "DAP": "डी ए पी",
            "kg": "किलो",
            "quintal": "क्विंटल",
            "acre": "एकड़",
            "hectare": "हेक्टेयर"
        }
        
        for eng, hindi in replacements.items():
            text = text.replace(eng, hindi)
        
        # Clean up extra spaces
        text = " ".join(text.split())
        
        return text
    
    def test_tts_system(self):
        """Test TTS system with sample farming text"""
        print("\n🧪 Testing TTS System")
        print("=" * 50)
        
        test_texts = [
            "नमस्कार किसान भाई",
            "गेहूं के लिए डी ए पी खाद का प्रयोग करें",
            "फसल में कीड़े लगने पर तुरंत दवाई का छिड़काव करें",
            "मंडी में आज गेहूं का भाव अच्छा है"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n🔊 Test {i}: {text}")
            success = self.speak_text(text)
            if success:
                print(f"✅ Test {i} passed")
            else:
                print(f"❌ Test {i} failed")
            
            time.sleep(1)  # Pause between tests
    
    def get_session_summary(self) -> dict:
        """Get TTS session summary"""
        session_duration = datetime.now() - self.session_start
        
        success_rate = 0
        if self.total_speeches > 0:
            success_rate = (self.successful_speeches / self.total_speeches) * 100
        
        return {
            "session_duration": str(session_duration),
            "total_speeches": self.total_speeches,
            "successful_speeches": self.successful_speeches,
            "success_rate": success_rate,
            "current_engine": self.current_engine,
            "available_engines": list(self.tts_engines.keys())
        }


def main():
    """Interactive TTS testing"""
    print("🔊 Farmer TTS System - Interactive Testing")
    print("=" * 60)
    
    try:
        # Initialize TTS
        tts = FarmerTTS()
        
        if not tts.current_engine:
            print("❌ No TTS engine available!")
            print("💡 Install dependencies:")
            print("   pip install pyttsx3 gtts pygame")
            return
        
        print("\n✅ TTS System Ready!")
        print("💡 Type farming text to convert to speech")
        print("💡 Type 'test' to run system tests")
        print("💡 Type 'quit' to exit")
        print("-" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n📝 Enter text: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर']:
                    print("\n👋 TTS system shutting down...")
                    break
                
                if user_input.lower() == 'test':
                    tts.test_tts_system()
                    continue
                
                if not user_input:
                    print("⚠️ Please enter some text")
                    continue
                
                # Convert to speech
                print("🔄 Converting to speech...")
                success = tts.speak_text(user_input)
                
                if not success:
                    print("❌ Speech conversion failed")
                
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        # Show session summary
        summary = tts.get_session_summary()
        print("\n📊 TTS Session Summary:")
        print(f"   Duration: {summary['session_duration']}")
        print(f"   Total Speeches: {summary['total_speeches']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Engine Used: {summary['current_engine']}")
        
    except Exception as e:
        print(f"❌ TTS system initialization failed: {e}")


if __name__ == "__main__":
    main()
