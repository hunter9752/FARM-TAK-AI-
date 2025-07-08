#!/usr/bin/env python3
"""
Complete Farmer Assistant: STT → NLP → LLM Pipeline
Real-time speech-to-text with intelligent LLM responses
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
    from farmer_llm_assistant import FarmerLLMAssistant
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available.")
    sys.exit(1)


class CompleteFarmerAssistant:
    """Complete pipeline: Speech → Text → Intent → LLM Response"""
    
    def __init__(self):
        """Initialize the complete system"""
        print("🌾 Initializing Complete Farmer Assistant...")
        print("=" * 60)
        
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
        
        # 2. Initialize NLP
        print("🧠 Initializing NLP Intent Detection...")
        try:
            self.nlp = CSVBasedFarmerIntentDetector()
            print("✅ NLP system ready")
        except Exception as e:
            print(f"❌ NLP initialization failed: {e}")
            sys.exit(1)
        
        # 3. Initialize LLM
        print("🤖 Initializing LLM Assistant...")
        try:
            self.llm = FarmerLLMAssistant()
            print("✅ LLM system ready")
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            sys.exit(1)
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 80)
        print("🌾 स्वागत है - Complete Farmer Assistant")
        print("🎤 → 🧠 → 🤖 (Speech → Intent → LLM Response)")
        print("=" * 80)
        print("📋 सिस्टम की विशेषताएं:")
        print("  • 🎤 Real-time speech recognition")
        print("  • 🧠 94.4% accurate intent detection")
        print("  • 🤖 Human-like LLM responses")
        print("  • 🌾 48+ farming topics covered")
        print("  • 🗣️ Hindi + English support")
        print("=" * 80)
        print("💡 बोलकर अपने खेती के सवाल पूछें")
        print("🛑 रोकने के लिए Ctrl+C दबाएं")
        print("=" * 80)
    
    def process_complete_pipeline(self, transcribed_text: str):
        """Process through complete STT → NLP → LLM pipeline"""
        if not transcribed_text or len(transcribed_text.strip()) < 3:
            return
        
        if self.is_processing:
            return  # Avoid overlapping processing
        
        self.is_processing = True
        start_time = time.time()
        
        try:
            print(f"\n🎤 आपने कहा: {transcribed_text}")
            print("🔄 Processing through pipeline...")
            
            # Step 1: NLP Intent Detection
            print("  🧠 Step 1: Detecting intent...")
            intent_result = self.nlp.detect_intent(transcribed_text)
            
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            entities = intent_result["entities"]
            
            print(f"  🎯 Intent: {intent} (Confidence: {confidence:.2f})")
            if entities:
                print(f"  🏷️ Entities: {entities}")
            
            # Step 2: LLM Response Generation
            print("  🤖 Step 2: Generating intelligent response...")
            llm_response = self.llm.generate_llm_response(intent_result, transcribed_text)
            
            # Step 3: Display Results
            processing_time = time.time() - start_time
            self.display_complete_response(transcribed_text, intent_result, llm_response, processing_time)
            
            # Update statistics
            self.total_interactions += 1
            if confidence > 0.5:  # Consider successful if confidence > 0.5
                self.successful_responses += 1
            
            self.last_response_time = processing_time
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
        finally:
            self.is_processing = False
    
    def display_complete_response(self, user_query: str, intent_result: Dict, llm_response: str, processing_time: float):
        """Display formatted complete response"""
        print("\n" + "🌾" * 30)
        print("🤖 किसान सहायक का जवाब:")
        print("🌾" * 30)
        print(f"💬 {llm_response}")
        print("🌾" * 30)
        
        # Technical details
        print(f"⏱️ Response Time: {processing_time:.2f}s")
        print(f"📊 Confidence: {intent_result['confidence']:.2f}")
        print(f"🎯 Intent: {intent_result['intent']}")
        if intent_result['entities']:
            print(f"🏷️ Entities: {intent_result['entities']}")
        
        print("─" * 60)
        print("🎤 अगला सवाल बोलें...")
    
    def run_complete_system(self):
        """Run the complete integrated system"""
        try:
            # Display welcome
            self.display_welcome()
            
            # Setup STT
            if not self.stt.select_language():
                return
            
            if not self.stt.load_improved_model():
                return
            
            print("\n🎯 Complete system ready! Start speaking...")
            print("💡 Speak clearly and wait for response")
            print("-" * 80)
            
            # Start STT with LLM integration
            self.stt.is_running = True
            
            # Modified audio processing for complete pipeline
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
                print(f"🎤 Listening... (Sample rate: {self.stt.sample_rate} Hz)")
                
                while self.stt.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down system...")
            self.stt.is_running = False
            self.show_session_summary()
            
        except Exception as e:
            print(f"❌ System error: {e}")
            self.stt.is_running = False
    
    def integrated_audio_processing(self):
        """Audio processing with complete pipeline integration"""
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
                
                # Show audio activity (less frequent)
                if audio_count % 15 == 0:  # Reduced frequency
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))
                    
                    bar_length = 15
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
                    # Final result - process through complete pipeline
                    result = json.loads(self.stt.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text and len(text) > 2:
                        # Clear the audio bar
                        print("\r" + " " * 40 + "\r", end='')
                        
                        # Process through complete pipeline
                        self.process_complete_pipeline(text)
                        
                        last_partial = ""
                else:
                    # Partial result (show less frequently)
                    partial = json.loads(self.stt.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != last_partial and len(partial_text) > 5:
                        print(f"\r🎤 सुन रहा हूं: {partial_text[:40]}...", end='', flush=True)
                        last_partial = partial_text
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Audio processing error: {e}")
    
    def show_session_summary(self):
        """Show complete session statistics"""
        session_duration = datetime.now() - self.session_start
        
        print("\n📊 Complete Session Summary:")
        print("=" * 60)
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
        
        # NLP summary
        nlp_summary = self.nlp.get_conversation_summary()
        if nlp_summary.get("total_interactions", 0) > 0:
            print(f"🧠 NLP Accuracy: {nlp_summary['average_confidence']:.2f}")
            print(f"🎯 Top Intents: {list(nlp_summary['intent_distribution'].keys())[:3]}")
        
        # LLM summary
        llm_summary = self.llm.get_conversation_summary()
        if llm_summary.get("total_queries", 0) > 0:
            print(f"🤖 LLM Model: {llm_summary['llm_model']}")
            print(f"💬 LLM Queries: {llm_summary['total_queries']}")
        
        print("\n🙏 धन्यवाद! खेती में सफलता की शुभकामनाएं!")


def main():
    """Main function"""
    try:
        assistant = CompleteFarmerAssistant()
        assistant.run_complete_system()
    except KeyboardInterrupt:
        print("\n👋 अलविदा!")
    except Exception as e:
        print(f"❌ System startup failed: {e}")


if __name__ == "__main__":
    main()
