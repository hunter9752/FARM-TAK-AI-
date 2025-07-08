#!/usr/bin/env python3
"""
Simple Flask Server for Farmer Assistant
Quick start server for testing
"""

import os
import sys
import json
import time
import tempfile
from datetime import datetime

# Try to import Flask
try:
    from flask import Flask, render_template, request, jsonify, send_file
    print("✅ Flask imported successfully")
except ImportError:
    print("❌ Installing Flask...")
    os.system("pip install flask flask-cors requests gtts")
    from flask import Flask, render_template, request, jsonify, send_file

try:
    from flask_cors import CORS
    print("✅ CORS imported successfully")
except ImportError:
    print("❌ Installing CORS...")
    os.system("pip install flask-cors")
    from flask_cors import CORS

import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
session_stats = {
    "total_queries": 0,
    "successful_responses": 0,
    "start_time": datetime.now()
}

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
    print(f"🔑 API key available: {api_key is not None}")

    if not api_key:
        print("❌ No API key configured")
        return {
            "success": False,
            "response": "API key not configured",
            "response_time": 0
        }
    
    system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

जवाब हमेशा:
- हिंदी में दें
- 3-4 वाक्यों में संक्षिप्त हो
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
            "max_tokens": 200,
            "stream": False
        }

        print(f"🌐 Making API call to: {url}")
        print(f"📝 Payload: {payload}")

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time

        print(f"📡 API response status: {response.status_code}")
        print(f"⏱️ Response time: {response_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            return {
                "success": True,
                "response": llm_response,
                "response_time": response_time,
                "provider": "groq"
            }
        else:
            return {
                "success": False,
                "response": f"API Error: {response.status_code}",
                "response_time": response_time,
                "provider": "groq"
            }
            
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "response_time": 0,
            "provider": "groq"
        }

