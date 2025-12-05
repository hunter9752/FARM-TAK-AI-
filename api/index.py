"""
Vercel Serverless Entry Point for FARM-TAK-AI
Complete Flask app optimized for Vercel deployment
"""
import sys
import os

# Setup paths for Vercel serverless environment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
website_dir = os.path.join(parent_dir, 'website')
nlp_dir = os.path.join(parent_dir, 'nlp')
llm_dir = os.path.join(parent_dir, 'llm')

sys.path.insert(0, website_dir)
sys.path.insert(0, nlp_dir)
sys.path.insert(0, llm_dir)
sys.path.insert(0, parent_dir)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
from datetime import datetime
import requests

# Create Flask app with template folder config
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Load environment variables
def load_env():
    """Load API key from environment"""
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        # Try to load from .env file (for local development)
        env_file = os.path.join(llm_dir, '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        if key.strip() == 'GROQ_API_KEY' and value.strip():
                            api_key = value.strip()
                            break
    return api_key

GROQ_API_KEY = load_env()

# NLP Detector (optional - will work without it)
nlp_detector = None
try:
    from csv_based_intent_detector import CSVBasedFarmerIntentDetector
    nlp_detector = CSVBasedFarmerIntentDetector()
    print("✅ NLP initialized")
except Exception as e:
    print(f"⚠️ NLP not available: {e}")

def get_llm_response(query, nlp_result=None):
    """Get AI farming advice"""
    if not GROQ_API_KEY:
        return {"success": False, "response": "API key not configured"}
    
    try:
        intent = nlp_result.get('intent', 'general') if nlp_result else 'general'
        
        system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं।
किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

विषय: {intent}

जवाब हमेशा:
- हिंदी में दें
- 3-4 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो"""
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            return {"success": True, "response": llm_response}
        else:
            return {"success": False, "response": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "response": f"Error: {str(e)}"}

def generate_tts(text):
    """Generate Hindi TTS audio"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Main page with embedded HTML"""
    return """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AI कृषि सलाहकार - FARM-TAK-AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        .subtitle {
            color: #718096;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .input-group {
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .response {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .response.active { display: block; }
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 18px;
            display: none;
        }
        .loading.active { display: block; }
        .status {
            background: #e6fffa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            color: #234e52;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌾 AI कृषि सलाहकार</h1>
        <p class="subtitle">Voice-based Farming Assistant powered by AI</p>
        
        <div class="status">
            ✅ System: <span id="status">Running on Vercel</span>
        </div>
        
        <div class="input-group">
            <textarea id="query" placeholder="अपना सवाल यहाँ लिखें... (जैसे: गेहूं की खेती कैसे करें?)"></textarea>
        </div>
        
        <button onclick="askQuestion()" id="askBtn">पूछें</button>
        
        <div class="loading" id="loading">⏳ जवाब तैयार हो रहा है...</div>
        <div class="response" id="response"></div>
    </div>
    
    <script>
        async function askQuestion() {
            const query = document.getElementById('query').value.trim();
            if (!query) {
                alert('कृपया अपना सवाल लिखें');
                return;
            }
            
            const btn = document.getElementById('askBtn');
            const loading = document.getElementById('loading');
            const response = document.getElementById('response');
            
            btn.disabled = true;
            loading.classList.add('active');
            response.classList.remove('active');
            
            try {
                const res = await fetch('/api/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                const data = await res.json();
                
                if (data.success && data.llm_result) {
                    response.innerHTML = '<strong>🌾 जवाब:</strong><br><br>' + data.llm_result.response;
                    response.classList.add('active');
                } else {
                    response.innerHTML = '<strong>⚠️ Error:</strong> ' + (data.error || 'कुछ गलत हो गया');
                    response.classList.add('active');
                }
            } catch (error) {
                response.innerHTML = '<strong>❌ Error:</strong> ' + error.message;
                response.classList.add('active');
            } finally {
                btn.disabled = false;
                loading.classList.remove('active');
            }
        }
        
        // Check health on load
        fetch('/api/health').then(r => r.json()).then(data => {
            document.getElementById('status').textContent = 
                data.status + (data.components ? ' | API: ' + data.components.llm : '');
        });
    </script>
</body>
</html>"""

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "nlp": "available" if nlp_detector else "unavailable",
            "llm": "available" if GROQ_API_KEY else "unavailable",
            "tts": "available"
        }
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process farming query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"success": False, "error": "Empty query"})
        
        # NLP detection (optional)
        nlp_result = None
        if nlp_detector:
            try:
                nlp_result = nlp_detector.detect_intent(query)
            except:
                pass
        
        # Get LLM response
        llm_result = get_llm_response(query, nlp_result)
        
        return jsonify({
            "success": True,
            "user_query": query,
            "nlp_result": nlp_result,
            "llm_result": llm_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Generate TTS audio"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_tts(text)
        
        if audio_file:
            return send_file(audio_file, mimetype='audio/mpeg')
        else:
            return jsonify({"success": False, "error": "TTS failed"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stats')
def stats():
    """API statistics"""
    return jsonify({
        "nlp_available": nlp_detector is not None,
        "llm_available": GROQ_API_KEY is not None,
        "timestamp": datetime.now().isoformat()
    })

# Export app for Vercel
