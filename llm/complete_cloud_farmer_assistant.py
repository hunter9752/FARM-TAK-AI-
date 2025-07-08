#!/usr/bin/env python3
"""
Complete Cloud Farmer Assistant: STT → NLP → Cloud LLM + Real-time Data
Real-time speech with internet-connected intelligent responses
"""

import sys
import os
import json
import time
import threading
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'stt vosk model'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nlp'))

try:
    from improved_stt import ImprovedSTT
    from csv_based_intent_detector import CSVBasedFarmerIntentDetector
    from cloud_llm_assistant import CloudLLMFarmerAssistant
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available.")
    sys.exit(1)


class CompleteCloudFarmerAssistant:
    """Complete pipeline: Speech → Text → Intent → Cloud LLM + Real-time Data"""
    
    def __init__(self):
        """Initialize the complete cloud system"""
        print("🌐 Initializing Complete Cloud Farmer Assistant...")
        print("=" * 70)
        
        # Initialize components
        self.initialize_components()
        
        # Session tracking
        self.session_start = datetime.now()
        self.total_interactions = 0
        self.successful_responses = 0
        
        # Audio processing state
        self.is_processing = False
        self.last_response_time = 0
    
    def initialize_components(self):
        """Initialize all system components"""
        
        # 1. Initialize STT
        print("🎤 Initializing Speech-to-Text...")
        try:
            self.stt = ImprovedSTT()
            print("✅ STT system ready")
        except Exception as e:
            print(f"❌ STT initialization failed: {e}")
            sys.exit(1)
        
        # 2. Initialize Cloud LLM (includes NLP)
        print("🌐 Initializing Cloud LLM with Real-time Data...")
        try:
            self.cloud_llm = CloudLLMFarmerAssistant()
            print("✅ Cloud LLM system ready")
        except Exception as e:
            print(f"❌ Cloud LLM initialization failed: {e}")
            print("💡 Make sure you have API keys configured")
            sys.exit(1)
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 90)
        print("🌐 स्वागत है - Complete Cloud Farmer Assistant")
        print("🎤 → 🧠 → 🌐 → 📊 (Speech → Intent → Cloud LLM → Real-time Data)")
        print("=" * 90)
        print("📋 सिस्टम की विशेषताएं:")
        print("  • 🎤 Real-time speech recognition (85-95% accuracy)")
        print("  • 🧠 94.4% accurate intent detection (30K samples)")
        print("  • 🌐 Cloud LLM responses (Groq/OpenAI/Gemini)")
        print("  • 📊 Real-time data integration (Weather/Market/News)")
        print("  • 🗣️ Hindi + English support")
        print("  • 🌾 48+ farming topics covered")
        print("=" * 90)
        
        # Show current LLM provider
        current_llm = self.cloud_llm.current_llm
        if current_llm:
            model = self.cloud_llm.llm_apis[current_llm]["model"]
            print(f"🤖 Current LLM: {current_llm} ({model})")
        
        # Show available data sources
        enabled_sources = [k for k, v in self.cloud_llm.data_sources.items() if v["enabled"]]
        if enabled_sources:
            print(f"📊 Real-time Data: {', '.join(enabled_sources)}")
        else:
            print("📊 Real-time Data: Not configured (optional)")
        
        print("=" * 90)
        print("💡 बोलकर अपने खेती के सवाल पूछें")
        print("🛑 रोकने के लिए Ctrl+C दबाएं")
        print("=" * 90)
    
    def process_complete_cloud_pipeline(self, transcribed_text: str):
        """Process through complete STT → NLP → Cloud LLM pipeline"""
        if not transcribed_text or len(transcribed_text.strip()) < 3:
            return
        
        if self.is_processing:
            return  # Avoid overlapping processing
        
        self.is_processing = True
        start_time = time.time()
        
        try:
            print(f"\n🎤 आपने कहा: {transcribed_text}")
            print("🔄 Processing through cloud pipeline...")
            
            # Process through cloud LLM (includes NLP)
            result = self.cloud_llm.process_farmer_query(transcribed_text)
            
            # Extract results
            nlp_result = result["nlp_result"]
            llm_response = result["llm_response"]
            llm_provider = result["llm_provider"]
            
            intent = nlp_result["intent"]
            confidence = nlp_result["confidence"]
            entities = nlp_result["entities"]
            
            # Display Results
            processing_time = time.time() - start_time
            self.display_complete_cloud_response(
                transcribed_text, nlp_result, llm_response, 
                llm_provider, processing_time
            )
            
            # Update statistics
            self.total_interactions += 1
            if confidence > 0.5:  # Consider successful if confidence > 0.5
                self.successful_responses += 1
            
            self.last_response_time = processing_time
            
        except Exception as e:
            print(f"❌ Cloud pipeline error: {e}")
            print("💡 Check your internet connection and API keys")
        finally:
            self.is_processing = False
    
    def display_complete_cloud_response(self, user_query: str, nlp_result: Dict, 
                                      llm_response: str, llm_provider: str, processing_time: float):
        """Display formatted complete cloud response"""
        print("\n" + "🌐" * 35)
        print("🤖 Cloud Farmer Assistant का जवाब:")
        print("🌐" * 35)
        print(f"💬 {llm_response}")
        print("🌐" * 35)
        
        # Technical details
        print(f"⏱️ Total Response Time: {processing_time:.2f}s")
        print(f"🌐 LLM Provider: {llm_provider}")
        print(f"📊 NLP Confidence: {nlp_result['confidence']:.2f}")
        print(f"🎯 Intent: {nlp_result['intent']}")
        if nlp_result['entities']:
            print(f"🏷️ Entities: {nlp_result['entities']}")
        
        # Show real-time data usage
        enabled_sources = [k for k, v in self.cloud_llm.data_sources.items() if v["enabled"]]
        if enabled_sources:
            print(f"📊 Real-time Data: {', '.join(enabled_sources)}")
        
        print("─" * 70)
        print("🎤 अगला सवाल बोलें...")
    
    def run_complete_cloud_system(self):
        """Run the complete cloud integrated system"""
        try:
            # Display welcome
            self.display_welcome()
            
            # Setup STT
            if not self.stt.select_language():
                return
            
            if not self.stt.load_improved_model():
                return
            
            print("\n🎯 Complete cloud system ready! Start speaking...")
            print("💡 Speak clearly and wait for intelligent response")
            print("-" * 80)
            
            # Start STT with Cloud LLM integration
            self.stt.is_running = True
            
            # Modified audio processing for cloud pipeline
            audio_thread = threading.Thread(target=self.cloud_audio_processing, daemon=True)
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
                print(f"🎤 Listening... (Sample rate: {self.stt.sample_rate} Hz)")
                
                while self.stt.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down cloud system...")
            self.stt.is_running = False
            self.show_session_summary()
            
        except Exception as e:
            print(f"❌ System error: {e}")
            self.stt.is_running = False
    
    def cloud_audio_processing(self):
        """Audio processing with cloud pipeline integration"""
        import queue
        import json
        import numpy as np
        
        last_partial = ""
        audio_count = 0
        
        while self.stt.is_running:
            try:
                # Get audio data
                data = self.stt.audio_queue.get(timeout=1)
                audio_count += 1
                
                # Show audio activity (less frequent for cloud processing)
                if audio_count % 20 == 0:  # Even less frequent for cloud
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))
                    
                    bar_length = 12
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
                    # Final result - process through cloud pipeline
                    result = json.loads(self.stt.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text and len(text) > 2:
                        # Clear the audio bar
                        print("\r" + " " * 30 + "\r", end='')
                        
                        # Process through complete cloud pipeline
                        self.process_complete_cloud_pipeline(text)
                        
                        last_partial = ""
                else:
                    # Partial result (show less frequently)
                    partial = json.loads(self.stt.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != last_partial and len(partial_text) > 5:
                        print(f"\r🎤 सुन रहा हूं: {partial_text[:30]}...", end='', flush=True)
                        last_partial = partial_text
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Audio processing error: {e}")
    
    def show_session_summary(self):
        """Show complete session statistics"""
        session_duration = datetime.now() - self.session_start
        
        print("\n📊 Complete Cloud Session Summary:")
        print("=" * 70)
        print(f"⏱️ Session Duration: {session_duration}")
        print(f"💬 Total Interactions: {self.total_interactions}")
        print(f"✅ Successful Responses: {self.successful_responses}")
        
        if self.total_interactions > 0:
            success_rate = (self.successful_responses / self.total_interactions) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.last_response_time > 0:
            print(f"⚡ Last Response Time: {self.last_response_time:.2f}s")
        
        # Show component summaries
        print("\n🔧 Component Performance:")
        
        # Cloud LLM summary
        current_llm = self.cloud_llm.current_llm
        if current_llm:
            model = self.cloud_llm.llm_apis[current_llm]["model"]
            print(f"🌐 LLM Provider: {current_llm} ({model})")
        
        # NLP summary
        nlp_summary = self.cloud_llm.nlp_detector.get_conversation_summary()
        if nlp_summary.get("total_interactions", 0) > 0:
            print(f"🧠 NLP Accuracy: {nlp_summary['average_confidence']:.2f}")
            print(f"🎯 Top Intents: {list(nlp_summary['intent_distribution'].keys())[:3]}")
        
        # Data sources
        enabled_sources = [k for k, v in self.cloud_llm.data_sources.items() if v["enabled"]]
        if enabled_sources:
            print(f"📊 Real-time Data: {', '.join(enabled_sources)}")
        
        print("\n🙏 धन्यवाद! Cloud-powered farming assistance के लिए!")


def main():
    """Main function"""
    try:
        assistant = CompleteCloudFarmerAssistant()
        assistant.run_complete_cloud_system()
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ System startup failed: {e}")


if __name__ == "__main__":
    main()
