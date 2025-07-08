#!/usr/bin/env python3
"""
Simple TTS Test - Direct imports
"""

import sys
import os

print("🔊 Simple TTS Test")
print("=" * 40)

# Test imports
print("Testing imports...")

try:
    import pyttsx3
    print("✅ pyttsx3 imported")
    
    # Test pyttsx3
    engine = pyttsx3.init()
    print("✅ pyttsx3 engine initialized")
    
    # Test speech
    print("🔊 Testing pyttsx3 speech...")
    engine.say("नमस्कार किसान भाई")
    engine.runAndWait()
    print("✅ pyttsx3 speech test completed")
    
except Exception as e:
    print(f"❌ pyttsx3 error: {e}")

print()

try:
    from gtts import gTTS
    import pygame
    import tempfile
    print("✅ gTTS and pygame imported")
    
    # Test gTTS
    print("🔊 Testing gTTS speech...")
    tts = gTTS(text="गेहूं के लिए खाद की सलाह", lang="hi")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        temp_filename = tmp_file.name
        tts.save(temp_filename)
    
    # Play with pygame
    pygame.mixer.init()
    pygame.mixer.music.load(temp_filename)
    pygame.mixer.music.play()
    
    # Wait for playback
    import time
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    pygame.mixer.quit()
    
    # Clean up
    try:
        os.unlink(temp_filename)
    except:
        pass
    
    print("✅ gTTS speech test completed")
    
except Exception as e:
    print(f"❌ gTTS error: {e}")

print("\n🎉 TTS Test Complete!")
