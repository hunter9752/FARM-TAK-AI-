#!/usr/bin/env python3
"""
Complete Voice Assistant: STT → NLP → LLM → TTS
Full voice-to-voice farmer assistant pipeline
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add all module paths
stt_dir = os.path.join(parent_dir, 'stt vosk model')
nlp_dir = os.path.join(parent_dir, 'nlp')
llm_dir = os.path.join(parent_dir, 'llm')

sys.path.append(stt_dir)
sys.path.append(nlm_dir)
sys.path.append(llm_dir)

# Import all systems
try:
    from farmer_tts import FarmerTTS
    print("✅ TTS module imported")
except ImportError as e:
    print(f"❌ Could not import TTS module: {e}")
    sys.exit(1)


class CompleteVoiceAssistant:
    """Complete voice-to-voice farmer assistant"""
    
    def __init__(self):
        """Initialize complete voice system"""
        print("🎤 Initializing Complete Voice Assistant...")
        print("🎤 → 🧠 → 🤖 → 🔊 (Speech → NLP → LLM → Speech)")
        print("=" * 70)
        
        # Initialize components
        self.initialize_components()
        
        # Session tracking
        self.session_start = datetime.now()
        self.total_interactions = 0
        self.successful_responses = 0
        
        # Processing state
        self.is_processing = False
        
        print("✅ Complete voice system ready!")
    
    def initialize_components(self):
        """Initialize all system components"""
        
        # 1. Initialize TTS
        print("🔊 Initializing TTS system...")
        self.tts = FarmerTTS()
        if not self.tts.current_engine:
            print("❌ TTS initialization failed!")
            sys.exit(1)
        print("✅ TTS system ready")
        
        # 2. Initialize LLM (simple version)
        print("🤖 Initializing LLM system...")
        self.setup_llm()
        print("✅ LLM system ready")
        
        # 3. STT will be initialized when needed
        self.stt = None
        print("⏳ STT will be initialized on demand")
    
    def setup_llm(self):
        """Setup LLM system"""
        # Load environment variables
        self.load_env()
        
        # Check API key
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print("❌ No Groq API key found!")
            print("💡 Please add GROQ_API_KEY to .env file in llm folder")
            sys.exit(1)
    
    def load_env(self):
        """Load environment variables from llm/.env"""
        env_file = os.path.join(parent_dir, 'llm', '.env')
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
    
    def get_llm_response(self, user_query: str) -> dict:
        """Get response from LLM"""
        import requests
        
        # Enhanced farmer-specific system prompt for voice
        system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

आपकी विशेषताएं:
- बीज, खाद, कीटनाशक की सलाह
- फसल रोग की पहचान और इलाज  
- मंडी भाव और बिक्री की सलाह
- मौसम के अनुसार खेती की सलाह
- सरकारी योजनाओं की जानकारी

जवाब हमेशा:
- हिंदी में दें
- 2-3 वाक्यों में संक्षिप्त हो (voice के लिए)
- तुरंत लागू होने वाला हो
- व्यावहारिक और उपयोगी हो
- बोलने के लिए उपयुक्त हो (TTS के लिए)
- सरल शब्दों में हो"""

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
                    {"role": "user", "content": user_query}
                ],
                "temperature": 0.7,
                "max_tokens": 150,  # Shorter for voice
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
                    "response_time": response_time,
                    "provider": "groq"
                }
            else:
                return {
                    "success": False,
                    "response": f"API Error: {response.status_code}",
                    "response_time": response_time,
                    "provider": "groq"
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "response_time": 0,
                "provider": "groq"
            }
    
    def process_voice_query(self, transcribed_text: str) -> dict:
        """Complete voice pipeline: Text → LLM → TTS"""
        if not transcribed_text or len(transcribed_text.strip()) < 3:
            return {"success": False, "reason": "Empty or too short text"}
        
        if self.is_processing:
            return {"success": False, "reason": "Already processing"}
        
        self.is_processing = True
        start_time = time.time()
        
        try:
            print(f"\n🎤 Voice Input: {transcribed_text}")
            print("🔄 Processing through voice pipeline...")
            
            # Step 1: Get LLM response
            print("  🤖 Step 1: Getting intelligent response...")
            llm_result = self.get_llm_response(transcribed_text)
            
            if not llm_result["success"]:
                print(f"  ❌ LLM failed: {llm_result['response']}")
                return {
                    "success": False,
                    "user_query": transcribed_text,
                    "llm_result": llm_result,
                    "tts_success": False,
                    "total_time": time.time() - start_time
                }
            
            print(f"  ✅ LLM response received ({llm_result['response_time']:.2f}s)")
            
            # Step 2: Convert to speech
            print("  🔊 Step 2: Converting to voice...")
            tts_start = time.time()
            
            # Speak with intro
            intro_text = "किसान सहायक का जवाब: " + llm_result["response"]
            tts_success = self.tts.speak_text(intro_text)
            
            tts_time = time.time() - tts_start
            total_time = time.time() - start_time
            
            if tts_success:
                print(f"  ✅ Voice response completed ({tts_time:.2f}s)")
            else:
                print(f"  ❌ Voice response failed ({tts_time:.2f}s)")
            
            # Update statistics
            self.total_interactions += 1
            if llm_result["success"] and tts_success:
                self.successful_responses += 1
            
            # Display results
            self.display_voice_response(transcribed_text, llm_result, tts_success, total_time)
            
            return {
                "success": llm_result["success"] and tts_success,
                "user_query": transcribed_text,
                "llm_result": llm_result,
                "tts_success": tts_success,
                "tts_time": tts_time,
                "total_time": total_time
            }
            
        except Exception as e:
            print(f"❌ Voice pipeline error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.is_processing = False
    
    def display_voice_response(self, query: str, llm_result: dict, tts_success: bool, total_time: float):
        """Display formatted voice response"""
        print("\n" + "🎤" * 35)
        print("🔊 Voice Assistant Response:")
        print("🎤" * 35)
        
        if llm_result["success"]:
            print(f"💬 Response: {llm_result['response']}")
        else:
            print(f"❌ Error: {llm_result['response']}")
        
        print("🎤" * 35)
        print(f"⏱️ LLM Time: {llm_result['response_time']:.2f}s")
        print(f"🔊 Voice Output: {'✅ Spoken' if tts_success else '❌ Failed'}")
        print(f"⚡ Total Time: {total_time:.2f}s")
        print("-" * 70)
        print("🎤 Ready for next voice input...")
    
    def run_text_mode(self):
        """Run in text input mode (for testing without STT)"""
        print("\n🎤 Voice Assistant - Text Input Mode")
        print("=" * 60)
        print("💡 Type your farming questions")
        print("💡 You will hear the response as speech!")
        print("💡 Type 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n📝 Type your question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर', 'बंद']:
                    print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                    break
                
                if not user_input:
                    print("⚠️ Please enter your question.")
                    continue
                
                # Process through voice pipeline
                result = self.process_voice_query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down voice assistant...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        # Show session summary
        self.show_session_summary()
    
    def show_session_summary(self):
        """Show session summary"""
        session_duration = datetime.now() - self.session_start
        
        print("\n📊 Voice Assistant Session Summary:")
        print("=" * 60)
        print(f"⏱️ Duration: {session_duration}")
        print(f"💬 Total Interactions: {self.total_interactions}")
        print(f"✅ Successful: {self.successful_responses}")
        
        if self.total_interactions > 0:
            success_rate = (self.successful_responses / self.total_interactions) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # TTS summary
        tts_summary = self.tts.get_session_summary()
        print(f"🔊 TTS Engine: {tts_summary['current_engine']}")
        print(f"🔊 TTS Success Rate: {tts_summary['success_rate']:.1f}%")
        
        print("\n🎉 Voice-to-Voice Farmer Assistant Session Complete!")


def main():
    """Main function"""
    try:
        # Initialize complete voice system
        assistant = CompleteVoiceAssistant()
        
        # For now, run in text mode (can be extended to full voice later)
        assistant.run_text_mode()
        
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ Voice assistant startup failed: {e}")


if __name__ == "__main__":
    main()