def generate_tts_audio(text):
    """Generate TTS audio"""
    try:
        from gtts import gTTS
        
        # Create TTS
        tts = gTTS(text=text, lang="hi", slow=False)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        
        return temp_file.name
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Main page"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌾 Farmer Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            h1 { color: #2e7d32; text-align: center; }
            .input-section { margin: 20px 0; }
            input[type="text"] { width: 70%; padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; }
            button { padding: 15px 25px; font-size: 16px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; margin-left: 10px; }
            button:hover { background: #45a049; }
            .response { margin: 20px 0; padding: 20px; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #4caf50; }
            .loading { display: none; text-align: center; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌾 Farmer Assistant</h1>
            <p style="text-align: center; color: #666;">AI-Powered Farming Guidance | Hindi + English Support</p>
            
            <div class="input-section">
                <input type="text" id="queryInput" placeholder="अपना सवाल यहाँ लिखें... (जैसे: गेहूं के लिए खाद की सलाह)" onkeypress="handleKeyPress(event)">
                <button onclick="sendQuery()">भेजें</button>
                <button onclick="playAudio()" id="audioBtn" style="display: none; background: #2196f3;">🔊 सुनें</button>
            </div>
            
            <div class="loading" id="loading">🤖 AI सोच रहा है...</div>
            <div class="response" id="response" style="display: none;"></div>
            
            <div style="margin-top: 30px; text-align: center;">
                <h3>Quick Examples:</h3>
                <button onclick="askExample('गेहूं के लिए खाद की सलाह दो')" style="margin: 5px;">गेहूं खाद</button>
                <button onclick="askExample('फसल में कीड़े लग गए हैं')" style="margin: 5px;">कीड़े समस्या</button>
                <button onclick="askExample('आज मंडी भाव क्या है')" style="margin: 5px;">मंडी भाव</button>
                <button onclick="askExample('बीज कब बोना चाहिए')" style="margin: 5px;">बुआई समय</button>
            </div>
            
            <div style="margin-top: 30px; text-align: center;">
                <a href="/realtime" style="background: #ff5722; color: white; padding: 15px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    🎤 Real-Time Voice Call
                </a>
            </div>
        </div>
        
        <script>
            let currentAudio = null;
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendQuery();
                }
            }
            
            function askExample(query) {
                document.getElementById('queryInput').value = query;
                sendQuery();
            }
            
            async function sendQuery() {
                const query = document.getElementById('queryInput').value.trim();
                if (!query) return;

                console.log('🔄 Sending query:', query);

                document.getElementById('loading').style.display = 'block';
                document.getElementById('response').style.display = 'none';
                document.getElementById('audioBtn').style.display = 'none';

                try {
                    console.log('📡 Making API call...');
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    console.log('📡 Response status:', response.status);
                    const result = await response.json();
                    console.log('📦 Response data:', result);
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (result.success) {
                        document.getElementById('response').innerHTML = 
                            `<strong>🤖 AI सलाहकार:</strong><br>${result.llm_result.response}<br>
                            <small style="color: #666;">⏱️ ${result.llm_result.response_time.toFixed(2)}s</small>`;
                        document.getElementById('response').style.display = 'block';
                        document.getElementById('audioBtn').style.display = 'inline-block';
                        
                        // Store response for audio
                        window.currentResponse = result.llm_result.response;
                    } else {
                        document.getElementById('response').innerHTML = 
                            '<strong>❌ Error:</strong> माफ करें, कुछ गलती हुई है।';
                        document.getElementById('response').style.display = 'block';
                    }
                    
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('response').innerHTML = 
                        '<strong>❌ Network Error:</strong> कृपया दोबारा कोशिश करें।';
                    document.getElementById('response').style.display = 'block';
                }
            }
            
            async function playAudio() {
                if (!window.currentResponse) return;
                
                try {
                    const response = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: window.currentResponse })
                    });
                    
                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        if (currentAudio) {
                            currentAudio.pause();
                        }
                        
                        currentAudio = new Audio(audioUrl);
                        currentAudio.play();
                    }
                } catch (error) {
                    console.error('Audio error:', error);
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/realtime')
def realtime():
    """Real-time voice call page"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Real-Time Voice Call - Farmer Assistant</title>

        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                margin: 0;
                padding: 0;
                color: white;
            }

            .call-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }

            .call-interface {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 100%;
                color: #333;
            }

            .call-status {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
                color: #2c3e50;
            }

            .call-status.listening {
                color: #27ae60;
                animation: pulse 2s infinite;
            }

            .call-status.speaking {
                color: #3498db;
                animation: pulse 2s infinite;
            }

            .call-status.processing {
                color: #f39c12;
                animation: pulse 1s infinite;
            }

            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.6; }
                100% { opacity: 1; }
            }

            .voice-visualizer {
                width: 200px;
                height: 200px;
                border-radius: 50%;
                margin: 30px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 60px;
                transition: all 0.3s ease;
            }

            .voice-visualizer.idle {
                background: linear-gradient(45deg, #bdc3c7, #95a5a6);
                color: white;
            }

            .voice-visualizer.listening {
                background: linear-gradient(45deg, #27ae60, #2ecc71);
                color: white;
                animation: listening-pulse 1.5s infinite;
            }

            .voice-visualizer.speaking {
                background: linear-gradient(45deg, #3498db, #5dade2);
                color: white;
                animation: speaking-pulse 1s infinite;
            }

            .voice-visualizer.processing {
                background: linear-gradient(45deg, #f39c12, #f4d03f);
                color: white;
                animation: processing-spin 2s linear infinite;
            }

            @keyframes listening-pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            @keyframes speaking-pulse {
                0% { transform: scale(1); }
                25% { transform: scale(1.05); }
                50% { transform: scale(1.1); }
                75% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }

            @keyframes processing-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .call-controls {
                margin-top: 30px;
            }

            .call-btn {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: none;
                font-size: 30px;
                margin: 0 15px;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .call-btn.start {
                background: linear-gradient(45deg, #27ae60, #2ecc71);
                color: white;
            }

            .call-btn.end {
                background: linear-gradient(45deg, #e74c3c, #c0392b);
                color: white;
            }

            .call-btn.mute {
                background: linear-gradient(45deg, #f39c12, #e67e22);
                color: white;
            }

            .call-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }

            .call-btn:active {
                transform: scale(0.95);
            }

            .conversation-log {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin-top: 30px;
                max-height: 300px;
                overflow-y: auto;
                text-align: left;
                color: #333;
            }

            .conversation-item {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 10px;
            }

            .conversation-item.user {
                background: #e3f2fd;
                margin-left: 20px;
            }

            .conversation-item.ai {
                background: #e8f5e8;
                margin-right: 20px;
            }

            .conversation-item .speaker {
                font-weight: 600;
                margin-bottom: 5px;
            }

            .conversation-item .timestamp {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }

            .interruption-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: 600;
                display: none;
                animation: shake 0.5s;
            }

            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }

            .back-link {
                position: fixed;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
            }

            .back-link:hover {
                background: rgba(255,255,255,0.3);
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-link">← Back to Main</a>

        <div class="call-container">
            <div class="call-interface">
                <h2>🎤 Real-Time Voice Call</h2>
                <div class="call-status" id="callStatus">कॉल शुरू करने के लिए तैयार</div>

                <div class="voice-visualizer idle" id="voiceVisualizer">
                    <span style="font-size: 60px;">📞</span>
                </div>

                <div class="call-controls">
                    <button class="call-btn start" id="startCallBtn" onclick="startCall()">
                        📞
                    </button>
                    <button class="call-btn mute" id="muteBtn" onclick="toggleMute()" style="display: none;">
                        🎤
                    </button>
                    <button class="call-btn end" id="endCallBtn" onclick="endCall()" style="display: none;">
                        📵
                    </button>
                </div>

                <div style="margin-top: 20px; font-size: 14px; color: #666;">
                    <p><strong>Instructions:</strong></p>
                    <p>1. Click phone button to start call</p>
                    <p>2. Allow microphone access</p>
                    <p>3. Speak your farming questions</p>
                    <p>4. Interrupt AI anytime by speaking</p>
                </div>
            </div>

            <div class="conversation-log" id="conversationLog" style="display: none;">
                <h5>💬 Conversation</h5>
                <div id="conversationItems"></div>
            </div>
        </div>

        <div class="interruption-indicator" id="interruptionIndicator">
            🛑 Previous response stopped
        </div>

        <script>
            // Real-time voice call system
            let isCallActive = false;
            let isListening = false;
            let isSpeaking = false;
            let isMuted = false;
            let recognition = null;
            let currentAudio = null;
            let conversationHistory = [];
            let interruptionCount = 0;

            // Initialize speech recognition
            function initializeSpeechRecognition() {
                if ('webkitSpeechRecognition' in window) {
                    recognition = new webkitSpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'hi-IN';

                    recognition.onstart = function() {
                        console.log('🎤 Voice recognition started');
                        isListening = true;
                        updateCallStatus('सुन रहा हूं... बोलिए', 'listening');
                        updateVisualizer('listening');
                    };

                    recognition.onresult = function(event) {
                        let finalTranscript = '';

                        for (let i = event.resultIndex; i < event.results.length; i++) {
                            const transcript = event.results[i][0].transcript;
                            if (event.results[i].isFinal) {
                                finalTranscript += transcript;
                            }
                        }

                        if (finalTranscript.trim()) {
                            handleVoiceInput(finalTranscript.trim());
                        }
                    };

                    recognition.onerror = function(event) {
                        console.error('Speech recognition error:', event.error);
                        if (isCallActive && !isMuted) {
                            setTimeout(() => {
                                if (isCallActive) {
                                    startListening();
                                }
                            }, 1000);
                        }
                    };

                    recognition.onend = function() {
                        isListening = false;
                        if (isCallActive && !isMuted) {
                            setTimeout(() => {
                                if (isCallActive) {
                                    startListening();
                                }
                            }, 100);
                        }
                    };

                    return true;
                } else {
                    alert('Voice recognition not supported in this browser. Please use Chrome or Edge.');
                    return false;
                }
            }

            function startCall() {
                if (!initializeSpeechRecognition()) return;

                isCallActive = true;
                interruptionCount = 0;
                conversationHistory = [];

                updateCallStatus('कॉल शुरू हो गई - बोलना शुरू करें', 'listening');
                updateVisualizer('listening');

                // Show/hide buttons
                document.getElementById('startCallBtn').style.display = 'none';
                document.getElementById('muteBtn').style.display = 'inline-block';
                document.getElementById('endCallBtn').style.display = 'inline-block';
                document.getElementById('conversationLog').style.display = 'block';

                // Start continuous listening
                startListening();

                // Add welcome message
                addConversationItem('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
            }

            function endCall() {
                isCallActive = false;
                isListening = false;
                isSpeaking = false;

                // Stop recognition
                if (recognition) {
                    recognition.stop();
                }

                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }

                updateCallStatus('कॉल समाप्त', 'idle');
                updateVisualizer('idle');

                // Show/hide buttons
                document.getElementById('startCallBtn').style.display = 'inline-block';
                document.getElementById('muteBtn').style.display = 'none';
                document.getElementById('endCallBtn').style.display = 'none';
            }

            function toggleMute() {
                isMuted = !isMuted;
                const muteBtn = document.getElementById('muteBtn');

                if (isMuted) {
                    if (recognition) recognition.stop();
                    muteBtn.innerHTML = '🔇';
                    muteBtn.style.background = 'linear-gradient(45deg, #e74c3c, #c0392b)';
                    updateCallStatus('Muted - बोलना बंद', 'idle');
                    updateVisualizer('idle');
                } else {
                    muteBtn.innerHTML = '🎤';
                    muteBtn.style.background = 'linear-gradient(45deg, #f39c12, #e67e22)';
                    startListening();
                }
            }

            function startListening() {
                if (!isCallActive || isMuted || isListening) return;

                if (recognition) {
                    try {
                        recognition.start();
                    } catch (error) {
                        console.error('Failed to start recognition:', error);
                        setTimeout(() => {
                            if (isCallActive && !isMuted) {
                                startListening();
                            }
                        }, 1000);
                    }
                }
            }

            function handleVoiceInput(transcript) {
                console.log('🎤 Voice input:', transcript);

                // Stop current audio if speaking (interruption)
                if (isSpeaking && currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                    isSpeaking = false;
                    interruptionCount++;
                    showInterruptionIndicator();
                }

                // Add user message to conversation
                addConversationItem('user', transcript);

                // Stop listening temporarily
                if (recognition) recognition.stop();

                // Process the query
                processVoiceQuery(transcript);
            }

            async function processVoiceQuery(query) {
                console.log('🎤 Processing voice query:', query);
                updateCallStatus('सोच रहा हूं...', 'processing');
                updateVisualizer('processing');

                try {
                    console.log('📡 Making voice API call...');
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: query })
                    });

                    console.log('📡 Voice response status:', response.status);
                    const result = await response.json();
                    console.log('📦 Voice response data:', result);

                    if (result.success) {
                        const aiResponse = result.llm_result.response;

                        // Add AI response to conversation
                        addConversationItem('ai', aiResponse);

                        // Generate and play TTS
                        await generateAndPlayTTS(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है। कृपया दोबारा कोशिश करें।';
                        addConversationItem('ai', errorMsg);
                        await generateAndPlayTTS(errorMsg);
                    }

                } catch (error) {
                    console.error('Query processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है। कृपया दोबारा कोशिश करें।';
                    addConversationItem('ai', errorMsg);
                    await generateAndPlayTTS(errorMsg);
                }
            }

            async function generateAndPlayTTS(text) {
                updateCallStatus('जवाब दे रहा हूं...', 'speaking');
                updateVisualizer('speaking');
                isSpeaking = true;

                try {
                    const response = await fetch('/api/tts', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: text })
                    });

                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);

                        currentAudio.onended = function() {
                            isSpeaking = false;
                            currentAudio = null;

                            // Resume listening if call is still active
                            if (isCallActive && !isMuted) {
                                setTimeout(() => {
                                    startListening();
                                }, 500);
                            }
                        };

                        currentAudio.onerror = function() {
                            isSpeaking = false;
                            currentAudio = null;
                            if (isCallActive && !isMuted) {
                                startListening();
                            }
                        };

                        await currentAudio.play();
                    } else {
                        throw new Error('TTS generation failed');
                    }

                } catch (error) {
                    console.error('TTS error:', error);
                    isSpeaking = false;
                    if (isCallActive && !isMuted) {
                        startListening();
                    }
                }
            }

            function updateCallStatus(status, type) {
                const statusElement = document.getElementById('callStatus');
                statusElement.textContent = status;
                statusElement.className = `call-status ${type}`;
            }

            function updateVisualizer(state) {
                const visualizer = document.getElementById('voiceVisualizer');
                visualizer.className = `voice-visualizer ${state}`;

                switch(state) {
                    case 'idle':
                        visualizer.innerHTML = '<span style="font-size: 60px;">📞</span>';
                        break;
                    case 'listening':
                        visualizer.innerHTML = '<span style="font-size: 60px;">🎤</span>';
                        break;
                    case 'speaking':
                        visualizer.innerHTML = '<span style="font-size: 60px;">🔊</span>';
                        break;
                    case 'processing':
                        visualizer.innerHTML = '<span style="font-size: 60px;">🧠</span>';
                        break;
                }
            }

            function addConversationItem(speaker, text) {
                const conversationItems = document.getElementById('conversationItems');
                const item = document.createElement('div');
                item.className = `conversation-item ${speaker}`;

                const speakerName = speaker === 'user' ? '👨‍🌾 आप' : '🤖 AI सलाहकार';
                const timestamp = new Date().toLocaleTimeString('hi-IN');

                item.innerHTML = `
                    <div class="speaker">${speakerName}</div>
                    <div class="text">${text}</div>
                    <div class="timestamp">${timestamp}</div>
                `;

                conversationItems.appendChild(item);
                conversationItems.scrollTop = conversationItems.scrollHeight;

                // Store in history
                conversationHistory.push({
                    speaker: speaker,
                    text: text,
                    timestamp: timestamp
                });
            }

            function showInterruptionIndicator() {
                const indicator = document.getElementById('interruptionIndicator');
                indicator.style.display = 'block';
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 2000);
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process query API"""
    try:
        print("🔄 API Query received")
        data = request.get_json()
        user_query = data.get('query', '').strip()

        print(f"📝 User query: {user_query}")

        if not user_query:
            print("❌ Empty query received")
            return jsonify({"success": False, "error": "Empty query"})

        # Get LLM response
        print("🤖 Calling LLM...")
        llm_result = get_llm_response(user_query)
        print(f"✅ LLM result: {llm_result}")

        # Update stats
        session_stats["total_queries"] += 1
        if llm_result["success"]:
            session_stats["successful_responses"] += 1

        result = {
            "success": True,
            "user_query": user_query,
            "llm_result": llm_result,
            "timestamp": datetime.now().isoformat()
        }

        print(f"📤 Sending response: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate TTS audio API"""
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

@app.route('/api/stats')
def get_stats():
    """Get session statistics"""
    uptime = datetime.now() - session_stats["start_time"]
    success_rate = 0
    
    if session_stats["total_queries"] > 0:
        success_rate = (session_stats["successful_responses"] / session_stats["total_queries"]) * 100
    
    return jsonify({
        "total_queries": session_stats["total_queries"],
        "successful_responses": session_stats["successful_responses"],
        "success_rate": success_rate,
        "uptime": str(uptime),
        "llm_available": api_key is not None
    })

if __name__ == '__main__':
    print("🌐 Starting Simple Farmer Assistant Website...")
    print("🌾 Complete AI-Powered Farming Guidance")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found - limited functionality")
    
    print("\n🚀 Starting web server...")
    print("🌐 Website URL: http://localhost:5000")
    print("💡 Press Ctrl+C to stop server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
