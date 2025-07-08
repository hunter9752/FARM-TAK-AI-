#!/usr/bin/env python3
"""
Audio Test Script - Check if microphone is working
"""

import sounddevice as sd
import numpy as np
import time


def test_microphone():
    """Test microphone input and show audio levels"""
    print("🎤 Testing Microphone Input")
    print("=" * 40)
    
    # List available devices
    print("\n📋 Available Audio Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            marker = " >" if i == sd.default.device[0] else "  "
            print(f"{marker} {i}: {device['name']} ({device['max_input_channels']} channels)")
    
    print(f"\n🎯 Using default input device: {sd.default.device[0]}")
    
    # Test audio input
    print("\n🔊 Testing audio input for 5 seconds...")
    print("💡 Speak into your microphone!")
    print("-" * 40)
    
    duration = 5  # seconds
    sample_rate = 16000
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        
        # Calculate volume level
        volume_norm = np.linalg.norm(indata) * 10
        
        # Show volume bar
        bar_length = 20
        filled_length = int(bar_length * min(volume_norm, 1.0))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\rVolume: |{bar}| {volume_norm:.2f}", end='', flush=True)
    
    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            callback=audio_callback,
            dtype='float32'
        ):
            time.sleep(duration)
            
        print(f"\n\n✅ Audio test completed!")
        print("If you saw volume bars moving, your microphone is working!")
        
    except Exception as e:
        print(f"\n❌ Audio test failed: {e}")
        print("Possible solutions:")
        print("1. Check microphone permissions")
        print("2. Try a different audio device")
        print("3. Restart the application")


def test_vosk_basic():
    """Test basic Vosk functionality"""
    print("\n🧪 Testing Vosk Integration")
    print("=" * 40)
    
    try:
        import vosk
        print("✅ Vosk library imported successfully")
        
        # Check if model exists
        import os
        model_path = "models/vosk-model-small-en-us-0.15"
        if os.path.exists(model_path):
            print("✅ English model found")
            
            # Try to load model
            model = vosk.Model(model_path)
            print("✅ Model loaded successfully")
            
            # Create recognizer
            rec = vosk.KaldiRecognizer(model, 16000)
            print("✅ Recognizer created successfully")
            
            print("\n🎉 Vosk is ready for transcription!")
            
        else:
            print(f"❌ Model not found at: {model_path}")
            print("Run: python download_models.py en")
            
    except Exception as e:
        print(f"❌ Vosk test failed: {e}")


def main():
    """Main test function"""
    print("🚀 Audio & STT System Test")
    print("=" * 50)
    
    # Test microphone
    test_microphone()
    
    # Test Vosk
    test_vosk_basic()
    
    print("\n🎯 Test Summary:")
    print("If both tests passed, your STT system should work!")
    print("If not, check the error messages above.")


if __name__ == "__main__":
    main()
