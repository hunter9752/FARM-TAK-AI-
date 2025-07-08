#!/usr/bin/env python3
"""
LLM + TTS Integrated System
Takes LLM farming advice and converts to natural Hindi speech
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
llm_dir = os.path.join(parent_dir, 'llm')
sys.path.append(llm_dir)

# Import LLM and TTS systems
try:
    from farmer_tts import FarmerTTS
except ImportError as e:
    print(f"❌ Could not import TTS module: {e}")
    sys.exit(1)


class LLMTTSIntegrated:
    """Integrated LLM + TTS system for farmers"""
    
    def __init__(self):
        """Initialize integrated system"""
        print("🌾 Initializing LLM + TTS Integrated System...")
        print("=" * 60)
        
        # Initialize TTS
        print("🔊 Setting up TTS system...")
        self.tts = FarmerTTS()
        
        # Initialize LLM (simple version)
        print("🤖 Setting up LLM system...")
        self.setup_llm()
        
        # Session tracking
        self.session_start = datetime.now()
        self.total_interactions = 0
        self.successful_responses = 0
        
        print("✅ Integrated system ready!")
    
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
        
        print("✅ Groq API key loaded")
    
    def load_env(self):
        """Load environment variables from llm/.env"""
        env_file = os.path.join(os.path.dirname(current_dir), 'llm', '.env')
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
        
        # Farmer-specific system prompt
        system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

आपकी विशेषताएं:
- बीज, खाद, कीटनाशक की सलाह
- फसल रोग की पहचान और इलाज  
- मंडी भाव और बिक्री की सलाह
- मौसम के अनुसार खेती की सलाह
- सरकारी योजनाओं की जानकारी

जवाब हमेशा:
- हिंदी में दें
- 3-4 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो
- व्यावहारिक और उपयोगी हो
- बोलने के लिए उपयुक्त हो (TTS के लिए)"""

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
                "max_tokens": 200,
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
    
    def process_farmer_query(self, user_query: str) -> dict:
        """Complete pipeline: Query → LLM → TTS"""
        print(f"\n🌾 Processing: {user_query}")
        
        start_time = time.time()
        
        # Step 1: Get LLM response
        print("🤖 Step 1: Getting LLM response...")
        llm_result = self.get_llm_response(user_query)
        
        if not llm_result["success"]:
            print(f"❌ LLM failed: {llm_result['response']}")
            return {
                "success": False,
                "user_query": user_query,
                "llm_result": llm_result,
                "tts_success": False,
                "total_time": time.time() - start_time
            }
        
        print(f"✅ LLM response received ({llm_result['response_time']:.2f}s)")
        
        # Step 2: Convert to speech
        print("🔊 Step 2: Converting to speech...")
        tts_start = time.time()
        
        tts_success = self.tts.speak_farming_response(
            llm_result["response"], 
            {"add_intro": True}
        )
        
        tts_time = time.time() - tts_start
        total_time = time.time() - start_time
        
        if tts_success:
            print(f"✅ Speech completed ({tts_time:.2f}s)")
        else:
            print(f"❌ Speech failed ({tts_time:.2f}s)")
        
        # Update statistics
        self.total_interactions += 1
        if llm_result["success"] and tts_success:
            self.successful_responses += 1
        
        return {
            "success": llm_result["success"] and tts_success,
            "user_query": user_query,
            "llm_result": llm_result,
            "tts_success": tts_success,
            "tts_time": tts_time,
            "total_time": total_time
        }
    
    def display_response(self, result: dict):
        """Display formatted response"""
        print("\n" + "🌾" * 40)
        print("🤖 Farmer Assistant Response:")
        print("🌾" * 40)
        
        if result["llm_result"]["success"]:
            print(f"💬 Text: {result['llm_result']['response']}")
        else:
            print(f"❌ LLM Error: {result['llm_result']['response']}")
        
        print("🌾" * 40)
        print(f"⏱️ LLM Time: {result['llm_result']['response_time']:.2f}s")
        
        if "tts_time" in result:
            print(f"🔊 TTS Time: {result['tts_time']:.2f}s")
        
        print(f"⚡ Total Time: {result['total_time']:.2f}s")
        print(f"🎯 Success: {'✅' if result['success'] else '❌'}")
        print("-" * 80)
    
    def run_interactive_system(self):
        """Run interactive LLM + TTS system"""
        print("\n🌾 LLM + TTS Farmer Assistant")
        print("=" * 60)
        print("💡 Type your farming questions in Hindi or English")
        print("💡 You will hear the response as speech!")
        print("💡 Type 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎤 आपका सवाल: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर', 'बंद']:
                    print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                    break
                
                if not user_input:
                    print("⚠️ कृपया अपना सवाल लिखें।")
                    continue
                
                # Process query through complete pipeline
                result = self.process_farmer_query(user_input)
                
                # Display response
                self.display_response(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 सिस्टम बंद कर रहे हैं...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        # Show session summary
        self.show_session_summary()
    
    def show_session_summary(self):
        """Show session summary"""
        session_duration = datetime.now() - self.session_start
        
        print("\n📊 Session Summary:")
        print("=" * 50)
        print(f"⏱️ Duration: {session_duration}")
        print(f"💬 Total Queries: {self.total_interactions}")
        print(f"✅ Successful: {self.successful_responses}")
        
        if self.total_interactions > 0:
            success_rate = (self.successful_responses / self.total_interactions) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # TTS summary
        tts_summary = self.tts.get_session_summary()
        print(f"🔊 TTS Engine: {tts_summary['current_engine']}")
        print(f"🔊 TTS Success Rate: {tts_summary['success_rate']:.1f}%")


def main():
    """Main function"""
    try:
        # Initialize integrated system
        system = LLMTTSIntegrated()
        
        # Run interactive system
        system.run_interactive_system()
        
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ System startup failed: {e}")


if __name__ == "__main__":
    main()
