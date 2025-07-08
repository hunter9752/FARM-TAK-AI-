#!/usr/bin/env python3
"""
Simple Test Voice System - Debug Input Flow
"""

import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Load API key
GROQ_API_KEY = None
try:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'GROQ_API_KEY=' in line:
                    GROQ_API_KEY = line.split('=', 1)[1].strip()
                    break
    print(f"✅ API Key: {'Ready' if GROQ_API_KEY else 'Missing'}")
except Exception as e:
    print(f"❌ API key error: {e}")

def get_farming_response(query):
    """Get farming response"""
    print(f"🌾 === PROCESSING QUERY ===")
    print(f"🌾 Input: {query}")
    print(f"🌾 Length: {len(query)} characters")
    
    if not GROQ_API_KEY:
        print("❌ No API key")
        return "API key नहीं मिली।"
    
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
                    "content": "आप एक भारतीय कृषि विशेषज्ञ हैं। हिंदी में 2-3 वाक्य में practical सलाह दें।"
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        print(f"🌾 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"🌾 API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"🌾 AI Response: {ai_response}")
            return ai_response
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return "AI में समस्या है।"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "नेटवर्क की समस्या है।"

@app.route('/')
def index():
    """Simple test interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🧪 Simple Test Voice</title>
        
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 40px;
                text-align: center;
                color: #333;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            h1 { color: #2c3e50; margin-bottom: 20px; }
            
            .test-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            
            .status {
                font-size: 18px;
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                background: #e9ecef;
                color: #495057;
            }
            
            .status.success {
                background: #d4edda;
                color: #155724;
            }
            
            .status.error {
                background: #f8d7da;
                color: #721c24;
            }
            
            .status.processing {
                background: #fff3cd;
                color: #856404;
                animation: pulse 1s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .btn {
                padding: 12px 24px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin: 8px;
                font-weight: bold;
                transition: all 0.3s;
            }
            
            .btn.primary { background: #007bff; color: white; }
            .btn.success { background: #28a745; color: white; }
            .btn.danger { background: #dc3545; color: white; }
            .btn:hover { transform: translateY(-2px); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            
            input[type="text"] {
                width: 70%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-right: 10px;
            }
            
            .log {
                background: #343a40;
                color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                font-family: monospace;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
                text-align: left;
            }
            
            .result {
                background: #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Simple Test Voice</h1>
            <p>Debug Input Flow System</p>
            
            <div class="status" id="status">
                Ready for testing
            </div>
            
            <div class="test-section">
                <h3>📝 Text Input Test:</h3>
                <input type="text" id="textInput" placeholder="Type: गेहूं के लिए खाद की सलाह दो">
                <button class="btn primary" onclick="testText()">Test Text</button>
                <div id="textResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>🎤 Voice Input Test:</h3>
                <button class="btn success" id="voiceBtn" onclick="testVoice()">🎤 Test Voice</button>
                <button class="btn danger" id="stopBtn" onclick="stopVoice()" disabled>⏹️ Stop</button>
                <div id="voiceResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="log" id="debugLog">
                Debug logs will appear here...
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isListening = false;
            
            function log(message) {
                const logEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                logEl.innerHTML += `[${timestamp}] ${message}\\n`;
                logEl.scrollTop = logEl.scrollHeight;
                console.log(`[DEBUG] ${message}`);
            }
            
            function updateStatus(message, type = '') {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
                log(`Status: ${message}`);
            }
            
            async function testText() {
                const query = document.getElementById('textInput').value.trim();
                if (!query) {
                    document.getElementById('textInput').value = 'गेहूं के लिए खाद की सलाह दो';
                    return;
                }
                
                log(`📝 Testing text input: "${query}"`);
                updateStatus('🔄 Testing text input...', 'processing');
                document.getElementById('textResult').style.display = 'block';
                document.getElementById('textResult').innerHTML = '<div style="color: #007bff;">🔄 Processing...</div>';
                
                try {
                    const response = await fetch('/api/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    log(`📡 API response status: ${response.status}`);
                    const result = await response.json();
                    log(`📦 API result: ${JSON.stringify(result)}`);
                    
                    if (result.success) {
                        updateStatus('✅ Text input working!', 'success');
                        document.getElementById('textResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724;">
                                <strong>✅ Success!</strong><br>
                                <strong>Input:</strong> ${query}<br>
                                <strong>Output:</strong> ${result.response}
                            </div>`;
                    } else {
                        updateStatus('❌ Text input failed', 'error');
                        document.getElementById('textResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                                <strong>❌ Error:</strong> ${result.error}
                            </div>`;
                    }
                } catch (error) {
                    log(`❌ Network error: ${error.message}`);
                    updateStatus('❌ Network error', 'error');
                    document.getElementById('textResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                            <strong>❌ Network Error:</strong> ${error.message}
                        </div>`;
                }
            }
            
            function testVoice() {
                log('🎤 Starting voice test...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    log('❌ Voice recognition not supported');
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge.');
                    return;
                }
                
                isListening = true;
                document.getElementById('voiceBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('voiceResult').style.display = 'block';
                document.getElementById('voiceResult').innerHTML = '<div style="color: #007bff;">🎤 Listening...</div>';
                
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                recognition.onstart = function() {
                    log('✅ Voice recognition started');
                    updateStatus('🎤 Listening... Speak now!', 'processing');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    log(`🎤 Voice detected: "${transcript}" (confidence: ${confidence.toFixed(2)})`);
                    
                    if (transcript && confidence > 0.3) {
                        processVoiceInput(transcript);
                    } else {
                        log('⚠️ Low confidence, ignoring...');
                        document.getElementById('voiceResult').innerHTML = 
                            `<div style="background: #fff3cd; padding: 10px; border-radius: 5px; color: #856404;">
                                <strong>⚠️ Low Confidence:</strong> "${transcript}" (${confidence.toFixed(2)})
                            </div>`;
                        stopVoice();
                    }
                };
                
                recognition.onerror = function(event) {
                    log(`❌ Voice error: ${event.error}`);
                    updateStatus('❌ Voice error', 'error');
                    
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied! Please allow microphone access.');
                    }
                    
                    document.getElementById('voiceResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                            <strong>❌ Voice Error:</strong> ${event.error}
                        </div>`;
                    stopVoice();
                };
                
                recognition.onend = function() {
                    log('🔄 Voice recognition ended');
                    if (isListening) {
                        stopVoice();
                    }
                };
                
                recognition.start();
            }
            
            function stopVoice() {
                log('⏹️ Stopping voice test');
                isListening = false;
                
                if (recognition) {
                    recognition.stop();
                    recognition = null;
                }
                
                document.getElementById('voiceBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Voice test stopped');
            }
            
            async function processVoiceInput(transcript) {
                log(`🔄 Processing voice input: "${transcript}"`);
                updateStatus('🔄 Processing voice input...', 'processing');
                
                try {
                    const response = await fetch('/api/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    log(`📡 Voice API response status: ${response.status}`);
                    const result = await response.json();
                    log(`📦 Voice API result: ${JSON.stringify(result)}`);
                    
                    if (result.success) {
                        updateStatus('✅ Voice input working!', 'success');
                        document.getElementById('voiceResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724;">
                                <strong>✅ Voice Success!</strong><br>
                                <strong>Voice Input:</strong> "${transcript}"<br>
                                <strong>AI Output:</strong> ${result.response}
                            </div>`;
                    } else {
                        updateStatus('❌ Voice processing failed', 'error');
                        document.getElementById('voiceResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                                <strong>❌ Voice Error:</strong> ${result.error}
                            </div>`;
                    }
                } catch (error) {
                    log(`❌ Voice processing error: ${error.message}`);
                    updateStatus('❌ Voice processing error', 'error');
                    document.getElementById('voiceResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                            <strong>❌ Processing Error:</strong> ${error.message}
                        </div>`;
                }
                
                stopVoice();
            }
            
            // Initialize
            window.onload = function() {
                log('🧪 Simple test voice system ready');
                updateStatus('Ready for testing');
                document.getElementById('textInput').value = 'गेहूं के लिए खाद की सलाह दो';
            };
            
            // Auto-test text on load
            setTimeout(() => {
                log('🚀 Auto-testing text input...');
                testText();
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/api/test', methods=['POST'])
def test_api():
    """Test API endpoint"""
    print("🧪 === TEST API CALLED ===")
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        print(f"🧪 Test Input: '{query}'")
        print(f"🧪 Input Length: {len(query)} characters")
        print(f"🧪 Input Type: {type(query)}")
        
        if not query:
            print("❌ Empty query received")
            return jsonify({"success": False, "error": "Empty query"})
        
        # Process query
        response = get_farming_response(query)
        
        print(f"🧪 Test Output: '{response}'")
        print(f"🧪 Output Length: {len(response)} characters")
        
        return jsonify({
            "success": True,
            "response": response,
            "debug": {
                "input_length": len(query),
                "output_length": len(response),
                "api_key_status": "present" if GROQ_API_KEY else "missing"
            }
        })
        
    except Exception as e:
        print(f"❌ Test API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🧪 Starting Simple Test Voice System...")
    print("🔍 Debug Input Flow Issues")
    print("=" * 50)
    
    print(f"✅ API Key: {'Ready' if GROQ_API_KEY else 'Missing'}")
    
    print(f"\n🚀 Starting server...")
    print(f"🌐 URL: http://localhost:5014")
    print(f"💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5014)
