#!/usr/bin/env python3
"""
🌾 FARMER ASSISTANT - PRODUCTION LAUNCHER
Complete Voice-Enabled AI Assistant for Farmers

Usage: python FARMER_ASSISTANT.py
"""

import os
import sys
import time
import subprocess
from datetime import datetime


class FarmerAssistantLauncher:
    """Production launcher for farmer assistant"""
    
    def __init__(self):
        """Initialize launcher"""
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.session_start = datetime.now()
        
    def display_welcome(self):
        """Display welcome screen"""
        print("🌾" * 80)
        print("🌾" + " " * 78 + "🌾")
        print("🌾" + " " * 25 + "FARMER ASSISTANT" + " " * 25 + "🌾")
        print("🌾" + " " * 20 + "AI-Powered Farming Guidance" + " " * 20 + "🌾")
        print("🌾" + " " * 78 + "🌾")
        print("🌾" * 80)
        
        print("\n🎯 Complete AI Pipeline:")
        print("🎤 Speech Input → 🧠 Intent Detection → 🤖 LLM Response → 🔊 Voice Output")
        
        print("\n✅ System Features:")
        print("  • 🎤 Hindi/English Speech Recognition (85-95% accuracy)")
        print("  • 🧠 Smart Intent Detection (94.4% accuracy)")
        print("  • 🤖 Cloud LLM Responses (Groq/OpenAI/Gemini)")
        print("  • 🔊 Natural Hindi Voice Output")
        print("  • 🌾 48+ Farming Topics Covered")
        
        print("\n🌟 Ready to Help with:")
        print("  • बीज और खाद की सलाह")
        print("  • फसल रोग और कीट नियंत्रण")
        print("  • मंडी भाव और बिक्री सलाह")
        print("  • मौसम आधारित खेती")
        print("  • सरकारी योजनाएं")
        
        print("🌾" * 80)
    
    def show_system_options(self):
        """Show available system options"""
        print("\n🚀 Choose Your Farmer Assistant Mode:")
        print("=" * 60)
        
        print("1. 🎤 Complete Voice Assistant (RECOMMENDED)")
        print("   • Full speech-to-speech interaction")
        print("   • Speak your questions, hear responses")
        print("   • Best for hands-free farming guidance")
        
        print("\n2. 💬 Text + Voice Assistant")
        print("   • Type questions, hear voice responses")
        print("   • Good for quiet environments")
        print("   • Fast and reliable")
        
        print("\n3. 📝 Text-Only Assistant")
        print("   • Type questions, read text responses")
        print("   • Works without microphone/speakers")
        print("   • Fastest response time")
        
        print("\n4. 🧪 System Testing")
        print("   • Test individual components")
        print("   • Verify system health")
        print("   • Troubleshooting mode")
        
        print("\n5. 📚 Help & Documentation")
        print("   • Setup guides and tutorials")
        print("   • System requirements")
        print("   • Troubleshooting tips")
        
        print("\n0. 🚪 Exit")
        print("=" * 60)
    
    def launch_complete_voice_assistant(self):
        """Launch complete voice assistant"""
        print("\n🎤 Launching Complete Voice Assistant...")
        print("🔄 Starting STT → NLP → LLM → TTS pipeline...")
        
        try:
            # Try to launch complete system
            script_path = os.path.join(self.current_dir, "tts model", "complete_voice_assistant.py")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                # Fallback to LLM + TTS
                script_path = os.path.join(self.current_dir, "tts model", "working_llm_tts.py")
                if os.path.exists(script_path):
                    print("🔄 Launching LLM + TTS system...")
                    subprocess.run([sys.executable, script_path])
                else:
                    print("❌ Voice assistant not found!")
                    
        except Exception as e:
            print(f"❌ Failed to launch voice assistant: {e}")
    
    def launch_text_voice_assistant(self):
        """Launch text + voice assistant"""
        print("\n💬 Launching Text + Voice Assistant...")
        
        try:
            script_path = os.path.join(self.current_dir, "tts model", "working_llm_tts.py")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("❌ Text + Voice assistant not found!")
                
        except Exception as e:
            print(f"❌ Failed to launch text + voice assistant: {e}")
    
    def launch_text_only_assistant(self):
        """Launch text-only assistant"""
        print("\n📝 Launching Text-Only Assistant...")
        
        try:
            script_path = os.path.join(self.current_dir, "llm", "simple_cloud_farmer.py")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("❌ Text-only assistant not found!")
                
        except Exception as e:
            print(f"❌ Failed to launch text-only assistant: {e}")
    
    def run_system_tests(self):
        """Run system tests"""
        print("\n🧪 Running System Tests...")
        
        try:
            script_path = os.path.join(self.current_dir, "production_validator.py")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("❌ System validator not found!")
                
        except Exception as e:
            print(f"❌ Failed to run system tests: {e}")
    
    def show_help_documentation(self):
        """Show help and documentation"""
        print("\n📚 Help & Documentation")
        print("=" * 50)
        
        print("🔧 Setup Guides:")
        print("  • STT Setup: stt vosk model/README.md")
        print("  • NLP Setup: nlp/README.md")
        print("  • LLM Setup: llm/CLOUD_LLM_SETUP.md")
        print("  • TTS Setup: tts model/TTS_SETUP.md")
        
        print("\n📖 Quick Start Guides:")
        print("  • Overall: PROJECT_OVERVIEW.md")
        print("  • Complete System: FINAL_SYSTEM_SUMMARY.md")
        print("  • LLM Quick Start: llm/QUICK_START.md")
        
        print("\n🆘 Troubleshooting:")
        print("  • Check API keys in llm/.env")
        print("  • Verify microphone permissions")
        print("  • Test internet connection")
        print("  • Run system validator")
        
        print("\n💡 System Requirements:")
        print("  • Python 3.8+")
        print("  • Internet connection (for cloud LLM)")
        print("  • Microphone (for voice input)")
        print("  • Speakers (for voice output)")
        print("  • 4GB+ RAM recommended")
        
        input("\nPress Enter to continue...")
    
    def run_production_launcher(self):
        """Run the production launcher"""
        try:
            while True:
                # Clear screen (Windows)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Show welcome
                self.display_welcome()
                
                # Show options
                self.show_system_options()
                
                # Get user choice
                try:
                    choice = input("\n🎯 Select option (1-5, 0 to exit): ").strip()
                    
                    if choice == "1":
                        self.launch_complete_voice_assistant()
                    elif choice == "2":
                        self.launch_text_voice_assistant()
                    elif choice == "3":
                        self.launch_text_only_assistant()
                    elif choice == "4":
                        self.run_system_tests()
                    elif choice == "5":
                        self.show_help_documentation()
                    elif choice == "0":
                        print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                        break
                    else:
                        print("\n⚠️ Invalid option. Please select 1-5 or 0.")
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Shutting down farmer assistant...")
                    break
                    
                # Pause before returning to menu
                if choice in ["1", "2", "3", "4"]:
                    input("\nPress Enter to return to main menu...")
                    
        except Exception as e:
            print(f"❌ Launcher error: {e}")
    
    def show_session_summary(self):
        """Show session summary"""
        session_duration = datetime.now() - self.session_start
        
        print(f"\n📊 Session Summary:")
        print(f"⏱️ Duration: {session_duration}")
        print(f"🌾 Farmer Assistant Session Complete")


def main():
    """Main production launcher"""
    try:
        launcher = FarmerAssistantLauncher()
        launcher.run_production_launcher()
        launcher.show_session_summary()
        
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ Production launcher failed: {e}")


if __name__ == "__main__":
    main()
