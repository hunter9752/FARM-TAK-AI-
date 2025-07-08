#!/usr/bin/env python3
"""
Integrated Farmer Assistant
Combines STT (Speech-to-Text) with NLP (Intent Detection)
"""

import sys
import os
import json
import time
from datetime import datetime

# Add parent directory to path to import STT modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'stt vosk model'))

try:
    from improved_stt import ImprovedSTT
except ImportError:
    print("❌ Could not import STT module. Please ensure 'stt vosk model' folder exists.")
    sys.exit(1)

from farmer_intent_detector import FarmerIntentDetector


class IntegratedFarmerAssistant:
    """Complete farmer assistant with speech recognition and intent detection"""
    
    def __init__(self):
        """Initialize the integrated system"""
        print("🌾 Initializing Farmer Assistant...")
        
        # Initialize STT system
        try:
            self.stt = ImprovedSTT()
            print("✅ Speech-to-Text system loaded")
        except Exception as e:
            print(f"❌ Failed to load STT system: {e}")
            sys.exit(1)
        
        # Initialize NLP system
        try:
            self.nlp = FarmerIntentDetector()
            print("✅ Intent detection system loaded")
        except Exception as e:
            print(f"❌ Failed to load NLP system: {e}")
            sys.exit(1)
        
        # Session tracking
        self.session_start = datetime.now()
        self.total_interactions = 0
        self.successful_intents = 0
        
        # Response database
        self.setup_response_database()
    
    def setup_response_database(self):
        """Setup detailed responses for farming intents"""
        self.detailed_responses = {
            "crop_planting": {
                "wheat": "गेहूं बोने का सही समय नवंबर-दिसंबर है। 100-120 किलो बीज प्रति हेक्टेयर चाहिए।",
                "rice": "धान की रोपाई जून-जुलाई में करें। पहले नर्सरी तैयार करें।",
                "corn": "मक्का की बुआई जून-जुलाई में करें। 20-25 किलो बीज प्रति हेक्टेयर।",
                "default": "फसल बोने से पहले मिट्टी की जांच कराएं और उचित बीज चुनें।"
            },
            
            "crop_disease": {
                "wheat": "गेहूं में रतुआ रोग हो सकता है। प्रोपिकोनाजोल का छिड़काव करें।",
                "rice": "धान में ब्लास्ट रोग के लिए ट्राइसाइक्लाजोल का प्रयोग करें।",
                "default": "तुरंत कृषि विशेषज्ञ से संपर्क करें। फोटो भेजकर सलाह लें।"
            },
            
            "market_price": {
                "wheat": "गेहूं का आज का भाव ₹2100-2200 प्रति क्विंटल है।",
                "rice": "धान का भाव ₹1800-1900 प्रति क्विंटल चल रहा है।",
                "default": "मंडी भाव के लिए eNAM पोर्टल देखें या स्थानीय मंडी से संपर्क करें।"
            },
            
            "fertilizer_advice": {
                "wheat": "गेहूं के लिए NPK 120:60:40 किलो प्रति हेक्टेयर दें।",
                "rice": "धान के लिए 150:75:75 NPK और जिंक सल्फेट दें।",
                "default": "मिट्टी परीक्षण के आधार पर संतुलित उर्वरक का प्रयोग करें।"
            },
            
            "irrigation_need": {
                "wheat": "गेहूं में 4-5 सिंचाई चाहिए। पहली सिंचाई 20-25 दिन बाद।",
                "rice": "धान में हमेशा 2-3 इंच पानी रखें।",
                "default": "मिट्टी की नमी देखकर सिंचाई करें। सुबह या शाम का समय बेहतर है।"
            },
            
            "government_scheme": {
                "default": "PM-KISAN, फसल बीमा योजना, KCC लोन उपलब्ध है। नजदीकी कृषि कार्यालय से संपर्क करें।"
            }
        }
    
    def get_detailed_response(self, intent_result):
        """Generate detailed farming advice based on intent and entities"""
        intent = intent_result["intent"]
        entities = intent_result["entities"]
        
        if intent == "unknown":
            return "मुझे आपकी बात समझ नहीं आई। कृपया स्पष्ट रूप से अपना सवाल पूछें।"
        
        # Get crop-specific response if crop is detected
        detected_crop = None
        if "crops" in entities and entities["crops"]:
            detected_crop = entities["crops"][0]
        
        # Get response from database
        if intent in self.detailed_responses:
            responses = self.detailed_responses[intent]
            if detected_crop and detected_crop in responses:
                response = responses[detected_crop]
            else:
                response = responses.get("default", "आपकी समस्या समझ गई है।")
        else:
            response = "इस विषय पर अधिक जानकारी के लिए कृषि विशेषज्ञ से संपर्क करें।"
        
        # Add confidence indicator
        confidence = intent_result["confidence"]
        if confidence < 0.7:
            response += "\n\n⚠️ कृपया अपना सवाल और स्पष्ट करें।"
        
        return response
    
    def display_welcome(self):
        """Display welcome message"""
        print("=" * 80)
        print("🌾 स्वागत है - किसान सहायक (Farmer Assistant)")
        print("🎤 बोलकर अपने खेती के सवाल पूछें")
        print("=" * 80)
        print("📋 मैं इन विषयों में मदद कर सकता हूं:")
        print("  • फसल बुआई और कटाई")
        print("  • रोग और कीट नियंत्रण") 
        print("  • मौसम और सिंचाई")
        print("  • बाजार भाव और बिक्री")
        print("  • खाद और बीज की सलाह")
        print("  • सरकारी योजनाएं")
        print("=" * 80)
    
    def process_speech_input(self, transcribed_text):
        """Process transcribed speech through NLP"""
        if not transcribed_text or len(transcribed_text.strip()) < 3:
            return None
        
        print(f"\n🎤 आपने कहा: {transcribed_text}")
        
        # Detect intent using NLP
        intent_result = self.nlp.detect_intent(transcribed_text)
        
        # Generate detailed response
        response = self.get_detailed_response(intent_result)
        
        # Display results
        print(f"\n🎯 समझा गया विषय: {intent_result['intent']}")
        print(f"📊 विश्वसनीयता: {intent_result['confidence']:.2f}")
        
        if intent_result['entities']:
            print(f"🏷️ पहचाने गए तत्व: {intent_result['entities']}")
        
        print(f"\n💬 सलाह:")
        print(f"   {response}")
        
        # Update session stats
        self.total_interactions += 1
        if intent_result['is_confident']:
            self.successful_intents += 1
        
        return intent_result
    
    def run_integrated_session(self):
        """Run the integrated STT + NLP session"""
        try:
            # Display welcome
            self.display_welcome()
            
            # Setup STT system
            if not self.stt.select_language():
                return
            
            if not self.stt.load_improved_model():
                return
            
            print("\n🎯 सिस्टम तैयार है! बोलना शुरू करें...")
            print("💡 स्पष्ट रूप से और धीरे-धीरे बोलें")
            print("🛑 रोकने के लिए Ctrl+C दबाएं")
            print("-" * 80)
            
            # Start STT with NLP integration
            self.stt.is_running = True
            
            # Modified audio processing for integration
            import threading
            audio_thread = threading.Thread(target=self.integrated_audio_processing, daemon=True)
            audio_thread.start()
            
            # Start audio stream
            import sounddevice as sd
            with sd.RawInputStream(
                samplerate=self.stt.sample_rate,
                blocksize=self.stt.block_size,
                device=None,
                dtype='float32',
                channels=1,
                callback=self.stt.audio_callback
            ):
                print(f"🎤 सुन रहा हूं... (Sample rate: {self.stt.sample_rate} Hz)")
                
                while self.stt.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 सिस्टम बंद कर रहे हैं...")
            self.stt.is_running = False
            self.show_session_summary()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stt.is_running = False
    
    def integrated_audio_processing(self):
        """Modified audio processing with NLP integration"""
        import queue
        import json
        import numpy as np
        
        last_partial = ""
        audio_count = 0
        
        while self.stt.is_running:
            try:
                # Get audio data from queue
                data = self.stt.audio_queue.get(timeout=1)
                audio_count += 1
                
                # Show audio activity (less frequent to avoid clutter)
                if audio_count % 10 == 0:
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))
                    
                    bar_length = 20
                    filled_length = int(bar_length * min(volume * 20, 1.0))
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    
                    if volume > 0.05:
                        status = "🟢"
                    elif volume > 0.02:
                        status = "🟡"
                    else:
                        status = "🔴"
                    
                    print(f"\r🎤 |{bar}| {status}", end='', flush=True)
                
                # Process with recognizer
                if self.stt.recognizer.AcceptWaveform(data):
                    # Final result - process with NLP
                    result = json.loads(self.stt.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text and len(text) > 2:
                        # Clear the audio bar
                        print("\r" + " " * 50 + "\r", end='')
                        
                        # Process through NLP
                        self.process_speech_input(text)
                        
                        print("\n" + "─" * 80)
                        print("🎤 अगला सवाल बोलें...")
                        
                        last_partial = ""
                else:
                    # Partial result (show less frequently)
                    partial = json.loads(self.stt.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != last_partial and len(partial_text) > 3:
                        print(f"\r🎤 सुन रहा हूं: {partial_text[:50]}...", end='', flush=True)
                        last_partial = partial_text
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Audio processing error: {e}")
    
    def show_session_summary(self):
        """Show session statistics"""
        session_duration = datetime.now() - self.session_start
        
        print("\n📊 सत्र की रिपोर्ट:")
        print("=" * 50)
        print(f"⏱️ कुल समय: {session_duration}")
        print(f"💬 कुल बातचीत: {self.total_interactions}")
        print(f"✅ सफल पहचान: {self.successful_intents}")
        
        if self.total_interactions > 0:
            success_rate = (self.successful_intents / self.total_interactions) * 100
            print(f"📈 सफलता दर: {success_rate:.1f}%")
        
        # Show NLP conversation summary
        nlp_summary = self.nlp.get_conversation_summary()
        if nlp_summary.get("total_interactions", 0) > 0:
            print(f"🎯 औसत विश्वसनीयता: {nlp_summary['average_confidence']:.2f}")
            print("📋 मुख्य विषय:")
            for intent, count in nlp_summary['intent_distribution'].items():
                print(f"   • {intent}: {count} बार")
        
        print("\n🙏 धन्यवाद! खेती में सफलता की शुभकामनाएं!")


def main():
    """Main function"""
    try:
        assistant = IntegratedFarmerAssistant()
        assistant.run_integrated_session()
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ System error: {e}")


if __name__ == "__main__":
    main()
