#!/usr/bin/env python3
"""
Simple Working Voice System
Minimal code to ensure voice input reaches AI
"""

import os
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Load API key
api_key = None
try:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if 'GROQ_API_KEY=' in line and '=' in line:
                    key = line.split('=', 1)[1].strip()
                    if key and key != "your_api_key_here":
                        api_key = key
                        print("✅ API key loaded")
                        break
except Exception as e:
    print(f"⚠️ API key loading failed: {e}")

def get_ai_response(query):
    """Get AI response"""
    print(f"🤖 AI Query: {query}")
    
    if not api_key:
        return {"success": False, "response": "API key not configured"}
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "आप एक भारतीय कृषि विशेषज्ञ हैं। हिंदी में संक्षिप्त जवाब दें।"},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ AI Response: {ai_response}")
            return {"success": True, "response": ai_response}
        else:
            print(f"❌ API Error: {response.status_code}")
            return {"success": False, "response": f"API Error: {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"success": False, "response": str(e)}

@app.route('/')
def index():
    """Simple working voice interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Simple Working Voice</title>
        
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
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                color: #333;
                max-width: 500px;
                width: 100%;
            }
            
            h1 { color: #2c3e50; margin-bottom: 20px; }
            
            .status {
                font-size: 20px;
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                background: #f8f9fa;
                color: #666;
            }
            
            .status.listening {
                background: #d4edda;
                color: #155724;
                animation: pulse 2s infinite;
            }
            
            .status.processing {
                background: #fff3cd;
                color: #856404;
                animation: pulse 1s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }
            
            .btn {
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                margin: 10px;
                font-weight: bold;
                transition: all 0.3s;
            }
            
            .btn.primary {
                background: #007bff;
                color: white;
            }
            
            .btn.success {
                background: #28a745;
                color: white;
            }
            
            .btn.danger {
                background: #dc3545;
                color: white;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .result {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
                display: none;
            }
            
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
            }
            
            .message.user {
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
            }
            
            .message.ai {
                background: #e8f5e8;
                border-left: 4px solid #4caf50;
            }
            
            .debug {
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
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Simple Working Voice</h1>
            <p>Direct voice input to AI system</p>
            
            <div class="status" id="status">
                Ready to test voice input
            </div>
            
            <div>
                <button class="btn success" id="startBtn" onclick="startVoice()">
                    🎤 Start Voice
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoice()" disabled>
                    🛑 Stop Voice
                </button>
                <button class="btn primary" onclick="toggleDebug()">
                    🔍 Debug
                </button>
            </div>
            
            <div class="debug" id="debugLog">
                Debug logs will appear here...
            </div>
            
            <div class="result" id="result">
                <h4>💬 Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isListening = false;
            
            function log(message) {
                const debugEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                debugEl.innerHTML += `[${timestamp}] ${message}\\n`;
                debugEl.scrollTop = debugEl.scrollHeight;
                console.log(message);
            }
            
            function toggleDebug() {
                const debugEl = document.getElementById('debugLog');
                debugEl.style.display = debugEl.style.display === 'none' ? 'block' : 'none';
            }
            
            function updateStatus(message, type = '') {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
                log(`Status: ${message}`);
            }
            
            function addMessage(speaker, text) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = `message ${speaker}`;
                messageEl.innerHTML = `<strong>${speaker === 'user' ? '👨‍🌾 आप' : '🤖 AI'}:</strong> ${text}`;
                messagesEl.appendChild(messageEl);
                document.getElementById('result').style.display = 'block';
                log(`Message: ${speaker} - ${text}`);
            }
            
            function startVoice() {
                log('🎤 Starting voice recognition...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('Voice recognition not supported! Use Chrome or Edge.');
                    log('❌ Speech recognition not supported');
                    return;
                }
                
                isListening = true;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                log('🔧 Speech recognition configured');
                
                recognition.onstart = function() {
                    log('✅ Speech recognition started');
                    updateStatus('🎤 Listening... Speak now!', 'listening');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    log(`🎤 Voice detected: "${transcript}" (confidence: ${confidence.toFixed(2)})`);
                    
                    if (transcript && confidence > 0.3) {
                        handleVoiceInput(transcript);
                    } else {
                        log('❌ Low confidence, please try again');
                        updateStatus('Low confidence, please speak again');
                        setTimeout(() => {
                            if (isListening) {
                                recognition.start();
                            }
                        }, 1000);
                    }
                };
                
                recognition.onerror = function(event) {
                    log(`❌ Speech recognition error: ${event.error}`);
                    updateStatus(`Error: ${event.error}`);
                    
                    if (event.error === 'not-allowed') {
                        alert('Microphone access denied! Please allow microphone access.');
                        stopVoice();
                    }
                };
                
                recognition.onend = function() {
                    log('🔚 Speech recognition ended');
                    if (isListening) {
                        log('🔄 Restarting recognition...');
                        setTimeout(() => {
                            if (isListening) {
                                recognition.start();
                            }
                        }, 500);
                    }
                };
                
                try {
                    recognition.start();
                    log('🚀 Recognition started');
                } catch (error) {
                    log(`❌ Failed to start: ${error.message}`);
                    stopVoice();
                }
            }
            
            function stopVoice() {
                log('🛑 Stopping voice recognition');
                isListening = false;
                
                if (recognition) {
                    recognition.stop();
                }
                
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Voice stopped');
            }
            
            async function handleVoiceInput(transcript) {
                log(`🔄 Processing voice input: "${transcript}"`);
                
                // Add user message
                addMessage('user', transcript);
                
                // Update status
                updateStatus('🧠 AI is thinking...', 'processing');
                
                try {
                    log('📡 Sending to AI...');
                    
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    log(`📡 Response status: ${response.status}`);
                    
                    const result = await response.json();
                    log(`📦 Response: ${JSON.stringify(result)}`);
                    
                    if (result.success) {
                        addMessage('ai', result.response);
                        updateStatus('✅ AI responded successfully');
                    } else {
                        addMessage('ai', 'माफ करें, कुछ गलती हुई है।');
                        updateStatus('❌ AI error');
                        log(`❌ AI error: ${result.response}`);
                    }
                } catch (error) {
                    log(`❌ Network error: ${error.message}`);
                    addMessage('ai', 'नेटवर्क की समस्या है।');
                    updateStatus('❌ Network error');
                }
                
                // Restart listening
                if (isListening) {
                    setTimeout(() => {
                        updateStatus('🎤 Listening... Speak now!', 'listening');
                        if (isListening) {
                            recognition.start();
                        }
                    }, 2000);
                }
            }
            
            // Initialize
            window.onload = function() {
                log('🚀 Simple voice system initialized');
                updateStatus('Ready to test voice input');
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/voice', methods=['POST'])
def handle_voice():
    """Handle voice input"""
    print("🎤 === VOICE API CALLED ===")
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        print(f"👨‍🌾 VOICE INPUT: {user_query}")
        
        if not user_query:
            print("❌ Empty voice query")
            return jsonify({"success": False, "response": "Empty query"})
        
        # Get AI response
        result = get_ai_response(user_query)
        
        print(f"📤 VOICE RESPONSE: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ VOICE API ERROR: {e}")
        return jsonify({"success": False, "response": str(e)})

if __name__ == '__main__':
    print("🎤 Starting Simple Working Voice System...")
    print("🌾 Minimal Voice Input to AI")
    print("=" * 50)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5007")
    print("💡 Press Ctrl+C to stop")
    print("\n📊 Watch for voice API calls:")
    print("   🎤 === VOICE API CALLED ===")
    print("   👨‍🌾 VOICE INPUT: [your voice]")
    print("   📤 VOICE RESPONSE: [AI response]")
    
    app.run(debug=True, host='0.0.0.0', port=5007)
