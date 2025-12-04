from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile
from datetime import datetime
import requests

# Add website directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website'))

# Create Flask app
app = Flask(__name__)
CORS(app)

# Load API key
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def get_farming_advice(query):
    """Get expert farming advice from AI"""
    print(f"🌾 Farmer Query: {query}")
    
    if not GROQ_API_KEY:
        return "API key की समस्या है, भाई।"
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system", 
                    "content": """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। 

जवाब देने का तरीका:
- हिंदी में स्पष्ट जवाब दें
- 2-3 वाक्य में practical सलाह दें
- "भाई" या "जी" का प्रयोग करें
- बिल्कुल phone call की तरह बात करें
- व्यावहारिक और actionable advice दें"""
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            return ai_response
        else:
            return "AI में कुछ समस्या है, भाई। फिर से कोशिश करें।"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "नेटवर्क की समस्या है, भाई। कनेक्शन चेक करें।"

def generate_hindi_voice(text):
    """Generate Hindi voice from text"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"❌ Voice generation error: {e}")
        return None

@app.route('/')
def index():
    """Main page with embedded HTML"""
    return """<!DOCTYPE html>
<html>
<head><title>🌾 Farmer Voice Agent</title></head>
<body>
<h1>🌾 AI कृषि सलाहकार</h1>
<p>Voice-based farming assistant</p>
<p>Status: Running on Vercel!</p>
</body>
</html>"""

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api_key": "configured" if GROQ_API_KEY else "missing"
    })

@app.route('/api/farming-advice', methods=['POST'])
def farming_advice():
    """Get farming advice"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"success": False, "error": "No query provided"}), 400
        
        response = get_farming_advice(query)
        return jsonify({"success": True, "response": response})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-voice', methods=['POST'])
def generate_voice():
    """Generate voice audio"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400
        
        audio_file = generate_hindi_voice(text)
        
        if audio_file:
            return send_file(audio_file, mimetype='audio/mpeg')
        else:
            return jsonify({"success": False, "error": "Voice generation failed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
