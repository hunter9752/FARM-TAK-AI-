#!/usr/bin/env python3
"""
Working Real-Time Voice Call System
Simplified and fully functional
"""

import os
import sys
import time
import tempfile
from datetime import datetime

# Import Flask
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

# Initialize Flask app
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

def get_llm_response(query):
    """Get LLM response"""
    print(f"🤖 Processing query: {query}")
    
    if not api_key:
        print("❌ No API key")
        return {
            "success": False,
            "response": "API key not configured",
            "response_time": 0
        }
    
    system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

जवाब हमेशा:
- हिंदी में दें
- 2-3 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो
- व्यावहारिक और उपयोगी हो"""

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "stream": False
        }
        
        print(f"🌐 Making API call...")
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        print(f"📡 API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            print(f"✅ LLM response: {llm_response}")
            
            return {
                "success": True,
                "response": llm_response,
                "response_time": response_time,
                "provider": "groq"
            }
        else:
            print(f"❌ API Error: {response.status_code}")
            return {
                "success": False,
                "response": f"API Error: {response.status_code}",
                "response_time": response_time,
                "provider": "groq"
            }
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "response_time": 0,
            "provider": "groq"
        }

def generate_tts_audio(text):
    """Generate TTS audio"""
    try:
        print(f"🔊 Generating TTS for: {text}")
        from gtts import gTTS
        
        # Create TTS
        tts = gTTS(text=text, lang="hi", slow=False)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        
        print(f"✅ TTS generated: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Main page with working voice call"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Working Voice Call - Farmer Assistant</title>
        
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: white;
            }
            
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                text-align: center;
                color: #333;
            }
            
            .status {
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
            }
            
            .status.idle {
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
            
            .status.speaking {
                background: #d1ecf1;
                color: #0c5460;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            
            .call-btn {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                border: none;
                font-size: 40px;
                margin: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .call-btn.start {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .call-btn.end {
                background: linear-gradient(45deg, #dc3545, #c82333);
                color: white;
            }
            
            .call-btn:hover {
                transform: scale(1.1);
            }
            
            .conversation {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                max-height: 300px;
                overflow-y: auto;
                text-align: left;
            }
            
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
            }
            
            .message.user {
                background: #e3f2fd;
                margin-left: 20px;
            }
            
            .message.ai {
                background: #e8f5e8;
                margin-right: 20px;
            }
            
            .test-section {
                margin: 30px 0;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            
            input[type="text"] {
                width: 70%;
                padding: 10px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            
            button {
                padding: 10px 20px;
                font-size: 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            
            button:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Working Real-Time Voice Call</h1>
            
            <div class="status idle" id="status">
                Ready to start voice call
            </div>
            
            <div>
                <button class="call-btn start" id="startBtn" onclick="startCall()">
                    📞
                </button>
                <button class="call-btn end" id="endBtn" onclick="endCall()" style="display: none;">
                    📵
                </button>
            </div>
            
            <div class="conversation" id="conversation" style="display: none;">
                <h4>💬 Conversation:</h4>
                <div id="messages"></div>
            </div>
            
            <div class="test-section">
                <h4>🧪 Test API (Text Mode):</h4>
                <input type="text" id="testInput" placeholder="Type farming question..." onkeypress="handleKeyPress(event)">
                <button onclick="testAPI()">Test</button>
                <div id="testResult" style="margin-top: 10px;"></div>
            </div>
        </div>
        
        <script>
            let isCallActive = false;
            let recognition = null;
            let currentAudio = null;
            
            // Test API function
            async function testAPI() {
                const query = document.getElementById('testInput').value.trim();
                if (!query) return;
                
                console.log('🧪 Testing API with:', query);
                document.getElementById('testResult').innerHTML = '🔄 Testing...';
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    console.log('📡 Test response status:', response.status);
                    const result = await response.json();
                    console.log('📦 Test result:', result);
                    
                    if (result.success) {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724;">
                                <strong>✅ Success!</strong><br>
                                ${result.llm_result.response}<br>
                                <small>Time: ${result.llm_result.response_time.toFixed(2)}s</small>
                            </div>`;
                    } else {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                                <strong>❌ Error:</strong> ${result.error}
                            </div>`;
                    }
                } catch (error) {
                    console.error('❌ Test error:', error);
                    document.getElementById('testResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                            <strong>❌ Network Error:</strong> ${error.message}
                        </div>`;
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    testAPI();
                }
            }
            
            // Voice call functions
            function startCall() {
                console.log('📞 Starting voice call...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('Voice recognition not supported. Please use Chrome or Edge.');
                    return;
                }
                
                isCallActive = true;
                updateStatus('Starting call...', 'processing');
                
                // Show/hide buttons
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('endBtn').style.display = 'inline-block';
                document.getElementById('conversation').style.display = 'block';
                
                // Initialize speech recognition
                recognition = new webkitSpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                recognition.onstart = function() {
                    console.log('🎤 Voice recognition started');
                    updateStatus('Listening... Speak now!', 'listening');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript;
                    console.log('🎤 Voice input:', transcript);
                    handleVoiceInput(transcript);
                };
                
                recognition.onerror = function(event) {
                    console.error('🎤 Recognition error:', event.error);
                    if (isCallActive) {
                        setTimeout(() => {
                            if (isCallActive) {
                                recognition.start();
                            }
                        }, 1000);
                    }
                };
                
                recognition.onend = function() {
                    console.log('🎤 Recognition ended');
                    if (isCallActive) {
                        setTimeout(() => {
                            if (isCallActive) {
                                recognition.start();
                            }
                        }, 500);
                    }
                };
                
                // Start recognition
                recognition.start();
                
                // Add welcome message
                addMessage('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
            }
            
            function endCall() {
                console.log('📵 Ending voice call...');
                
                isCallActive = false;
                
                if (recognition) {
                    recognition.stop();
                }
                
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                updateStatus('Call ended', 'idle');
                
                // Show/hide buttons
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('endBtn').style.display = 'none';
            }
            
            async function handleVoiceInput(transcript) {
                console.log('🔄 Processing voice input:', transcript);
                
                // Stop current audio if playing
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Add user message
                addMessage('user', transcript);
                
                // Update status
                updateStatus('AI is thinking...', 'processing');
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const aiResponse = result.llm_result.response;
                        addMessage('ai', aiResponse);
                        
                        // Generate and play TTS
                        await playTTS(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await playTTS(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Voice processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await playTTS(errorMsg);
                }
            }
            
            async function playTTS(text) {
                console.log('🔊 Playing TTS:', text);
                updateStatus('AI is speaking...', 'speaking');
                
                try {
                    const response = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);
                        
                        currentAudio.onended = function() {
                            console.log('🔊 Audio ended');
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('Listening... Speak now!', 'listening');
                            }
                        };
                        
                        await currentAudio.play();
                    } else {
                        throw new Error('TTS failed');
                    }
                } catch (error) {
                    console.error('🔊 TTS error:', error);
                    if (isCallActive) {
                        updateStatus('Listening... Speak now!', 'listening');
                    }
                }
            }
            
            function updateStatus(message, type) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
            }
            
            function addMessage(speaker, text) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = `message ${speaker}`;
                
                const speakerName = speaker === 'user' ? '👨‍🌾 You' : '🤖 AI';
                const timestamp = new Date().toLocaleTimeString();
                
                messageEl.innerHTML = `
                    <strong>${speakerName}:</strong> ${text}
                    <br><small style="color: #666;">${timestamp}</small>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            // Initialize
            console.log('🎤 Voice call system initialized');
        </script>
    </body>
    </html>
    """

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process query API"""
    print("🔄 API Query received")
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        print(f"📝 User query: {user_query}")
        
        if not user_query:
            print("❌ Empty query")
            return jsonify({"success": False, "error": "Empty query"})
        
        # Get LLM response
        llm_result = get_llm_response(user_query)
        
        result = {
            "success": llm_result["success"],
            "user_query": user_query,
            "llm_result": llm_result,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 Sending response: {result['success']}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate TTS audio API"""
    print("🔊 TTS request received")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"🔊 TTS text: {text}")
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_tts_audio(text)
        
        if audio_file:
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            return jsonify({"success": False, "error": "TTS generation failed"})
            
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🎤 Starting Working Voice Call System...")
    print("🌾 Real-Time Voice Call for Farmers")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5001")
    print("💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
