#!/usr/bin/env python3
"""
Fixed Voice Communication System
Better voice recognition and clear communication
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
    """Get direct farming response"""
    print(f"🌾 Farming query: {query}")
    
    if not api_key:
        return {
            "success": False,
            "response": "API key not configured",
            "response_time": 0
        }
    
    system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसान के सवाल का सीधा और practical जवाब दें।

जवाब देने का तरीका:
- सीधे सवाल का जवाब दें
- 1-2 वाक्य में संक्षिप्त रखें
- व्यावहारिक सलाह दें
- "भाई" या "जी" जैसे friendly words use करें
- कोई उल्टा सवाल न पूछें"""

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
            "max_tokens": 80,
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            
            print(f"🤖 AI response: {ai_response}")
            
            return {
                "success": True,
                "response": ai_response,
                "response_time": response_time,
                "provider": "groq"
            }
        else:
            return {
                "success": False,
                "response": f"API Error: {response.status_code}",
                "response_time": response_time
            }
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "response_time": 0
        }

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
    """Fixed voice communication interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Fixed Voice Communication</title>
        
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: white;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 40px;
                text-align: center;
                color: #333;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            .status {
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
                padding: 20px;
                border-radius: 15px;
                transition: all 0.3s;
            }
            
            .status.idle {
                background: #f8f9fa;
                color: #666;
            }
            
            .status.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: pulse 2s infinite;
            }
            
            .status.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: pulse 1s infinite;
            }
            
            .status.speaking {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }
            
            .voice-btn {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: none;
                font-size: 60px;
                margin: 30px;
                cursor: pointer;
                transition: all 0.3s;
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .voice-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .voice-btn.listening {
                background: linear-gradient(45deg, #dc3545, #c82333);
                animation: pulse 1s infinite;
            }
            
            .controls {
                margin: 30px 0;
            }
            
            .btn {
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 50px;
                margin: 10px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: bold;
            }
            
            .btn.primary {
                background: linear-gradient(45deg, #007bff, #0056b3);
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
            
            .conversation {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                max-height: 400px;
                overflow-y: auto;
                text-align: left;
            }
            
            .message {
                margin: 15px 0;
                padding: 15px;
                border-radius: 15px;
                animation: fadeIn 0.3s;
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
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .text-input {
                margin: 20px 0;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
            }
            
            input[type="text"] {
                width: 70%;
                padding: 15px;
                font-size: 18px;
                border: 2px solid #ddd;
                border-radius: 10px;
                margin-right: 10px;
            }
            
            .instructions {
                background: rgba(0,123,255,0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #007bff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Fixed Voice Communication</h1>
            <p style="font-size: 18px; color: #666;">Clear Voice Communication with AI Farmer Assistant</p>
            
            <div class="status idle" id="status">
                Ready for voice communication
            </div>
            
            <div class="voice-btn" id="voiceBtn" onclick="toggleVoice()">
                🎤
            </div>
            
            <div class="controls">
                <button class="btn primary" onclick="startListening()">
                    🎤 Start Listening
                </button>
                <button class="btn danger" onclick="stopListening()">
                    🛑 Stop Listening
                </button>
            </div>
            
            <div class="text-input">
                <h4>💬 Or Type Your Question:</h4>
                <input type="text" id="textInput" placeholder="Type farming question in Hindi..." onkeypress="handleKeyPress(event)">
                <button class="btn primary" onclick="sendTextQuery()">Send</button>
            </div>
            
            <div class="instructions">
                <h4>📋 Instructions for Better Voice Recognition:</h4>
                <ul style="text-align: left;">
                    <li><strong>Speak Clearly:</strong> धीरे और साफ बोलें</li>
                    <li><strong>Close to Mic:</strong> Microphone के पास आएं</li>
                    <li><strong>Quiet Environment:</strong> Background noise कम रखें</li>
                    <li><strong>Wait for Response:</strong> AI के जवाब का इंतजार करें</li>
                    <li><strong>Short Sentences:</strong> छोटे वाक्य में बोलें</li>
                </ul>
            </div>
            
            <div class="conversation" id="conversation" style="display: none;">
                <h4>💬 Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let isListening = false;
            let recognition = null;
            let currentAudio = null;
            
            function initializeVoiceRecognition() {
                if ('webkitSpeechRecognition' in window) {
                    recognition = new webkitSpeechRecognition();
                    recognition.continuous = false;  // Single recognition
                    recognition.interimResults = false;  // Only final results
                    recognition.lang = 'hi-IN';
                    recognition.maxAlternatives = 1;
                    
                    recognition.onstart = function() {
                        console.log('🎤 Voice recognition started');
                        updateStatus('Listening... Speak now!', 'listening');
                        document.getElementById('voiceBtn').classList.add('listening');
                    };
                    
                    recognition.onresult = function(event) {
                        const transcript = event.results[0][0].transcript.trim();
                        const confidence = event.results[0][0].confidence;
                        
                        console.log('🎤 Voice input:', transcript, 'Confidence:', confidence);
                        
                        if (transcript && confidence > 0.3) {  // Minimum confidence
                            handleVoiceInput(transcript);
                        } else {
                            updateStatus('Please speak more clearly', 'idle');
                            document.getElementById('voiceBtn').classList.remove('listening');
                        }
                    };
                    
                    recognition.onerror = function(event) {
                        console.error('🎤 Recognition error:', event.error);
                        updateStatus('Voice recognition error. Try again.', 'idle');
                        document.getElementById('voiceBtn').classList.remove('listening');
                        isListening = false;
                    };
                    
                    recognition.onend = function() {
                        console.log('🎤 Recognition ended');
                        document.getElementById('voiceBtn').classList.remove('listening');
                        isListening = false;
                    };
                    
                    return true;
                } else {
                    alert('Voice recognition not supported. Please use Chrome or Edge.');
                    return false;
                }
            }
            
            function toggleVoice() {
                if (isListening) {
                    stopListening();
                } else {
                    startListening();
                }
            }
            
            function startListening() {
                if (!recognition && !initializeVoiceRecognition()) {
                    return;
                }
                
                if (isListening) {
                    console.log('Already listening');
                    return;
                }
                
                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                isListening = true;
                document.getElementById('conversation').style.display = 'block';
                
                try {
                    recognition.start();
                } catch (error) {
                    console.error('Failed to start recognition:', error);
                    isListening = false;
                }
            }
            
            function stopListening() {
                if (recognition && isListening) {
                    recognition.stop();
                }
                isListening = false;
                updateStatus('Listening stopped', 'idle');
                document.getElementById('voiceBtn').classList.remove('listening');
            }
            
            async function handleVoiceInput(transcript) {
                console.log('🔄 Processing voice input:', transcript);
                
                // Add farmer message
                addMessage('farmer', transcript);
                
                // Update status
                updateStatus('AI is thinking...', 'processing');
                
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
            }
            
            async function sendTextQuery() {
                const query = document.getElementById('textInput').value.trim();
                if (!query) return;
                
                console.log('💬 Text query:', query);
                document.getElementById('textInput').value = '';
                document.getElementById('conversation').style.display = 'block';
                
                // Add farmer message
                addMessage('farmer', query);
                
                // Update status
                updateStatus('AI is thinking...', 'processing');
                
                try {
                    const response = await fetch('/api/farming', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        await speakText(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        updateStatus('Ready for next question', 'idle');
                    }
                } catch (error) {
                    console.error('❌ Text processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    updateStatus('Ready for next question', 'idle');
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendTextQuery();
                }
            }
            
            async function speakText(text) {
                console.log('🔊 AI speaking:', text);
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
                            currentAudio = null;
                            updateStatus('Ready for next question', 'idle');
                        };
                        
                        await currentAudio.play();
                    } else {
                        updateStatus('Ready for next question', 'idle');
                    }
                } catch (error) {
                    console.error('🔊 TTS error:', error);
                    updateStatus('Ready for next question', 'idle');
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
                
                const speakerName = speaker === 'farmer' ? '👨‍🌾 आप' : '🤖 AI सलाहकार';
                const timestamp = new Date().toLocaleTimeString('hi-IN');
                
                messageEl.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 8px;">${speakerName}</div>
                    <div style="font-size: 18px; line-height: 1.4;">${text}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 8px;">${timestamp}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            console.log('🎤 Fixed voice communication system ready');
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
        
        print(f"👨‍🌾 Farmer question: {user_query}")
        
        if not user_query:
            return jsonify({"success": False, "error": "Empty query"})
        
        # Get farming response
        result = get_farming_response(user_query)
        
        return jsonify({
            "success": result["success"],
            "response": result["response"],
            "response_time": result["response_time"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Farming API error: {e}")
        return jsonify({"success": False, "error": str(e)})

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
    print("🔧 Starting Fixed Voice Communication System...")
    print("🌾 Clear Communication with AI Farmer Assistant")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5003")
    print("💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
