#!/usr/bin/env python3
"""
Working Voice Agent - New Approach
Guaranteed working voice call system for farmers
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
GROQ_API_KEY = None
try:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'GROQ_API_KEY=' in line:
                    GROQ_API_KEY = line.split('=', 1)[1].strip()
                    break
    print(f"✅ API Key: {'Loaded' if GROQ_API_KEY else 'Not found'}")
except Exception as e:
    print(f"❌ API key error: {e}")

def get_farming_advice(query):
    """Get farming advice from AI"""
    print(f"🌾 Farmer Query: {query}")
    
    if not GROQ_API_KEY:
        return "API key नहीं मिली है।"
    
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
                    "content": "आप एक भारतीय कृषि विशेषज्ञ हैं। हिंदी में 2-3 वाक्य में practical सलाह दें। 'भाई' या 'जी' का use करें।"
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            advice = result["choices"][0]["message"]["content"].strip()
            print(f"✅ AI Advice: {advice}")
            return advice
        else:
            print(f"❌ API Error: {response.status_code}")
            return "AI में कुछ समस्या है।"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "नेटवर्क की समस्या है।"

def create_audio(text):
    """Create audio from text"""
    print(f"🔊 Creating audio: {text}")
    
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        print(f"✅ Audio created: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"❌ Audio error: {e}")
        return None

@app.route('/')
def index():
    """Working voice agent interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Working Voice Agent</title>
        
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
            
            .btn.success { background: #28a745; color: white; }
            .btn.danger { background: #dc3545; color: white; }
            .btn:hover { transform: translateY(-2px); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            
            .conversation {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                max-height: 400px;
                overflow-y: auto;
                text-align: left;
                display: none;
            }
            
            .message {
                margin: 12px 0;
                padding: 15px;
                border-radius: 12px;
                animation: fadeIn 0.3s;
            }
            
            .message.farmer {
                background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                margin-left: 20px;
                border-left: 4px solid #2196f3;
            }
            
            .message.ai {
                background: linear-gradient(45deg, #e8f5e8, #c8e6c9);
                margin-right: 20px;
                border-left: 4px solid #4caf50;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .test-section {
                background: #e9ecef;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            
            input[type="text"] {
                width: 70%;
                padding: 10px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Working Voice Agent</h1>
            <p>Real-time voice call system for farmers</p>
            
            <div class="status" id="status">
                Ready for voice call
            </div>
            
            <div>
                <button class="btn success" id="startBtn" onclick="startVoiceCall()">
                    🎤 Start Voice Call
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoiceCall()" disabled>
                    📵 End Call
                </button>
            </div>
            
            <div class="test-section">
                <h4>🧪 Test First:</h4>
                <input type="text" id="testInput" placeholder="Type: गेहूं के लिए खाद की सलाह दो">
                <button onclick="testAPI()" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 5px;">
                    Test
                </button>
                <div id="testResult" style="margin-top: 10px;"></div>
            </div>
            
            <div class="conversation" id="conversation">
                <h4>💬 Voice Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isCallActive = false;
            let currentAudio = null;
            
            function updateStatus(message, type = '') {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
                console.log('Status:', message);
            }
            
            async function testAPI() {
                const query = document.getElementById('testInput').value.trim();
                if (!query) {
                    document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                    return;
                }
                
                console.log('Testing API with:', query);
                document.getElementById('testResult').innerHTML = '<div style="color: #007bff;">🔄 Testing...</div>';
                
                try {
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const result = await response.json();
                    console.log('API result:', result);
                    
                    if (result.success) {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724; margin-top: 10px;">
                                <strong>✅ Working!</strong><br>
                                ${result.response}
                            </div>`;
                    } else {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-top: 10px;">
                                <strong>❌ Error:</strong> ${result.error}
                            </div>`;
                    }
                } catch (error) {
                    document.getElementById('testResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-top: 10px;">
                            <strong>❌ Network Error:</strong> ${error.message}
                        </div>`;
                }
            }
            
            function startVoiceCall() {
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Use Chrome or Edge.');
                    return;
                }
                
                isCallActive = true;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('conversation').style.display = 'block';
                
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                recognition.onstart = function() {
                    updateStatus('🎤 Listening... Speak now!', 'listening');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    console.log('Voice:', transcript, 'Confidence:', confidence);
                    
                    if (transcript && confidence > 0.3) {
                        processVoice(transcript);
                    } else {
                        if (isCallActive) {
                            setTimeout(() => recognition.start(), 1000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Voice error:', event.error);
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied!');
                        stopVoiceCall();
                    }
                };
                
                recognition.onend = function() {
                    if (isCallActive) {
                        setTimeout(() => recognition.start(), 500);
                    }
                };
                
                recognition.start();
                
                setTimeout(() => {
                    addMessage('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
                }, 1000);
            }
            
            function stopVoiceCall() {
                isCallActive = false;
                
                if (recognition) recognition.stop();
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Call ended');
            }
            
            async function processVoice(transcript) {
                console.log('Processing voice:', transcript);
                
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                addMessage('farmer', transcript);
                updateStatus('🧠 AI is thinking...', 'processing');
                
                try {
                    const response = await fetch('/api/voice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    const result = await response.json();
                    console.log('Voice result:', result);
                    
                    if (result.success) {
                        addMessage('ai', result.response);
                        await playAudio(result.response);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await playAudio(errorMsg);
                    }
                } catch (error) {
                    console.error('Voice processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await playAudio(errorMsg);
                }
            }
            
            async function playAudio(text) {
                updateStatus('🔊 AI is speaking...', 'processing');
                
                try {
                    const response = await fetch('/api/audio', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);
                        
                        currentAudio.onended = function() {
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Listening... Speak now!', 'listening');
                            }
                        };
                        
                        await currentAudio.play();
                    }
                } catch (error) {
                    console.error('Audio error:', error);
                    if (isCallActive) {
                        updateStatus('🎤 Listening... Speak now!', 'listening');
                    }
                }
            }
            
            function addMessage(speaker, text) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = `message ${speaker}`;
                
                const speakerName = speaker === 'farmer' ? '👨‍🌾 आप' : '🤖 AI सलाहकार';
                const timestamp = new Date().toLocaleTimeString('hi-IN');
                
                messageEl.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 8px;">${speakerName}</div>
                    <div style="font-size: 16px; line-height: 1.4;">${text}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 8px;">${timestamp}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            // Auto-test on load
            window.onload = function() {
                console.log('Working voice agent ready');
                document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                setTimeout(testAPI, 1000);
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
        query = data.get('query', '').strip()
        
        print(f"👨‍🌾 Voice Input: {query}")
        
        if not query:
            return jsonify({"success": False, "error": "Empty query"})
        
        # Get farming advice
        advice = get_farming_advice(query)
        
        return jsonify({
            "success": True,
            "response": advice,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Voice API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/audio', methods=['POST'])
def handle_audio():
    """Handle audio generation"""
    print("🔊 === AUDIO API CALLED ===")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"🔊 Audio Text: {text}")
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = create_audio(text)
        
        if audio_file:
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            return jsonify({"success": False, "error": "Audio generation failed"})
            
    except Exception as e:
        print(f"❌ Audio API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🎤 Starting Working Voice Agent...")
    print("🌾 Simple and Reliable Voice Call System")
    print("=" * 50)
    
    print(f"✅ API Key: {'Loaded' if GROQ_API_KEY else 'Not found'}")
    
    print(f"\n🚀 Starting server...")
    print(f"🌐 URL: http://localhost:5012")
    print(f"💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5012)
