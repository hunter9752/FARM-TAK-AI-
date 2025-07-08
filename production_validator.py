#!/usr/bin/env python3
"""
Production System Validator
Validates all components before production deployment
"""

import os
import sys
import subprocess
import time
from datetime import datetime


class ProductionValidator:
    """Validates complete farmer assistant system"""
    
    def __init__(self):
        """Initialize validator"""
        self.validation_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def validate_component(self, component_name, test_function):
        """Validate a system component"""
        print(f"\n🧪 Testing {component_name}...")
        self.total_tests += 1
        
        try:
            result = test_function()
            if result:
                print(f"✅ {component_name}: PASSED")
                self.passed_tests += 1
                self.validation_results[component_name] = "PASSED"
            else:
                print(f"❌ {component_name}: FAILED")
                self.validation_results[component_name] = "FAILED"
        except Exception as e:
            print(f"❌ {component_name}: ERROR - {e}")
            self.validation_results[component_name] = f"ERROR: {e}"
    
    def test_stt_system(self):
        """Test STT system"""
        try:
            # Check if STT files exist
            stt_files = [
                "stt vosk model/improved_stt.py",
                "stt vosk model/test_audio.py"
            ]
            
            for file in stt_files:
                if not os.path.exists(file):
                    print(f"  Missing: {file}")
                    return False
            
            print("  ✅ STT files present")
            
            # Test audio system
            result = subprocess.run([
                sys.executable, "-c", 
                "import sounddevice; import vosk; print('STT dependencies OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✅ STT dependencies available")
                return True
            else:
                print(f"  ❌ STT dependencies missing: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ STT test error: {e}")
            return False
    
    def test_nlp_system(self):
        """Test NLP system"""
        try:
            # Check NLP files
            nlp_files = [
                "nlp/csv_based_intent_detector.py",
                "nlp/farmer_intents_dataset.csv"
            ]
            
            for file in nlp_files:
                if not os.path.exists(file):
                    print(f"  Missing: {file}")
                    return False
            
            print("  ✅ NLP files present")
            
            # Test NLP import
            sys.path.append("nlp")
            from csv_based_intent_detector import CSVBasedFarmerIntentDetector
            
            nlp = CSVBasedFarmerIntentDetector()
            result = nlp.detect_intent("गेहूं के लिए खाद की सलाह")
            
            if result["confidence"] > 0.5:
                print(f"  ✅ NLP working (confidence: {result['confidence']:.2f})")
                return True
            else:
                print(f"  ❌ NLP low confidence: {result['confidence']:.2f}")
                return False
                
        except Exception as e:
            print(f"  ❌ NLP test error: {e}")
            return False
    
    def test_llm_system(self):
        """Test LLM system"""
        try:
            # Check LLM files
            llm_files = [
                "llm/cloud_llm_assistant.py",
                "llm/.env"
            ]
            
            for file in llm_files:
                if not os.path.exists(file):
                    print(f"  Missing: {file}")
                    return False
            
            print("  ✅ LLM files present")
            
            # Load API key
            with open("llm/.env", "r") as f:
                for line in f:
                    if "GROQ_API_KEY=" in line and "=" in line:
                        key = line.split("=", 1)[1].strip()
                        if key and key != "your_api_key_here":
                            print("  ✅ API key configured")
                            
                            # Test API call
                            import requests
                            headers = {
                                "Authorization": f"Bearer {key}",
                                "Content-Type": "application/json"
                            }
                            
                            payload = {
                                "model": "llama3-70b-8192",
                                "messages": [{"role": "user", "content": "test"}],
                                "max_tokens": 10
                            }
                            
                            response = requests.post(
                                "https://api.groq.com/openai/v1/chat/completions",
                                json=payload, headers=headers, timeout=10
                            )
                            
                            if response.status_code == 200:
                                print("  ✅ LLM API working")
                                return True
                            else:
                                print(f"  ❌ LLM API error: {response.status_code}")
                                return False
            
            print("  ❌ No valid API key found")
            return False
            
        except Exception as e:
            print(f"  ❌ LLM test error: {e}")
            return False
    
    def test_tts_system(self):
        """Test TTS system"""
        try:
            # Check TTS files
            tts_files = [
                "tts model/farmer_tts.py",
                "tts model/working_llm_tts.py"
            ]
            
            for file in tts_files:
                if not os.path.exists(file):
                    print(f"  Missing: {file}")
                    return False
            
            print("  ✅ TTS files present")
            
            # Test TTS dependencies
            result = subprocess.run([
                sys.executable, "-c", 
                "import pyttsx3; import gtts; import pygame; print('TTS dependencies OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✅ TTS dependencies available")
                return True
            else:
                print(f"  ❌ TTS dependencies missing: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ TTS test error: {e}")
            return False
    
    def test_system_integration(self):
        """Test system integration"""
        try:
            # Test if all components can work together
            integration_files = [
                "llm/complete_cloud_farmer_assistant.py",
                "tts model/complete_voice_assistant.py"
            ]
            
            for file in integration_files:
                if not os.path.exists(file):
                    print(f"  Missing: {file}")
                    return False
            
            print("  ✅ Integration files present")
            print("  ✅ Complete pipeline available")
            return True
            
        except Exception as e:
            print(f"  ❌ Integration test error: {e}")
            return False
    
    def run_validation(self):
        """Run complete system validation"""
        print("🚀 Production System Validation")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        
        # Validate each component
        self.validate_component("STT System", self.test_stt_system)
        self.validate_component("NLP System", self.test_nlp_system)
        self.validate_component("LLM System", self.test_llm_system)
        self.validate_component("TTS System", self.test_tts_system)
        self.validate_component("System Integration", self.test_system_integration)
        
        # Show results
        print("\n📊 Validation Results:")
        print("=" * 60)
        
        for component, result in self.validation_results.items():
            status = "✅" if result == "PASSED" else "❌"
            print(f"{status} {component}: {result}")
        
        success_rate = (self.passed_tests / self.total_tests) * 100
        print(f"\n📈 Overall Success Rate: {success_rate:.1f}%")
        print(f"✅ Passed: {self.passed_tests}/{self.total_tests}")
        
        if success_rate >= 80:
            print("\n🎉 SYSTEM READY FOR PRODUCTION!")
            return True
        else:
            print("\n⚠️ SYSTEM NEEDS FIXES BEFORE PRODUCTION")
            return False


def main():
    """Main validation function"""
    validator = ProductionValidator()
    is_ready = validator.run_validation()
    
    if is_ready:
        print("\n🚀 Proceeding with production deployment...")
    else:
        print("\n🛑 Please fix issues before production deployment")
    
    return is_ready


if __name__ == "__main__":
    main()
