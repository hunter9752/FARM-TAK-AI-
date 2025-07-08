#!/usr/bin/env python3
"""
Real-Time Call Agent - Like Phone Call
Perfect voice interaction system for farmers
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

def get_ai_response(query):
    """Get AI response for farmer query"""
    print(f"🎤 Farmer: {query}")
    
    if not GROQ_API_KEY:
        return "API key की समस्या है।"
    
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
                    "content": "आप एक भारतीय कृषि विशेषज्ञ हैं। हिंदी में 2-3 वाक्य में practical सलाह दें। 'भाई' या 'जी' का use करें। बिल्कुल phone call की तरह बात करें।"
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 120
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"🤖 AI: {ai_response}")
            return ai_response
        else:
            print(f"❌ API Error: {response.status_code}")
            return "AI में कुछ समस्या है, भाई।"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "नेटवर्क की समस्या है, भाई।"

def generate_voice(text):
    """Generate voice from text"""
    print(f"🔊 Generating voice: {text[:50]}...")
    
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        print(f"✅ Voice generated: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"❌ Voice error: {e}")
        return None

@app.route('/')
def index():
    """Real-time call agent interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📞 Real-Time Call Agent</title>
        
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            
            .phone-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                padding: 40px;
                text-align: center;
                color: #333;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 25px 50px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }
            
            .phone-container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
                transform: rotate(45deg);
                animation: shine 3s infinite;
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
                position: relative;
                z-index: 1;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 16px;
                position: relative;
                z-index: 1;
            }
            
            .call-status {
                font-size: 24px;
                font-weight: bold;
                margin: 30px 0;
                padding: 20px;
                border-radius: 15px;
                background: #f8f9fa;
                color: #666;
                position: relative;
                z-index: 1;
                transition: all 0.3s ease;
            }
            
            .call-status.connected {
                background: linear-gradient(45deg, #d4edda, #c3e6cb);
                color: #155724;
                animation: pulse 2s infinite;
                border: 2px solid #28a745;
            }
            
            .call-status.listening {
                background: linear-gradient(45deg, #cce5ff, #b3d9ff);
                color: #004085;
                animation: listening 1.5s infinite;
                border: 2px solid #007bff;
            }
            
            .call-status.speaking {
                background: linear-gradient(45deg, #fff3cd, #ffeaa7);
                color: #856404;
                animation: speaking 1s infinite;
                border: 2px solid #ffc107;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.9; }
            }
            
            @keyframes listening {
                0%, 100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); }
                50% { box-shadow: 0 0 0 20px rgba(0, 123, 255, 0); }
            }
            
            @keyframes speaking {
                0%, 100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
                50% { box-shadow: 0 0 0 15px rgba(255, 193, 7, 0); }
            }
            
            .call-button {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: none;
                font-size: 30px;
                cursor: pointer;
                margin: 15px;
                transition: all 0.3s ease;
                position: relative;
                z-index: 1;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            }
            
            .call-button.start {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .call-button.end {
                background: linear-gradient(45deg, #dc3545, #e74c3c);
                color: white;
            }
            
            .call-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.3);
            }
            
            .call-button:active {
                transform: translateY(0);
            }
            
            .call-button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .conversation-display {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
                max-height: 300px;
                overflow-y: auto;
                display: none;
                position: relative;
                z-index: 1;
            }
            
            .message {
                margin: 15px 0;
                padding: 12px 16px;
                border-radius: 12px;
                animation: messageSlide 0.3s ease;
                position: relative;
            }
            
            @keyframes messageSlide {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.farmer {
                background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                margin-left: 30px;
                border-left: 4px solid #2196f3;
            }
            
            .message.ai {
                background: linear-gradient(45deg, #e8f5e8, #c8e6c9);
                margin-right: 30px;
                border-left: 4px solid #4caf50;
            }
            
            .message-header {
                font-weight: bold;
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .message-text {
                font-size: 16px;
                line-height: 1.4;
                margin-bottom: 8px;
            }
            
            .message-time {
                font-size: 12px;
                color: #666;
                text-align: right;
            }
            
            .voice-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #28a745;
                border-radius: 50%;
                margin-right: 8px;
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
            
            .connection-info {
                background: rgba(0, 123, 255, 0.1);
                border: 1px solid #007bff;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                font-size: 14px;
                color: #004085;
                position: relative;
                z-index: 1;
            }
        </style>
    </head>
    <body>
        <div class="phone-container">
            <h1>📞 Real-Time Call Agent</h1>
            <p class="subtitle">AI Farming Expert - Voice Call</p>
            
            <div class="connection-info">
                <strong>🌾 AI कृषि विशेषज्ञ से जुड़ें</strong><br>
                बिल्कुल phone call की तरह बात करें
            </div>
            
            <div class="call-status" id="callStatus">
                📞 Call करने के लिए तैयार
            </div>
            
            <div>
                <button class="call-button start" id="startCall" onclick="startCall()">
                    📞
                </button>
                <button class="call-button end" id="endCall" onclick="endCall()" disabled>
                    📵
                </button>
            </div>
            
            <div class="conversation-display" id="conversation">
                <h4>💬 Call Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isCallActive = false;
            let currentAudio = null;
            let callStartTime = null;
            
            function updateCallStatus(message, type = '') {
                const statusEl = document.getElementById('callStatus');
                statusEl.textContent = message;
                statusEl.className = `call-status ${type}`;
                console.log('📞 Call Status:', message);
            }
            
            function startCall() {
                console.log('📞 Starting call...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge.');
                    return;
                }
                
                isCallActive = true;
                callStartTime = new Date();
                
                document.getElementById('startCall').disabled = true;
                document.getElementById('endCall').disabled = false;
                document.getElementById('conversation').style.display = 'block';
                
                // Initialize speech recognition
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                recognition.onstart = function() {
                    updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                    console.log('✅ Voice recognition started');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    console.log('🎤 Voice detected:', transcript, 'Confidence:', confidence);
                    
                    if (transcript && confidence > 0.3) {
                        processVoiceCall(transcript);
                    } else {
                        console.log('⚠️ Low confidence, restarting...');
                        if (isCallActive) {
                            setTimeout(() => recognition.start(), 1000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('❌ Voice error:', event.error);
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied! Please allow microphone access.');
                        endCall();
                    } else if (isCallActive) {
                        setTimeout(() => recognition.start(), 2000);
                    }
                };
                
                recognition.onend = function() {
                    console.log('🔄 Voice recognition ended');
                    if (isCallActive) {
                        setTimeout(() => recognition.start(), 500);
                    }
                };
                
                // Start recognition
                recognition.start();
                
                // Welcome message
                setTimeout(() => {
                    const welcomeMsg = 'नमस्कार भाई! मैं आपका AI कृषि विशेषज्ञ हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।';
                    addMessage('ai', welcomeMsg);
                    playVoiceResponse(welcomeMsg);
                }, 1500);
            }
            
            function endCall() {
                console.log('📵 Ending call...');
                isCallActive = false;
                
                if (recognition) {
                    recognition.stop();
                    recognition = null;
                }
                
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                document.getElementById('startCall').disabled = false;
                document.getElementById('endCall').disabled = true;
                
                const callDuration = callStartTime ? Math.floor((new Date() - callStartTime) / 1000) : 0;
                updateCallStatus(`📵 Call Ended (${callDuration}s)`);
                
                setTimeout(() => {
                    updateCallStatus('📞 Call करने के लिए तैयार');
                }, 3000);
            }
            
            async function processVoiceCall(transcript) {
                console.log('🔄 Processing voice call:', transcript);
                
                // Stop current audio if playing
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Add farmer message
                addMessage('farmer', transcript);
                
                // Update status
                updateCallStatus('🤖 AI सोच रहा है...', 'speaking');
                
                try {
                    // Get AI response
                    const response = await fetch('/api/call', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    const result = await response.json();
                    console.log('📦 AI response:', result);
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        await playVoiceResponse(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें भाई, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await playVoiceResponse(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Call processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है भाई।';
                    addMessage('ai', errorMsg);
                    await playVoiceResponse(errorMsg);
                }
            }
            
            async function playVoiceResponse(text) {
                console.log('🔊 Playing voice response:', text.substring(0, 50) + '...');
                updateCallStatus('🔊 AI बोल रहा है...', 'speaking');
                
                try {
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);
                        
                        currentAudio.onended = function() {
                            console.log('✅ Voice response finished');
                            currentAudio = null;
                            if (isCallActive) {
                                updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                            }
                        };
                        
                        currentAudio.onerror = function(e) {
                            console.error('❌ Audio playback error:', e);
                            if (isCallActive) {
                                updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                            }
                        };
                        
                        await currentAudio.play();
                        console.log('✅ Voice response started playing');
                    } else {
                        console.error('❌ Voice generation failed');
                        if (isCallActive) {
                            updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                        }
                    }
                } catch (error) {
                    console.error('❌ Voice playback error:', error);
                    if (isCallActive) {
                        updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                    }
                }
            }
            
            function addMessage(speaker, text) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = `message ${speaker}`;
                
                const speakerName = speaker === 'farmer' ? '👨‍🌾 आप' : '🤖 AI विशेषज्ञ';
                const timestamp = new Date().toLocaleTimeString('hi-IN');
                
                messageEl.innerHTML = `
                    <div class="message-header">${speakerName}</div>
                    <div class="message-text">${text}</div>
                    <div class="message-time">${timestamp}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
                
                console.log('💬 Message added:', speakerName, text.substring(0, 50) + '...');
            }
            
            // Initialize
            window.onload = function() {
                console.log('📞 Real-time call agent ready');
                updateCallStatus('📞 Call करने के लिए तैयार');
            };
            
            // Handle page unload
            window.onbeforeunload = function() {
                if (isCallActive) {
                    endCall();
                }
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/call', methods=['POST'])
def handle_call():
    """Handle voice call"""
    print("📞 === CALL API ===")
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"success": False, "error": "Empty query"})
        
        # Get AI response
        ai_response = get_ai_response(query)
        
        return jsonify({
            "success": True,
            "response": ai_response
        })
        
    except Exception as e:
        print(f"❌ Call API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/voice', methods=['POST'])
def handle_voice():
    """Handle voice generation"""
    print("🔊 === VOICE API ===")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_voice(text)
        
        if audio_file:
            return send_file(audio_file, as_attachment=True, download_name="voice.mp3")
        else:
            return jsonify({"success": False, "error": "Voice generation failed"})
            
    except Exception as e:
        print(f"❌ Voice API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("📞 Starting Real-Time Call Agent...")
    print("🌾 Like Phone Call - Voice Interaction")
    print("=" * 50)
    
    print(f"✅ API Key: {'Ready' if GROQ_API_KEY else 'Missing'}")
    
    print(f"\n🚀 Starting server...")
    print(f"🌐 URL: http://localhost:5013")
    print(f"💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5013)
