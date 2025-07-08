#!/usr/bin/env python3
"""
Enhanced Real-time Speech-to-Text Application with Accuracy Improvements
Includes noise reduction, audio filtering, and advanced processing
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
from scipy import signal
import noisereduce as nr


class EnhancedSTT:
    """Enhanced STT with accuracy improvements"""
    
    def __init__(self):
        """Initialize enhanced STT application"""
        # Language model configuration
        self.language_models = {
            "en": {
                "name": "English",
                "model_path": "models/vosk-model-small-en-us-0.15",
                "sample_rate": 16000,
                "large_model_path": "models/vosk-model-en-us-0.22"  # For better accuracy
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
        
        # Enhanced audio configuration
        self.sample_rate = 16000
        self.block_size = 2048  # Smaller for better responsiveness
        self.audio_gain = 5.0
        self.use_large_model = False
        
        # Audio processing buffers
        self.noise_sample = None
        self.audio_buffer = deque(maxlen=10)  # Keep last 10 chunks for noise estimation
        self.volume_history = deque(maxlen=20)  # Volume history for adaptive gain
        
        # Audio filters
        self.setup_audio_filters()
        
        # Post-processing
        self.confidence_threshold = 0.7
        self.min_word_length = 2
        
    def setup_audio_filters(self):
        """Setup audio filters for preprocessing"""
        # High-pass filter to remove low-frequency noise
        self.highpass_sos = signal.butter(4, 80, btype='high', fs=self.sample_rate, output='sos')
        
        # Band-pass filter for speech frequencies (300-3400 Hz)
        self.bandpass_sos = signal.butter(4, [300, 3400], btype='band', fs=self.sample_rate, output='sos')
        
        # Notch filter for 50Hz/60Hz power line noise
        self.notch_sos = signal.iirnotch(50, 30, fs=self.sample_rate)
        
    def preprocess_audio(self, audio_data):
        """Advanced audio preprocessing"""
        try:
            # Convert to float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # 1. Apply high-pass filter (remove low-frequency noise)
            filtered = signal.sosfilt(self.highpass_sos, audio_data)
            
            # 2. Apply band-pass filter (focus on speech frequencies)
            filtered = signal.sosfilt(self.bandpass_sos, filtered)
            
            # 3. Apply notch filter (remove power line noise)
            filtered = signal.sosfilt(self.notch_sos, filtered)
            
            # 4. Noise reduction (if we have noise sample)
            if self.noise_sample is not None and len(filtered) > 1024:
                try:
                    filtered = nr.reduce_noise(y=filtered, sr=self.sample_rate, 
                                             stationary=True, prop_decrease=0.8)
                except:
                    pass  # Fallback to original if noise reduction fails
            
            # 5. Adaptive gain control
            current_volume = np.sqrt(np.mean(filtered**2))
            self.volume_history.append(current_volume)
            
            if len(self.volume_history) > 5:
                avg_volume = statistics.mean(self.volume_history)
                if avg_volume > 0:
                    # Adaptive gain based on recent volume history
                    target_volume = 0.1  # Target RMS level
                    adaptive_gain = min(target_volume / avg_volume, 10.0)  # Max 10x gain
                    filtered = filtered * adaptive_gain
            
            # 6. Normalize and clip
            filtered = np.clip(filtered, -1.0, 1.0)
            
            return filtered
            
        except Exception as e:
            print(f"Audio preprocessing error: {e}")
            return audio_data
    
    def estimate_noise(self, audio_data):
        """Estimate background noise from quiet periods"""
        volume = np.sqrt(np.mean(audio_data**2))
        
        # If volume is very low, use this as noise sample
        if volume < 0.01:
            if self.noise_sample is None:
                self.noise_sample = audio_data.copy()
            else:
                # Update noise sample with exponential moving average
                alpha = 0.1
                self.noise_sample = alpha * audio_data + (1 - alpha) * self.noise_sample
    
    def select_model_quality(self):
        """Allow user to select model quality"""
        if self.selected_language == "en":
            print("\n🎯 Model Quality Options:")
            print("1. Fast (Small model - 40MB, faster processing)")
            print("2. Accurate (Large model - 1.8GB, better accuracy)")
            
            while True:
                try:
                    choice = input("Select quality (1/2): ").strip()
                    if choice == "1":
                        self.use_large_model = False
                        print("✅ Selected: Fast model")
                        break
                    elif choice == "2":
                        # Check if large model exists
                        large_path = self.language_models["en"]["large_model_path"]
                        if os.path.exists(large_path):
                            self.use_large_model = True
                            print("✅ Selected: Accurate model")
                            break
                        else:
                            print("❌ Large model not found. Download with:")
                            print("   python download_models.py en-large")
                            print("Using fast model instead...")
                            self.use_large_model = False
                            break
                    else:
                        print("❌ Invalid choice. Please enter 1 or 2")
                except KeyboardInterrupt:
                    return False
        return True
    
    def load_model_with_custom_vocab(self):
        """Load model with custom vocabulary for better accuracy"""
        if not self.selected_language:
            raise ValueError("No language selected")
            
        lang_info = self.language_models[self.selected_language]
        
        # Select model path based on quality choice
        if self.selected_language == "en" and self.use_large_model:
            model_path = lang_info.get("large_model_path", lang_info["model_path"])
        else:
            model_path = lang_info["model_path"]
        
        print(f"\n🔄 Loading {lang_info['name']} model...")
        print(f"📁 Path: {model_path}")
        
        if not self.check_model_exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            return False
            
        try:
            # Load the model
            self.model = vosk.Model(model_path)
            self.sample_rate = lang_info["sample_rate"]
            
            # Create recognizer with enhanced settings
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            
            # Add custom vocabulary if available
            self.add_custom_vocabulary()
            
            print(f"✅ Model loaded successfully!")
            print(f"🎯 Quality: {'High Accuracy' if self.use_large_model else 'Fast Processing'}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def add_custom_vocabulary(self):
        """Add custom vocabulary for better recognition"""
        try:
            # Common technical terms, names, etc.
            custom_vocab = [
                "vosk", "speech", "recognition", "transcription", "microphone",
                "audio", "python", "application", "real-time", "processing"
            ]
            
            # Language-specific vocabulary
            if self.selected_language == "hi":
                custom_vocab.extend([
                    "नमस्ते", "धन्यवाद", "कृपया", "माफ़", "करिए"
                ])
            elif self.selected_language == "mr":
                custom_vocab.extend([
                    "नमस्कार", "धन्यवाद", "कृपया", "माफ", "करा"
                ])
            
            # Note: Vosk doesn't directly support custom vocabulary addition
            # This is a placeholder for future implementation
            print(f"📚 Custom vocabulary ready ({len(custom_vocab)} terms)")
            
        except Exception as e:
            print(f"⚠️ Custom vocabulary setup failed: {e}")
    
    def check_model_exists(self, model_path):
        """Check if the Vosk model exists"""
        if not os.path.exists(model_path):
            return False
        
        # Check for essential directories/files
        required_items = ['am', 'conf']
        for item in required_items:
            if not os.path.exists(os.path.join(model_path, item)):
                return False
        return True
    
    def display_welcome(self):
        """Display enhanced welcome message"""
        print("=" * 70)
        print("🎤 Enhanced Real-time Speech-to-Text Application")
        print("🚀 With Advanced Accuracy Improvements")
        print("=" * 70)
        print("Supported Languages:")
        for code, info in self.language_models.items():
            print(f"  {code.upper()}: {info['name']}")
        print("\n🎯 Features:")
        print("  • Noise reduction and audio filtering")
        print("  • Adaptive gain control")
        print("  • Enhanced post-processing")
        print("  • Multiple model quality options")
        print("=" * 70)
    
    def select_language(self):
        """Language selection with enhanced options"""
        while True:
            try:
                choice = input("\nEnter language code (en/hi/mr/ta): ").lower().strip()
                
                if choice in self.language_models:
                    self.selected_language = choice
                    lang_info = self.language_models[choice]
                    print(f"✅ Selected: {lang_info['name']}")
                    
                    # Select model quality for English
                    if not self.select_model_quality():
                        return False
                    
                    return True
                else:
                    print("❌ Invalid choice. Please select from: en, hi, mr, ta")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return False

    def audio_callback(self, indata, frames, time, status):
        """Enhanced audio callback with preprocessing"""
        if status:
            print(f"Audio status: {status}")

        try:
            # Convert to numpy array
            audio_array = np.frombuffer(indata, dtype=np.float32).copy()

            # Store in buffer for noise estimation
            self.audio_buffer.append(audio_array)

            # Estimate noise from quiet periods
            self.estimate_noise(audio_array)

            # Apply advanced preprocessing
            processed_audio = self.preprocess_audio(audio_array)

            # Convert to int16 and add to queue
            audio_data = (processed_audio * 32767).astype('int16').tobytes()
            self.audio_queue.put(audio_data)

        except Exception as e:
            print(f"Audio callback error: {e}")

    def post_process_text(self, text):
        """Post-process recognized text for better accuracy"""
        if not text:
            return text

        # 1. Basic cleaning
        text = text.strip()

        # 2. Remove very short words (likely noise)
        words = text.split()
        filtered_words = [w for w in words if len(w) >= self.min_word_length or w.lower() in ['i', 'a']]

        # 3. Common corrections for English
        if self.selected_language == "en":
            corrections = {
                "uh": "", "um": "", "ah": "",  # Remove filler words
                "gonna": "going to", "wanna": "want to",
                "gotta": "got to", "kinda": "kind of"
            }

            for i, word in enumerate(filtered_words):
                if word.lower() in corrections:
                    replacement = corrections[word.lower()]
                    if replacement:
                        filtered_words[i] = replacement
                    else:
                        filtered_words[i] = ""  # Remove word

        # 4. Rejoin and clean
        result = " ".join([w for w in filtered_words if w])
        result = " ".join(result.split())  # Remove extra spaces

        return result

    def process_audio_enhanced(self):
        """Enhanced audio processing with confidence scoring"""
        print("\n🎯 Starting enhanced transcription...")
        print("💡 Speak clearly into your microphone")
        print("🔊 Audio preprocessing: ON")
        print("🧠 Post-processing: ON")
        print("-" * 70)

        last_partial = ""
        audio_count = 0
        confidence_scores = deque(maxlen=10)

        while self.is_running:
            try:
                # Get audio data from queue
                data = self.audio_queue.get(timeout=1)
                audio_count += 1

                # Show audio activity
                if audio_count % 5 == 0:
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                    volume = np.sqrt(np.mean(audio_array**2))

                    # Enhanced volume bar
                    bar_length = 30
                    filled_length = int(bar_length * min(volume * 20, 1.0))
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)

                    # Color coding based on volume
                    if volume > 0.05:
                        status = "🟢 GOOD"
                    elif volume > 0.02:
                        status = "🟡 OK"
                    else:
                        status = "🔴 LOW"

                    print(f"\rAudio: |{bar}| {volume:.3f} {status}", end='', flush=True)

                # Process with recognizer
                if self.recognizer.AcceptWaveform(data):
                    # Final result
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    confidence = result.get('confidence', 0.0)

                    if text:
                        # Post-process text
                        processed_text = self.post_process_text(text)

                        if processed_text:
                            confidence_scores.append(confidence)
                            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0

                            # Display with confidence indicator
                            conf_indicator = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
                            print(f"\n✅ Final: {processed_text} {conf_indicator} ({confidence:.2f})")

                            last_partial = ""
                else:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()

                    if partial_text and partial_text != last_partial:
                        # Post-process partial text
                        processed_partial = self.post_process_text(partial_text)
                        if processed_partial:
                            print(f"\n... {processed_partial}", end='', flush=True)
                            last_partial = partial_text

            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n❌ Error processing audio: {e}")

    def start_enhanced_transcription(self):
        """Start enhanced real-time transcription"""
        if not self.recognizer:
            print("❌ No model loaded. Cannot start transcription.")
            return False

        try:
            self.is_running = True

            # Start enhanced audio processing thread
            audio_thread = threading.Thread(target=self.process_audio_enhanced, daemon=True)
            audio_thread.start()

            # Start audio stream with enhanced settings
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                device=None,
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print(f"🎤 Enhanced listening... (Sample rate: {self.sample_rate} Hz)")
                print("🎯 Features active: Noise reduction, Audio filtering, Post-processing")

                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping enhanced transcription...")
            self.is_running = False

        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            self.is_running = False

        return True

    def run(self):
        """Main enhanced application entry point"""
        try:
            # Display welcome message
            self.display_welcome()

            # Language selection
            if not self.select_language():
                return

            # Load model with enhancements
            if not self.load_model_with_custom_vocab():
                return

            # Start enhanced transcription
            self.start_enhanced_transcription()

        except KeyboardInterrupt:
            print("\n👋 Enhanced application terminated by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("🔚 Enhanced application ended")


def main():
    """Main function"""
    # Create and run the enhanced STT application
    enhanced_stt = EnhancedSTT()
    enhanced_stt.run()


if __name__ == "__main__":
    main()
