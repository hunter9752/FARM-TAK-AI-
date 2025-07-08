#!/usr/bin/env python3
"""
Farmer Assistant Website - Flask Backend
Complete STT → NLP → LLM → TTS Web Application
"""

import os
import sys
import json
import time
import tempfile
from datetime import datetime

# Try to import Flask
try:
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    print("💡 Installing Flask...")
    os.system("pip install flask flask-cors")
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS

import threading
import requests

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, 'nlp'))
sys.path.append(os.path.join(parent_dir, 'llm'))

# Import our systems
nlp_detector = None
try:
    from csv_based_intent_detector import CSVBasedFarmerIntentDetector
    nlp_detector = CSVBasedFarmerIntentDetector()
    print("✅ NLP module imported")
except ImportError as e:
    print(f"❌ NLP import failed: {e}")
except Exception as e:
    print(f"⚠️ NLP initialization failed: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global variables
nlp_detector = None
session_stats = {
    "total_queries": 0,
    "successful_responses": 0,
    "start_time": datetime.now()
}


class WebFarmerAssistant:
    """Web-based farmer assistant with complete pipeline"""
    
    def __init__(self):
        """Initialize web assistant"""
        self.load_env()
        self.api_key = os.getenv('GROQ_API_KEY')
        
        # Initialize NLP
        try:
            global nlp_detector
            nlp_detector = CSVBasedFarmerIntentDetector()
            print("✅ NLP system initialized")
        except Exception as e:
            print(f"❌ NLP initialization failed: {e}")
    
    def load_env(self):
        """Load environment variables"""
        env_file = os.path.join(os.path.dirname(current_dir), 'llm', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
    
    def process_text_query(self, user_query):
        """Process text query through NLP → LLM pipeline"""
        try:
            # Step 1: NLP Intent Detection
            if nlp_detector:
                nlp_result = nlp_detector.detect_intent(user_query)
            else:
                nlp_result = {
                    "intent": "general",
                    "confidence": 0.5,
                    "entities": {}
                }
            
            # Step 2: LLM Response
            llm_result = self.get_llm_response(user_query, nlp_result)
            
            # Update stats
            session_stats["total_queries"] += 1
            if llm_result["success"]:
                session_stats["successful_responses"] += 1
            
            return {
                "success": True,
                "user_query": user_query,
                "nlp_result": nlp_result,
                "llm_result": llm_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_llm_response(self, query, nlp_result):
        """Get LLM response"""
        if not self.api_key:
            return {
                "success": False,
                "response": "API key not configured",
                "response_time": 0
            }
        
        # Enhanced system prompt for web interface
        system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

पहचाना गया विषय: {nlp_result.get('intent', 'general')}
विश्वसनीयता: {nlp_result.get('confidence', 0):.2f}

जवाब हमेशा:
- हिंदी में दें
- 3-4 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो
- व्यावहारिक और उपयोगी हो
- Web interface के लिए उपयुक्त हो"""

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.7,
                "max_tokens": 200,
                "stream": False
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result["choices"][0]["message"]["content"].strip()
                
                return {
                    "success": True,
                    "response": llm_response,
                    "response_time": response_time,
                    "provider": "groq"
                }
            else:
                return {
                    "success": False,
                    "response": f"API Error: {response.status_code}",
                    "response_time": response_time,
                    "provider": "groq"
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "response_time": 0,
                "provider": "groq"
            }
    
    def generate_tts_audio(self, text):
        """Generate TTS audio for web"""
        try:
            from gtts import gTTS
            
            # Create TTS
            tts = gTTS(text=text, lang="hi", slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None


# Initialize web assistant
web_assistant = WebFarmerAssistant()


# Web Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/realtime')
def realtime_voice():
    """Real-time voice call page"""
    return render_template('realtime_voice.html')


@app.route('/api/query', methods=['POST'])
def process_query():
    """Process farmer query API"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Empty query"
            })
        
        # Process query
        result = web_assistant.process_text_query(user_query)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate TTS audio API with real-time streaming support"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        response_id = data.get('responseId', '')
        streaming = data.get('streaming', False)

        if not text:
            return jsonify({
                "success": False,
                "error": "Empty text"
            })

        # Generate audio
        audio_file = web_assistant.generate_tts_audio(text)

        if audio_file:
            # For real-time streaming, return immediately
            if streaming:
                return send_file(audio_file, as_attachment=False,
                               mimetype="audio/mpeg",
                               download_name=f"response_{response_id}.mp3")
            else:
                return send_file(audio_file, as_attachment=True,
                               download_name="response.mp3")
        else:
            return jsonify({
                "success": False,
                "error": "TTS generation failed"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/realtime/query', methods=['POST'])
def realtime_query():
    """Real-time query processing with interruption support"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        response_id = data.get('responseId', '')
        interrupt_previous = data.get('interruptPrevious', False)

        if not user_query:
            return jsonify({
                "success": False,
                "error": "Empty query"
            })

        # Handle interruption
        if interrupt_previous:
            # Cancel any previous processing
            # This would be implemented with a proper task queue in production
            pass

        # Process query with response ID
        result = web_assistant.process_text_query(user_query)

        if result["success"]:
            # Add response ID to result
            result["responseId"] = response_id
            result["timestamp"] = datetime.now().isoformat()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "responseId": response_id
        })


@app.route('/api/stats')
def get_stats():
    """Get session statistics"""
    uptime = datetime.now() - session_stats["start_time"]
    success_rate = 0
    
    if session_stats["total_queries"] > 0:
        success_rate = (session_stats["successful_responses"] / session_stats["total_queries"]) * 100
    
    return jsonify({
        "total_queries": session_stats["total_queries"],
        "successful_responses": session_stats["successful_responses"],
        "success_rate": success_rate,
        "uptime": str(uptime),
        "nlp_available": nlp_detector is not None,
        "llm_available": web_assistant.api_key is not None
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "nlp": "available" if nlp_detector else "unavailable",
            "llm": "available" if web_assistant.api_key else "unavailable",
            "tts": "available"
        }
    })


if __name__ == '__main__':
    print("🌐 Starting Farmer Assistant Website...")
    print("🌾 Complete STT → NLP → LLM → TTS Web Application")
    print("=" * 60)
    
    # Install dependencies
    try:
        import flask
        import flask_cors
        print("✅ Flask dependencies available")
    except ImportError:
        print("❌ Installing Flask dependencies...")
        os.system("pip install flask flask-cors")
    
    try:
        from gtts import gTTS
        print("✅ TTS dependencies available")
    except ImportError:
        print("❌ Installing TTS dependencies...")
        os.system("pip install gtts")
    
    print("\n🚀 Starting web server...")
    print("🌐 Website URL: http://localhost:5000")
    print("💡 Press Ctrl+C to stop server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
