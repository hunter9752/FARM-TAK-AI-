#!/usr/bin/env python3
"""
Improved Real-time Speech-to-Text Application with Accuracy Enhancements
Focuses on practical improvements without heavy dependencies
"""

import json
import queue
import threading
import time
import os
from collections import deque
import statistics

import sounddevice as sd
import vosk
import numpy as np


class ImprovedSTT:
    """Improved STT with practical accuracy enhancements"""
    
    def __init__(self):
        """Initialize improved STT application"""
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
        
        # Improved audio configuration
        self.sample_rate = 16000
        self.block_size = 1024  # Smaller blocks for better responsiveness
        self.base_gain = 8.0
        self.adaptive_gain = 1.0
        
        # Audio processing
        self.volume_history = deque(maxlen=20)
        self.noise_floor = 0.01
        
        # Post-processing settings
        self.confidence_threshold = 0.6
        self.min_word_length = 2
        
        # Performance tracking
        self.transcription_count = 0
        self.confidence_scores = deque(maxlen=50)
        
    def adaptive_audio_processing(self, audio_data):
        """Improved audio processing with adaptive features"""
        try:
            # Calculate current volume
            volume = np.sqrt(np.mean(audio_data**2))
            self.volume_history.append(volume)
            
            # Update noise floor estimate
            if volume < self.noise_floor * 2:
                self.noise_floor = 0.9 * self.noise_floor + 0.1 * volume
            
            # Adaptive gain control
            if len(self.volume_history) > 5:
                recent_avg = statistics.mean(list(self.volume_history)[-10:])
                if recent_avg > 0:
                    target_level = 0.15  # Target RMS level
                    self.adaptive_gain = min(target_level / recent_avg, 15.0)
            
            # Apply gain with noise gating
            if volume > self.noise_floor * 3:  # Only amplify if above noise floor
                processed = audio_data * self.base_gain * self.adaptive_gain
            else:
                processed = audio_data * 0.1  # Reduce noise
            
            # Soft clipping to prevent distortion
            processed = np.tanh(processed * 0.8) * 1.25
            processed = np.clip(processed, -1.0, 1.0)
            
            return processed
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            return audio_data
    
    def enhanced_post_processing(self, text):
        """Enhanced post-processing for better accuracy"""
        if not text:
            return text
        
        # 1. Basic cleaning
        text = text.strip().lower()
        
        # 2. Remove filler words and noise
        filler_words = {'uh', 'um', 'ah', 'er', 'mm', 'hmm'}
        words = text.split()
        
        # 3. Filter words
        filtered_words = []
        for word in words:
            # Skip very short words unless they're important
            if len(word) < self.min_word_length and word not in ['i', 'a', 'is', 'it', 'to', 'of', 'in', 'on']:
                continue
            # Skip filler words
            if word in filler_words:
                continue
            filtered_words.append(word)
        
        # 4. Language-specific corrections
        if self.selected_language == "en":
            corrections = {
                'gonna': 'going to',
                'wanna': 'want to', 
                'gotta': 'got to',
                'kinda': 'kind of',
                'sorta': 'sort of',
                'lotta': 'lot of',
                'gimme': 'give me',
                'lemme': 'let me',
                'dunno': "don't know",
                'yeah': 'yes',
                'yep': 'yes',
                'nope': 'no',
                'ok': 'okay',
                'alright': 'all right'
            }
            
            filtered_words = [corrections.get(word, word) for word in filtered_words]
        
        # 5. Capitalize first word and proper nouns
        if filtered_words:
            filtered_words[0] = filtered_words[0].capitalize()
            
            # Simple proper noun detection
            proper_nouns = {'python', 'vosk', 'windows', 'linux', 'mac', 'google', 'microsoft'}
            for i, word in enumerate(filtered_words):
                if word.lower() in proper_nouns:
                    filtered_words[i] = word.capitalize()
        
        # 6. Join and clean
        result = ' '.join(filtered_words)
        
        # 7. Basic punctuation (simple heuristics)
        if result and not result.endswith(('.', '!', '?')):
            # Add period if it seems like a complete sentence
            if len(result.split()) > 3:
                result += '.'
        
        return result
    
    def display_enhanced_welcome(self):
        """Display improved welcome message"""
        print("=" * 75)
        print("🎤 Improved Real-time Speech-to-Text Application")
        print("🚀 Enhanced Accuracy & Performance Features")
        print("=" * 75)
        print("Supported Languages:")
        for code, info in self.language_models.items():
            print(f"  {code.upper()}: {info['name']}")
        print("\n🎯 Improvements:")
        print("  • Adaptive gain control for varying volumes")
        print("  • Noise floor estimation and gating")
        print("  • Enhanced post-processing and corrections")
        print("  • Real-time confidence scoring")
        print("  • Optimized audio buffer management")
        print("=" * 75)
    
    def select_language(self):
        """Enhanced language selection"""
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
    
    def load_improved_model(self):
        """Load model with improved settings"""
        if not self.selected_language:
            raise ValueError("No language selected")
            
        lang_info = self.language_models[self.selected_language]
        model_path = lang_info["model_path"]
        
        print(f"\n🔄 Loading {lang_info['name']} model...")
        print(f"📁 Path: {model_path}")
        
        if not self.check_model_exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            print(f"📥 Download with: python download_models.py {self.selected_language}")
            return False
            
        try:
            # Load the model
            self.model = vosk.Model(model_path)
            self.sample_rate = lang_info["sample_rate"]
            
            # Create recognizer with optimized settings
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            
            print(f"✅ Model loaded successfully!")
            print(f"🎯 Optimizations: Adaptive processing, Enhanced filtering")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def check_model_exists(self, model_path):
        """Check if model exists and is valid"""
        if not os.path.exists(model_path):
            return False
        
        # Check for essential directories
        required_dirs = ['am', 'conf']
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(model_path, dir_name)):
                return False
        return True
    
    def audio_callback(self, indata, frames, time, status):
        """Improved audio callback"""
        if status:
            print(f"Audio status: {status}")
        
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(indata, dtype=np.float32).copy()
            
            # Apply improved processing
            processed_audio = self.adaptive_audio_processing(audio_array)
            
            # Convert to int16 and add to queue
            audio_data = (processed_audio * 32767).astype('int16').tobytes()
            self.audio_queue.put(audio_data)
            
        except Exception as e:
            print(f"Audio callback error: {e}")
    
    def process_audio_improved(self):
        """Improved audio processing with better feedback"""
        print("\n🎯 Starting improved transcription...")
        print("💡 Speak clearly - adaptive processing is active")
        print("🔊 Volume will auto-adjust based on your voice")
        print("-" * 75)
        
        last_partial = ""
        audio_count = 0
        
        while self.is_running:
            try:
                # Get audio data from queue
                data = self.audio_queue.get(timeout=1)
                audio_count += 1
                
                # Show enhanced audio feedback
                if audio_count % 3 == 0:
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))
                    
                    # Enhanced volume visualization
                    bar_length = 35
                    filled_length = int(bar_length * min(volume * 15, 1.0))
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    
                    # Dynamic status with adaptive gain info
                    if volume > 0.08:
                        status = "🟢 EXCELLENT"
                    elif volume > 0.04:
                        status = "🟡 GOOD"
                    elif volume > 0.02:
                        status = "🟠 OK"
                    else:
                        status = "🔴 TOO LOW"
                    
                    gain_info = f"Gain: {self.adaptive_gain:.1f}x"
                    print(f"\rAudio: |{bar}| {volume:.3f} {status} ({gain_info})", end='', flush=True)
                
                # Process with recognizer
                if self.recognizer.AcceptWaveform(data):
                    # Final result
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    confidence = result.get('confidence', 0.0)
                    
                    if text:
                        # Enhanced post-processing
                        processed_text = self.enhanced_post_processing(text)
                        
                        if processed_text:
                            self.transcription_count += 1
                            self.confidence_scores.append(confidence)
                            
                            # Enhanced confidence display
                            if confidence > 0.8:
                                conf_indicator = "🟢 HIGH"
                            elif confidence > 0.6:
                                conf_indicator = "🟡 MEDIUM"
                            else:
                                conf_indicator = "🔴 LOW"
                            
                            avg_conf = statistics.mean(self.confidence_scores) if self.confidence_scores else 0
                            
                            print(f"\n✅ [{self.transcription_count}] {processed_text}")
                            print(f"   Confidence: {conf_indicator} ({confidence:.2f}) | Avg: {avg_conf:.2f}")
                            
                            last_partial = ""
                else:
                    # Partial result with improved display
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text and partial_text != last_partial:
                        processed_partial = self.enhanced_post_processing(partial_text)
                        if processed_partial:
                            print(f"\n... {processed_partial}", end='', flush=True)
                            last_partial = partial_text
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Error processing audio: {e}")
    
    def start_improved_transcription(self):
        """Start improved real-time transcription"""
        if not self.recognizer:
            print("❌ No model loaded. Cannot start transcription.")
            return False
            
        try:
            self.is_running = True
            
            # Start improved audio processing thread
            audio_thread = threading.Thread(target=self.process_audio_improved, daemon=True)
            audio_thread.start()
            
            # Start audio stream with optimized settings
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                device=None,
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print(f"🎤 Improved listening... (Sample rate: {self.sample_rate} Hz)")
                print("🎯 Active features: Adaptive gain, Noise gating, Enhanced processing")
                
                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping improved transcription...")
            self.is_running = False
            
            # Show session statistics
            if self.confidence_scores:
                avg_confidence = statistics.mean(self.confidence_scores)
                print(f"\n📊 Session Stats:")
                print(f"   Transcriptions: {self.transcription_count}")
                print(f"   Average Confidence: {avg_confidence:.2f}")
                print(f"   Final Adaptive Gain: {self.adaptive_gain:.1f}x")
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            self.is_running = False
            
        return True
    
    def run(self):
        """Main improved application entry point"""
        try:
            # Display welcome message
            self.display_enhanced_welcome()
            
            # Language selection
            if not self.select_language():
                return
                
            # Load model with improvements
            if not self.load_improved_model():
                return
                
            # Start improved transcription
            self.start_improved_transcription()
            
        except KeyboardInterrupt:
            print("\n👋 Improved application terminated by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("🔚 Improved application ended")


def main():
    """Main function"""
    # Create and run the improved STT application
    improved_stt = ImprovedSTT()
    improved_stt.run()


if __name__ == "__main__":
    main()
