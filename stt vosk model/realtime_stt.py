#!/usr/bin/env python3
"""
Real-time Speech-to-Text Application using Vosk
Supports Hindi, Marathi, Tamil, and English languages
Works entirely offline with local Vosk models
"""

import json
import queue
import sys
import threading
import time
import os
from pathlib import Path

import sounddevice as sd
import vosk
import numpy as np


class RealtimeSTT:
    """Real-time Speech-to-Text application using Vosk library"""
    
    def __init__(self):
        """Initialize the STT application"""
        # Language model configuration
        self.language_models = {
            "en": {
                "name": "English",
                "model_path": "models/vosk-model-small-en-us-0.15",
                "sample_rate": 16000
            },
            "hi": {
                "name": "Hindi", 
                "model_path": "models/vosk-model-hi-0.22",
                "sample_rate": 16000
            },
            "mr": {
                "name": "Marathi",
                "model_path": "models/vosk-model-mr-0.22", 
                "sample_rate": 16000
            },
            "ta": {
                "name": "Tamil",
                "model_path": "models/vosk-model-ta-0.22",
                "sample_rate": 16000
            }
        }
        
        # Application state
        self.selected_language = None
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_running = False
        
        # Audio configuration
        self.sample_rate = 16000
        self.block_size = 4000  # Smaller blocks for better responsiveness
        self.audio_gain = 10.0  # Amplify audio signal
        
    def display_welcome(self):
        """Display welcome message and available languages"""
        print("=" * 60)
        print("🎤 Real-time Speech-to-Text Application")
        print("=" * 60)
        print("Supported Languages:")
        for code, info in self.language_models.items():
            print(f"  {code.upper()}: {info['name']}")
        print("=" * 60)
        
    def select_language(self):
        """Allow user to select a language for transcription"""
        while True:
            try:
                choice = input("\nEnter language code (en/hi/mr/ta): ").lower().strip()
                
                if choice in self.language_models:
                    self.selected_language = choice
                    lang_info = self.language_models[choice]
                    print(f"✅ Selected: {lang_info['name']}")
                    return True
                else:
                    print("❌ Invalid choice. Please select from: en, hi, mr, ta")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return False
                
    def check_model_exists(self, model_path):
        """Check if the Vosk model exists at the specified path"""
        if not os.path.exists(model_path):
            return False

        # Check if it's a valid Vosk model directory
        # Different models have different structures, so check for key directories
        required_dirs = ['am', 'conf']
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(model_path, dir_name)):
                return False

        # Check for essential files
        essential_files = [
            os.path.join('am', 'final.mdl'),
            os.path.join('conf', 'mfcc.conf')
        ]
        for file_path in essential_files:
            if not os.path.exists(os.path.join(model_path, file_path)):
                return False
        return True
        
    def load_model(self):
        """Load the Vosk model for the selected language"""
        if not self.selected_language:
            raise ValueError("No language selected")
            
        lang_info = self.language_models[self.selected_language]
        model_path = lang_info["model_path"]
        
        print(f"\n🔄 Loading {lang_info['name']} model...")
        
        # Check if model exists
        if not self.check_model_exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            print(f"\n📥 Please download the {lang_info['name']} model:")
            print(f"   1. Visit: https://alphacephei.com/vosk/models")
            print(f"   2. Download the appropriate model for {lang_info['name']}")
            print(f"   3. Extract it to: {model_path}")
            return False
            
        try:
            # Load the model
            self.model = vosk.Model(model_path)
            self.sample_rate = lang_info["sample_rate"]
            
            # Create recognizer
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            
            print(f"✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
            
    def audio_callback(self, indata, frames, time, status):
        """Callback function for audio input"""
        if status:
            print(f"Audio status: {status}")

        # Convert to numpy array first
        audio_array = np.frombuffer(indata, dtype=np.float32).copy()

        # Amplify and clip to prevent overflow
        amplified = np.clip(audio_array * self.audio_gain, -1.0, 1.0)

        # Convert to int16 and then to bytes
        audio_data = (amplified * 32767).astype('int16').tobytes()
        self.audio_queue.put(audio_data)
        
    def process_audio(self):
        """Process audio data from the queue and perform recognition"""
        print("\n🎯 Starting transcription...")
        print("💡 Speak into your microphone (Ctrl+C to stop)")
        print("🔊 Audio levels will be shown - speak loudly and clearly!")
        print("-" * 60)

        last_partial = ""
        audio_count = 0

        while self.is_running:
            try:
                # Get audio data from queue
                data = self.audio_queue.get(timeout=1)
                audio_count += 1

                # Show audio activity every 10 chunks
                if audio_count % 10 == 0:
                    # Convert back to float to check levels
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))

                    # Show volume bar
                    bar_length = 20
                    filled_length = int(bar_length * min(volume * 50, 1.0))  # Scale up for visibility
                    bar = '█' * filled_length + '-' * (bar_length - filled_length)
                    print(f"\rAudio: |{bar}| {volume:.3f}", end='', flush=True)

                # Process with recognizer
                if self.recognizer.AcceptWaveform(data):
                    # Final result
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        print(f"\n✅ Final: {text}")
                        last_partial = ""
                else:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    if partial_text and partial_text != last_partial:
                        print(f"\n... {partial_text}", end='', flush=True)
                        last_partial = partial_text

            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Error processing audio: {e}")
                
    def start_transcription(self):
        """Start real-time audio transcription"""
        if not self.recognizer:
            print("❌ No model loaded. Cannot start transcription.")
            return False
            
        try:
            self.is_running = True
            
            # Start audio processing thread
            audio_thread = threading.Thread(target=self.process_audio, daemon=True)
            audio_thread.start()
            
            # Start audio stream
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                device=None,  # Use default device
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print(f"🎤 Listening... (Sample rate: {self.sample_rate} Hz)")
                
                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping transcription...")
            self.is_running = False
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            self.is_running = False
            
        return True
        
    def run(self):
        """Main application entry point"""
        try:
            # Display welcome message
            self.display_welcome()
            
            # Language selection
            if not self.select_language():
                return
                
            # Load model
            if not self.load_model():
                return
                
            # Start transcription
            self.start_transcription()
            
        except KeyboardInterrupt:
            print("\n👋 Application terminated by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("🔚 Application ended")


def main():
    """Main function"""
    # Create and run the STT application
    stt_app = RealtimeSTT()
    stt_app.run()


if __name__ == "__main__":
    main()
