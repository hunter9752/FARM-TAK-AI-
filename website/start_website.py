#!/usr/bin/env python3
"""
Farmer Assistant Website Launcher
Automated setup and launch script
"""

import os
import sys
import subprocess
import time
import webbrowser
from datetime import datetime


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing website dependencies...")
    
    try:
        # Install Flask and other requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "flask", "flask-cors", "requests", "gtts", "pandas"
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_system_requirements():
    """Check if all system components are available"""
    print("🔍 Checking system requirements...")
    
    # Check if parent directories exist
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_dirs = [
        os.path.join(parent_dir, 'nlp'),
        os.path.join(parent_dir, 'llm'),
        os.path.join(parent_dir, 'tts model')
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Found: {os.path.basename(dir_path)}")
        else:
            print(f"❌ Missing: {os.path.basename(dir_path)}")
            return False
    
    # Check API keys
    env_file = os.path.join(parent_dir, 'llm', '.env')
    if os.path.exists(env_file):
        print("✅ API configuration found")
    else:
        print("⚠️ API configuration not found (website will have limited functionality)")
    
    return True


def start_website():
    """Start the website server"""
    print("🌐 Starting Farmer Assistant Website...")
    print("=" * 60)
    
    # Change to website directory
    website_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(website_dir)
    
    # Start Flask app
    try:
        print("🚀 Starting web server...")
        print("🌐 Website will be available at: http://localhost:5000")
        print("💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Wait a moment then open browser
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:5000')
                print("🌐 Opening website in browser...")
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
                print("💡 Please manually open: http://localhost:5000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Start Flask app
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Website server stopped")
    except Exception as e:
        print(f"❌ Failed to start website: {e}")


def show_website_info():
    """Show website information"""
    print("🌾 Farmer Assistant Website")
    print("=" * 60)
    print("🎯 Complete AI-Powered Farming Guidance Platform")
    print("")
    print("✅ Features:")
    print("  • 🎤 Voice Input (Speech-to-Text)")
    print("  • 🧠 Smart Intent Detection (94.4% accuracy)")
    print("  • 🤖 Cloud LLM Responses (Groq/OpenAI/Gemini)")
    print("  • 🔊 Voice Output (Text-to-Speech)")
    print("  • 🌾 48+ Farming Topics")
    print("  • 🗣️ Hindi + English Support")
    print("  • 📱 Responsive Web Interface")
    print("")
    print("🚀 Complete Workflow:")
    print("  🎤 Farmer speaks/types → 🧠 AI understands → 🤖 Expert advice → 🔊 Voice response")
    print("")
    print("💡 Usage:")
    print("  1. Open website in browser")
    print("  2. Type or speak your farming questions")
    print("  3. Get instant AI-powered advice")
    print("  4. Hear responses in natural Hindi voice")
    print("=" * 60)


def main():
    """Main launcher function"""
    try:
        # Show info
        show_website_info()
        
        # Check system
        if not check_system_requirements():
            print("❌ System requirements not met")
            print("💡 Please ensure all components are properly installed")
            return
        
        # Install dependencies
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            return
        
        # Start website
        start_website()
        
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped")
    except Exception as e:
        print(f"❌ Launcher error: {e}")


if __name__ == "__main__":
    main()
