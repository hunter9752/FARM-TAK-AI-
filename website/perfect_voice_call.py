#!/usr/bin/env python3
"""
Perfect Working Voice Call System
Real phone call experience with proper voice recognition
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
    print(f"🌾 Processing: {query}")
    
    if not api_key:
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
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ Response: {ai_response}")
            
            return {
                "success": True,
                "response": ai_response,
                "response_time": response_time
            }
        else:
            return {"success": False, "response": f"API Error: {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "response": f"Error: {str(e)}"}

def generate_tts_audio(text):
    """Generate TTS audio"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

@app.route('/')
def index():
    """Perfect voice call interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Perfect Voice Call System</title>
        
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
                box-shadow: 0 30px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 90%;
            }
            
            .phone-header {
                margin-bottom: 30px;
            }
            
            .phone-header h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .phone-header p {
                color: #666;
                font-size: 16px;
            }
            
            .call-status {
                font-size: 22px;
                font-weight: bold;
                margin: 25px 0;
                padding: 20px;
                border-radius: 15px;
                transition: all 0.3s ease;
            }
            
            .call-status.idle {
                background: #f8f9fa;
                color: #666;
                border: 2px solid #dee2e6;
            }
            
            .call-status.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: pulse 2s infinite;
                border: 2px solid #28a745;
            }
            
            .call-status.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: pulse 1s infinite;
                border: 2px solid #ffc107;
            }
            
            .call-status.speaking {
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
            
            .voice-circle:hover {
                transform: scale(1.05);
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .controls {
                margin: 30px 0;
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 12px 25px;
                font-size: 16px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                min-width: 120px;
            }
            
            .btn.primary {
                background: linear-gradient(45deg, #007bff, #0056b3);
                color: white;
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
            
            .test-section {
                margin: 30px 0;
                padding: 20px;
                background: rgba(0,123,255,0.1);
                border-radius: 15px;
                border-left: 4px solid #007bff;
            }
            
            .test-section h4 {
                margin-bottom: 15px;
                color: #007bff;
            }
            
            .test-input {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }
            
            input[type="text"] {
                flex: 1;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                min-width: 200px;
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
                padding: 12px;
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
            
            .instructions {
                background: rgba(255,193,7,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
                text-align: left;
            }
            
            .instructions h4 {
                color: #856404;
                margin-bottom: 10px;
            }
            
            .instructions ul {
                color: #856404;
                padding-left: 20px;
            }
            
            .instructions li {
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <div class="phone-container">
            <div class="phone-header">
                <h1>📞 Perfect Voice Call</h1>
                <p>Real-time AI Farmer Assistant</p>
            </div>
            
            <div class="call-status idle" id="status">
                Ready for voice call
            </div>
            
            <div class="voice-circle idle" id="voiceCircle" onclick="handleVoiceClick()">
                📞
            </div>
            
            <div class="controls">
                <button class="btn success" id="startBtn" onclick="startVoiceCall()">
                    🎤 Start Call
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoiceCall()" disabled>
                    📵 End Call
                </button>
            </div>
            
            <div class="test-section">
                <h4>🧪 Test with Text First:</h4>
                <div class="test-input">
                    <input type="text" id="testInput" placeholder="Type: गेहूं के लिए खाद की सलाह दो" onkeypress="handleKeyPress(event)">
                    <button class="btn primary" onclick="testAPI()">Test</button>
                </div>
                <div id="testResult"></div>
            </div>
            
            <div class="instructions">
                <h4>📋 Voice Call Instructions:</h4>
                <ul>
                    <li><strong>Step 1:</strong> Test with text first to check API</li>
                    <li><strong>Step 2:</strong> Click "Start Call" button</li>
                    <li><strong>Step 3:</strong> Allow microphone access</li>
                    <li><strong>Step 4:</strong> Speak clearly when status shows "Listening"</li>
                    <li><strong>Step 5:</strong> Wait for AI response</li>
                </ul>
            </div>
            
            <div class="conversation" id="conversation">
                <h4>💬 Voice Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let isCallActive = false;
            let recognition = null;
            let currentAudio = null;
            let isProcessing = false;
            
            // Test API first
            async function testAPI() {
                const query = document.getElementById('testInput').value.trim();
                if (!query) {
                    document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                    return;
                }
                
                console.log('🧪 Testing API:', query);
                document.getElementById('testResult').innerHTML = '<div style="color: #007bff;">🔄 Testing API...</div>';
                
                try {
                    const response = await fetch('/api/farming', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 10px; border-radius: 8px; color: #155724; margin-top: 10px;">
                                <strong>✅ API Working!</strong><br>
                                Response: ${result.response}<br>
                                <small>Time: ${result.response_time.toFixed(2)}s</small>
                            </div>`;
                        
                        // Enable voice call
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('startBtn').textContent = '🎤 Start Voice Call';
                    } else {
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 8px; color: #721c24; margin-top: 10px;">
                                <strong>❌ API Error:</strong> ${result.response}
                            </div>`;
                    }
                } catch (error) {
                    document.getElementById('testResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 8px; color: #721c24; margin-top: 10px;">
                            <strong>❌ Network Error:</strong> ${error.message}
                        </div>`;
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    testAPI();
                }
            }
            
            function handleVoiceClick() {
                if (isCallActive) {
                    stopVoiceCall();
                } else {
                    startVoiceCall();
                }
            }
            
            function startVoiceCall() {
                console.log('📞 Starting voice call...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported!\\n\\nPlease use:\\n• Chrome browser\\n• Edge browser\\n• Allow microphone access');
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
                
                recognition.onstart = function() {
                    console.log('🎤 Voice recognition started');
                    updateStatus('🎤 Listening... Speak now!', 'listening');
                    updateVoiceCircle('listening');
                    isProcessing = false;
                };
                
                recognition.onresult = function(event) {
                    if (isProcessing) return;
                    
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    console.log('🎤 Voice detected:', transcript, 'Confidence:', confidence);
                    
                    if (transcript && confidence > 0.4) {
                        handleVoiceInput(transcript);
                    } else {
                        console.log('❌ Low confidence, restarting...');
                        if (isCallActive) {
                            setTimeout(() => startListening(), 1000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('🎤 Recognition error:', event.error);
                    
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied!\\n\\nPlease:\\n1. Allow microphone access\\n2. Refresh the page\\n3. Try again');
                        stopVoiceCall();
                        return;
                    }
                    
                    if (isCallActive && !isProcessing) {
                        setTimeout(() => startListening(), 2000);
                    }
                };
                
                recognition.onend = function() {
                    console.log('🎤 Recognition ended');
                    if (isCallActive && !isProcessing) {
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
                if (!isCallActive || isProcessing) return;
                
                try {
                    recognition.start();
                } catch (error) {
                    console.error('Failed to start recognition:', error);
                    if (isCallActive) {
                        setTimeout(() => startListening(), 1000);
                    }
                }
            }
            
            function stopVoiceCall() {
                console.log('📵 Stopping voice call...');
                
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
                updateStatus('Call ended', 'idle');
                updateVoiceCircle('idle');
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
            
            async function handleVoiceInput(transcript) {
                if (isProcessing) return;
                
                isProcessing = true;
                console.log('🔄 Processing voice input:', transcript);
                
                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Add farmer message
                addMessage('farmer', transcript);
                
                // Update status
                updateStatus('🧠 AI is thinking...', 'processing');
                updateVoiceCircle('processing');
                
                try {
                    const response = await fetch('/api/farming', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        await speakText(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await speakText(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Voice processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await speakText(errorMsg);
                }
                
                isProcessing = false;
            }
            
            async function speakText(text) {
                console.log('🔊 AI speaking:', text);
                updateStatus('🔊 AI is speaking...', 'speaking');
                updateVoiceCircle('speaking');
                
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
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Listening... Speak now!', 'listening');
                                updateVoiceCircle('listening');
                                setTimeout(() => startListening(), 500);
                            }
                        };
                        
                        currentAudio.onerror = function() {
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Listening... Speak now!', 'listening');
                                updateVoiceCircle('listening');
                                setTimeout(() => startListening(), 500);
                            }
                        };
                        
                        await currentAudio.play();
                    } else {
                        throw new Error('TTS failed');
                    }
                } catch (error) {
                    console.error('🔊 TTS error:', error);
                    if (isCallActive) {
                        updateStatus('🎤 Listening... Speak now!', 'listening');
                        updateVoiceCircle('listening');
                        setTimeout(() => startListening(), 500);
                    }
                }
            }
            
            function updateStatus(message, type) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `call-status ${type}`;
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
            }
            
            // Initialize
            console.log('📞 Perfect voice call system ready');
            
            // Auto-test API on load
            setTimeout(() => {
                document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                testAPI();
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/api/farming', methods=['POST'])
def handle_farming_query():
    """Handle farming query"""
    print("🌾 Farming API called")
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        print(f"👨‍🌾 Farmer: {user_query}")
        
        if not user_query:
            return jsonify({"success": False, "response": "Empty query"})
        
        # Get farming response
        result = get_farming_response(user_query)
        
        return jsonify({
            "success": result["success"],
            "response": result["response"],
            "response_time": result.get("response_time", 0),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({"success": False, "response": str(e)})

@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate TTS audio"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_tts_audio(text)
        
        if audio_file:
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            return jsonify({"success": False, "error": "TTS generation failed"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("📞 Starting Perfect Voice Call System...")
    print("🌾 Real Phone Call Experience for Farmers")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5004")
    print("💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5004)
