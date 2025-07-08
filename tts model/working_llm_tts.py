#!/usr/bin/env python3
"""
Working LLM + TTS System
Direct imports and simple implementation
"""

import os
import sys
import time
import tempfile
from datetime import datetime

# Direct imports
import pyttsx3
from gtts import gTTS
import pygame
import requests


class WorkingLLMTTS:
    """Working LLM + TTS system"""
    
    def __init__(self):
        """Initialize system"""
        print("🌾 Working LLM + TTS System")
        print("=" * 50)
        
        # Load API key
        self.load_env()
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print("❌ No Groq API key found!")
            sys.exit(1)
        print("✅ Groq API key loaded")
        
        # Initialize TTS engines
        self.init_tts()
        print("✅ System ready!")
    
    def load_env(self):
        """Load .env from llm folder"""
        env_file = os.path.join('..', 'llm', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
    
    def init_tts(self):
        """Initialize TTS engines"""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty('rate', 150)
            self.pyttsx3_engine.setProperty('volume', 0.9)
            print("✅ pyttsx3 engine ready")
        except Exception as e:
            print(f"⚠️ pyttsx3 init failed: {e}")
            self.pyttsx3_engine = None
        
        try:
            # Test gTTS
            test_tts = gTTS(text="test", lang="hi")
            print("✅ gTTS engine ready")
            self.gtts_available = True
        except Exception as e:
            print(f"⚠️ gTTS init failed: {e}")
            self.gtts_available = False
    
    def get_llm_response(self, query):
        """Get LLM response"""
        system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

जवाब हमेशा:
- हिंदी में दें
- 2-3 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो
- बोलने के लिए उपयुक्त हो"""

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.7,
                "max_tokens": 150,
                "stream": False
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result["choices"][0]["message"]["content"].strip()
                return {
                    "success": True,
                    "response": llm_response,
                    "response_time": response_time
                }
            else:
                return {
                    "success": False,
                    "response": f"API Error: {response.status_code}",
                    "response_time": response_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "response_time": 0
            }
    
    def speak_with_pyttsx3(self, text):
        """Speak using pyttsx3"""
        if not self.pyttsx3_engine:
            return False
        
        try:
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ pyttsx3 speech failed: {e}")
            return False
    
    def speak_with_gtts(self, text):
        """Speak using gTTS"""
        if not self.gtts_available:
            return False
        
        try:
            tts = gTTS(text=text, lang="hi", slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_filename = tmp_file.name
                tts.save(temp_filename)
            
            pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.quit()
            
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ gTTS speech failed: {e}")
            return False
    
    def speak_text(self, text):
        """Speak text using best available engine"""
        print(f"🔊 Speaking: {text[:50]}...")
        
        # Try gTTS first (better Hindi)
        if self.gtts_available:
            if self.speak_with_gtts(text):
                return True
        
        # Fallback to pyttsx3
        if self.pyttsx3_engine:
            if self.speak_with_pyttsx3(text):
                return True
        
        print("❌ No TTS engine available")
        return False
    
    def process_query(self, query):
        """Complete LLM + TTS pipeline"""
        print(f"\n🌾 Processing: {query}")
        
        # Step 1: Get LLM response
        print("🤖 Getting LLM response...")
        llm_result = self.get_llm_response(query)
        
        if not llm_result["success"]:
            print(f"❌ LLM failed: {llm_result['response']}")
            return False
        
        print(f"✅ LLM response ({llm_result['response_time']:.2f}s)")
        
        # Step 2: Speak response
        print("🔊 Converting to speech...")
        intro_text = "किसान सहायक का जवाब: " + llm_result["response"]
        
        tts_start = time.time()
        tts_success = self.speak_text(intro_text)
        tts_time = time.time() - tts_start
        
        # Display results
        print("\n" + "🌾" * 30)
        print("🤖 Response:")
        print("🌾" * 30)
        print(f"💬 {llm_result['response']}")
        print("🌾" * 30)
        print(f"⏱️ LLM Time: {llm_result['response_time']:.2f}s")
        print(f"🔊 TTS Time: {tts_time:.2f}s")
        print(f"🎯 Success: {'✅' if tts_success else '❌'}")
        print("-" * 60)
        
        return tts_success
    
    def run_interactive(self):
        """Run interactive system"""
        print("\n💡 Type farming questions in Hindi or English")
        print("💡 You will hear responses as speech!")
        print("💡 Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🎤 आपका सवाल: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर']:
                    print("\n👋 धन्यवाद!")
                    break
                
                if not user_input:
                    print("⚠️ Please enter your question")
                    continue
                
                self.process_query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    try:
        system = WorkingLLMTTS()
        system.run_interactive()
    except Exception as e:
        print(f"❌ System failed: {e}")


if __name__ == "__main__":
    main()
