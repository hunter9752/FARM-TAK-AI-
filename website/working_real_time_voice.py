#!/usr/bin/env python3
"""
Working Real-Time Voice Call System
Complete voice input to AI with proper debugging
"""

import os
import sys
import time
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

def get_farming_response(query):
    """Get farming response"""
    print(f"🌾 Processing farmer query: {query}")
    
    if not api_key:
        print("❌ No API key available")
        return {"success": False, "response": "API key not configured"}
    
    system_prompt = """आप एक भारतीय कृषि विशेषज्ञ हैं। किसान के सवाल का सीधा जवाब दें।

- हिंदी में जवाब दें
- 1-2 वाक्य में संक्षिप्त रखें
- व्यावहारिक सलाह दें
- "भाई" या "जी" का use करें"""

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
            "max_tokens": 100,
            "stream": False
        }
        
        print(f"🌐 Making API call to Groq...")
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        print(f"📡 API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ AI Response: {ai_response}")
            
            return {
                "success": True,
                "response": ai_response,
                "response_time": response_time
            }
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {"success": False, "response": f"API Error: {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception in API call: {e}")
        return {"success": False, "response": f"Error: {str(e)}"}

def generate_tts_audio(text):
    """Generate TTS audio"""
    try:
        print(f"🔊 Generating TTS for: {text}")
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        print(f"✅ TTS generated: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

@app.route('/')
def index():
    """Working real-time voice call interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Working Real-Time Voice Call</title>
        
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
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 16px;
            }
            
            .status {
                font-size: 22px;
                font-weight: bold;
                margin: 25px 0;
                padding: 20px;
                border-radius: 15px;
                transition: all 0.3s ease;
            }
            
            .status.idle {
                background: #f8f9fa;
                color: #666;
                border: 2px solid #dee2e6;
            }
            
            .status.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: pulse 2s infinite;
                border: 2px solid #28a745;
            }
            
            .status.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: pulse 1s infinite;
                border: 2px solid #ffc107;
            }
            
            .status.speaking {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                animation: pulse 1.5s infinite;
                border: 2px solid #007bff;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.02); opacity: 0.9; }
                100% { transform: scale(1); opacity: 1; }
            }
            
            .voice-circle {
                width: 180px;
                height: 180px;
                border-radius: 50%;
                margin: 30px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 70px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 4px solid transparent;
            }
            
            .voice-circle.idle {
                background: linear-gradient(45deg, #6c757d, #495057);
                color: white;
            }
            
            .voice-circle.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: listening-pulse 1.5s infinite;
                border-color: #28a745;
            }
            
            .voice-circle.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: processing-spin 2s linear infinite;
                border-color: #ffc107;
            }
            
            .voice-circle.speaking {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                animation: speaking-wave 1s infinite;
                border-color: #007bff;
            }
            
            @keyframes listening-pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            @keyframes processing-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes speaking-wave {
                0%, 100% { transform: scale(1); }
                25% { transform: scale(1.05); }
                50% { transform: scale(1.1); }
                75% { transform: scale(1.05); }
            }
            
            .controls {
                margin: 30px 0;
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 15px 30px;
                font-size: 16px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                min-width: 140px;
            }
            
            .btn.success {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .btn.danger {
                background: linear-gradient(45deg, #dc3545, #c82333);
                color: white;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .conversation {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                max-height: 300px;
                overflow-y: auto;
                text-align: left;
                display: none;
            }
            
            .message {
                margin: 12px 0;
                padding: 15px;
                border-radius: 12px;
                animation: fadeIn 0.3s ease;
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
            
            .debug-info {
                background: #343a40;
                color: #fff;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                font-family: monospace;
                font-size: 14px;
                max-height: 150px;
                overflow-y: auto;
                text-align: left;
                display: none;
            }
            
            .debug-toggle {
                background: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 12px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Working Real-Time Voice Call</h1>
            <p class="subtitle">Complete voice input to AI system</p>
            
            <div class="status idle" id="status">
                Ready for real-time voice call
            </div>
            
            <div class="voice-circle idle" id="voiceCircle" onclick="toggleVoiceCall()">
                📞
            </div>
            
            <div class="controls">
                <button class="btn success" id="startBtn" onclick="startVoiceCall()">
                    🎤 Start Voice Call
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoiceCall()" disabled>
                    📵 End Voice Call
                </button>
            </div>
            
            <button class="debug-toggle" onclick="toggleDebug()">
                🔍 Show Debug Logs
            </button>
            
            <div class="debug-info" id="debugLog">
                Debug information will appear here...
            </div>
            
            <div class="conversation" id="conversation">
                <h4>💬 Real-Time Voice Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let isCallActive = false;
            let recognition = null;
            let currentAudio = null;
            let isProcessing = false;
            
            function debugLog(message) {
                const debugEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                debugEl.innerHTML += `[${timestamp}] ${message}\\n`;
                debugEl.scrollTop = debugEl.scrollHeight;
                console.log(`[DEBUG] ${message}`);
            }
            
            function toggleDebug() {
                const debugEl = document.getElementById('debugLog');
                if (debugEl.style.display === 'none' || !debugEl.style.display) {
                    debugEl.style.display = 'block';
                } else {
                    debugEl.style.display = 'none';
                }
            }
            
            function updateStatus(message, type) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
                debugLog(`Status: ${message} (${type})`);
            }
            
            function updateVoiceCircle(state) {
                const circleEl = document.getElementById('voiceCircle');
                circleEl.className = `voice-circle ${state}`;
                
                switch(state) {
                    case 'idle':
                        circleEl.textContent = '📞';
                        break;
                    case 'listening':
                        circleEl.textContent = '🎤';
                        break;
                    case 'processing':
                        circleEl.textContent = '🧠';
                        break;
                    case 'speaking':
                        circleEl.textContent = '🔊';
                        break;
                }
            }
            
            function toggleVoiceCall() {
                if (isCallActive) {
                    stopVoiceCall();
                } else {
                    startVoiceCall();
                }
            }
            
            function startVoiceCall() {
                debugLog('🎤 Starting voice call...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge.');
                    debugLog('❌ Speech recognition not supported');
                    return;
                }
                
                isCallActive = true;
                isProcessing = false;
                
                // Update UI
                updateStatus('Initializing voice call...', 'processing');
                updateVoiceCircle('processing');
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('conversation').style.display = 'block';
                
                // Initialize speech recognition
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                recognition.maxAlternatives = 1;
                
                debugLog('🔧 Speech recognition configured');
                
                recognition.onstart = function() {
                    debugLog('✅ Speech recognition started');
                    updateStatus('🎤 Listening... Speak now!', 'listening');
                    updateVoiceCircle('listening');
                    isProcessing = false;
                };
                
                recognition.onresult = function(event) {
                    if (isProcessing) {
                        debugLog('⚠️ Already processing, ignoring result');
                        return;
                    }
                    
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    debugLog(`🎤 Voice detected: "${transcript}" (confidence: ${confidence.toFixed(2)})`);
                    
                    if (transcript && confidence > 0.4) {
                        handleVoiceInput(transcript);
                    } else {
                        debugLog('❌ Low confidence or empty transcript, restarting...');
                        if (isCallActive) {
                            setTimeout(() => startListening(), 1000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    debugLog(`❌ Speech recognition error: ${event.error}`);
                    
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied! Please allow microphone access.');
                        stopVoiceCall();
                        return;
                    }
                    
                    if (isCallActive && !isProcessing) {
                        debugLog('🔄 Restarting recognition after error...');
                        setTimeout(() => startListening(), 2000);
                    }
                };
                
                recognition.onend = function() {
                    debugLog('🔚 Speech recognition ended');
                    if (isCallActive && !isProcessing) {
                        debugLog('🔄 Restarting recognition...');
                        setTimeout(() => startListening(), 500);
                    }
                };
                
                // Start listening
                startListening();
                
                // Add welcome message
                setTimeout(() => {
                    addMessage('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
                }, 1000);
            }
            
            function startListening() {
                if (!isCallActive || isProcessing) {
                    debugLog('⚠️ Cannot start listening - call inactive or processing');
                    return;
                }
                
                try {
                    debugLog('🚀 Starting speech recognition...');
                    recognition.start();
                } catch (error) {
                    debugLog(`❌ Failed to start recognition: ${error.message}`);
                    if (isCallActive) {
                        setTimeout(() => startListening(), 1000);
                    }
                }
            }
            
            function stopVoiceCall() {
                debugLog('📵 Stopping voice call...');
                
                isCallActive = false;
                isProcessing = false;
                
                if (recognition) {
                    recognition.stop();
                }
                
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Update UI
                updateStatus('Voice call ended', 'idle');
                updateVoiceCircle('idle');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
            
            async function handleVoiceInput(transcript) {
                if (isProcessing) {
                    debugLog('⚠️ Already processing, ignoring input');
                    return;
                }
                
                isProcessing = true;
                debugLog(`🔄 Processing voice input: "${transcript}"`);
                
                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                    debugLog('🛑 Stopped current audio');
                }
                
                // Add farmer message
                addMessage('farmer', transcript);
                
                // Update status
                updateStatus('🧠 AI is thinking...', 'processing');
                updateVoiceCircle('processing');
                
                try {
                    debugLog('📡 Sending voice input to AI...');
                    
                    const response = await fetch('/api/voice-farming', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    debugLog(`📡 API response status: ${response.status}`);
                    
                    const result = await response.json();
                    debugLog(`📦 API response: ${JSON.stringify(result)}`);
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        debugLog(`✅ AI response received: "${aiResponse}"`);
                        await speakText(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        debugLog(`❌ API error: ${result.response}`);
                        await speakText(errorMsg);
                    }
                } catch (error) {
                    debugLog(`❌ Voice processing error: ${error.message}`);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await speakText(errorMsg);
                }
                
                isProcessing = false;
                debugLog('✅ Voice processing completed');
            }
            
            async function speakText(text) {
                debugLog(`🔊 Starting TTS for: "${text}"`);
                updateStatus('🔊 AI is speaking...', 'speaking');
                updateVoiceCircle('speaking');
                
                try {
                    const response = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    debugLog(`🔊 TTS response status: ${response.status}`);
                    
                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);
                        
                        debugLog('🔊 Playing TTS audio...');
                        
                        currentAudio.onended = function() {
                            debugLog('🔊 TTS audio ended');
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Listening... Speak now!', 'listening');
                                updateVoiceCircle('listening');
                                setTimeout(() => startListening(), 500);
                            }
                        };
                        
                        currentAudio.onerror = function() {
                            debugLog('❌ TTS audio error');
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Listening... Speak now!', 'listening');
                                updateVoiceCircle('listening');
                                setTimeout(() => startListening(), 500);
                            }
                        };
                        
                        await currentAudio.play();
                    } else {
                        throw new Error(`TTS failed with status ${response.status}`);
                    }
                } catch (error) {
                    debugLog(`❌ TTS error: ${error.message}`);
                    if (isCallActive) {
                        updateStatus('🎤 Listening... Speak now!', 'listening');
                        updateVoiceCircle('listening');
                        setTimeout(() => startListening(), 500);
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
                    <div style="font-weight: bold; margin-bottom: 8px; font-size: 14px;">${speakerName}</div>
                    <div style="font-size: 16px; line-height: 1.4;">${text}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 8px;">${timestamp}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
                
                debugLog(`💬 Message added: ${speakerName} - "${text}"`);
            }
            
            // Initialize
            window.onload = function() {
                debugLog('🚀 Working real-time voice call system initialized');
                updateStatus('Ready for real-time voice call', 'idle');
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/voice-farming', methods=['POST'])
def handle_voice_farming_query():
    """Handle voice farming query with detailed logging"""
    print("🎤 VOICE FARMING API CALLED")
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        print(f"👨‍🌾 VOICE INPUT FROM FARMER: {user_query}")
        
        if not user_query:
            print("❌ Empty voice query received")
            return jsonify({"success": False, "response": "Empty query"})
        
        # Get farming response
        print("🤖 Calling AI for voice input...")
        result = get_farming_response(user_query)
        
        response_data = {
            "success": result["success"],
            "response": result["response"],
            "response_time": result.get("response_time", 0),
            "timestamp": datetime.now().isoformat(),
            "input_type": "voice"
        }
        
        print(f"📤 VOICE API RESPONSE: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ VOICE API ERROR: {e}")
        return jsonify({"success": False, "response": str(e)})

@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate TTS audio with logging"""
    print("🔊 TTS API CALLED")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"🔊 TTS TEXT: {text}")
        
        if not text:
            print("❌ Empty TTS text")
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_tts_audio(text)
        
        if audio_file:
            print(f"✅ TTS file generated: {audio_file}")
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            print("❌ TTS generation failed")
            return jsonify({"success": False, "error": "TTS generation failed"})
            
    except Exception as e:
        print(f"❌ TTS API ERROR: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🎤 Starting Working Real-Time Voice Call System...")
    print("🌾 Complete Voice Input to AI with Debug Logging")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5006")
    print("💡 Press Ctrl+C to stop")
    print("\n📊 Server will show detailed logs for:")
    print("   - Voice input detection")
    print("   - API calls to AI")
    print("   - TTS generation")
    print("   - All errors and responses")
    
    app.run(debug=True, host='0.0.0.0', port=5006)
