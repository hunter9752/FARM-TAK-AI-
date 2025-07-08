#!/usr/bin/env python3
"""
🌾 FINAL FARMER VOICE AGENT 🌾
Complete Real-Time Voice Call System for Farmers
Production Ready - All Tests Passed
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
    print(f"✅ API Key: {'READY' if GROQ_API_KEY else 'MISSING'}")
except Exception as e:
    print(f"❌ API key error: {e}")

def get_farming_advice(query):
    """Get expert farming advice from AI"""
    print(f"🌾 Farmer Query: {query}")
    
    if not GROQ_API_KEY:
        return "API key की समस्या है, भाई।"
    
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
                    "content": """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। 

जवाब देने का तरीका:
- हिंदी में स्पष्ट जवाब दें
- 2-3 वाक्य में practical सलाह दें
- "भाई" या "जी" का प्रयोग करें
- बिल्कुल phone call की तरह बात करें
- व्यावहारिक और actionable advice दें

विषय expertise:
- फसल की खेती (गेहूं, धान, मक्का, सब्जी)
- खाद और उर्वरक
- कीट-पतंग नियंत्रण
- सिंचाई और पानी प्रबंधन
- मंडी भाव और बिक्री
- मिट्टी की जांच"""
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ AI Response: {ai_response}")
            return ai_response
        else:
            print(f"❌ API Error: {response.status_code}")
            return "AI में कुछ समस्या है, भाई। फिर से कोशिश करें।"
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "नेटवर्क की समस्या है, भाई। कनेक्शन चेक करें।"

def generate_hindi_voice(text):
    """Generate Hindi voice from text"""
    print(f"🔊 Generating voice: {text[:50]}...")
    
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        print(f"✅ Voice generated: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"❌ Voice generation error: {e}")
        return None

@app.route('/')
def index():
    """Final Farmer Voice Agent Interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌾 Farmer Voice Agent - AI कृषि सलाहकार</title>
        
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2E8B57 0%, #228B22 50%, #32CD32 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                overflow-x: hidden;
            }
            
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                padding: 40px;
                text-align: center;
                color: #2c3e50;
                max-width: 600px;
                width: 90%;
                box-shadow: 0 30px 60px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }
            
            .main-container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(46, 139, 87, 0.1), transparent);
                transform: rotate(45deg);
                animation: shine 4s infinite;
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
            }
            
            .header {
                position: relative;
                z-index: 1;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 32px;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #2E8B57, #228B22);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p {
                color: #666;
                font-size: 18px;
            }
            
            .call-interface {
                position: relative;
                z-index: 1;
                margin: 30px 0;
            }
            
            .call-status {
                font-size: 22px;
                font-weight: bold;
                margin: 25px 0;
                padding: 20px;
                border-radius: 15px;
                background: #f8f9fa;
                color: #495057;
                transition: all 0.3s ease;
                border: 2px solid #e9ecef;
            }
            
            .call-status.connected {
                background: linear-gradient(45deg, #d4edda, #c3e6cb);
                color: #155724;
                border-color: #28a745;
                animation: connectedPulse 2s infinite;
            }
            
            .call-status.listening {
                background: linear-gradient(45deg, #cce5ff, #b3d9ff);
                color: #004085;
                border-color: #007bff;
                animation: listeningWave 1.5s infinite;
            }
            
            .call-status.speaking {
                background: linear-gradient(45deg, #fff3cd, #ffeaa7);
                color: #856404;
                border-color: #ffc107;
                animation: speakingBounce 1s infinite;
            }
            
            @keyframes connectedPulse {
                0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
                50% { transform: scale(1.02); box-shadow: 0 0 0 20px rgba(40, 167, 69, 0); }
            }
            
            @keyframes listeningWave {
                0%, 100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); }
                50% { box-shadow: 0 0 0 25px rgba(0, 123, 255, 0); }
            }
            
            @keyframes speakingBounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }
            
            .call-buttons {
                margin: 30px 0;
            }
            
            .call-btn {
                width: 90px;
                height: 90px;
                border-radius: 50%;
                border: none;
                font-size: 35px;
                cursor: pointer;
                margin: 0 20px;
                transition: all 0.3s ease;
                position: relative;
                z-index: 1;
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }
            
            .call-btn.start {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .call-btn.end {
                background: linear-gradient(45deg, #dc3545, #e74c3c);
                color: white;
            }
            
            .call-btn:hover {
                transform: translateY(-5px) scale(1.05);
                box-shadow: 0 15px 30px rgba(0,0,0,0.3);
            }
            
            .call-btn:active {
                transform: translateY(-2px) scale(1.02);
            }
            
            .call-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .conversation {
                background: #f8f9fa;
                border-radius: 20px;
                padding: 25px;
                margin: 25px 0;
                text-align: left;
                max-height: 400px;
                overflow-y: auto;
                display: none;
                position: relative;
                z-index: 1;
                border: 2px solid #e9ecef;
            }
            
            .conversation h4 {
                color: #495057;
                margin-bottom: 20px;
                text-align: center;
                font-size: 18px;
            }
            
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 15px;
                animation: messageSlide 0.4s ease;
                position: relative;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            @keyframes messageSlide {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.farmer {
                background: linear-gradient(45deg, #e3f2fd, #bbdefb);
                margin-left: 40px;
                border-left: 5px solid #2196f3;
            }
            
            .message.ai {
                background: linear-gradient(45deg, #e8f5e8, #c8e6c9);
                margin-right: 40px;
                border-left: 5px solid #4caf50;
            }
            
            .message-header {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 14px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .message-text {
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 10px;
            }
            
            .message-time {
                font-size: 12px;
                color: #666;
                text-align: right;
            }
            
            .features {
                background: rgba(46, 139, 87, 0.1);
                border: 2px solid #2E8B57;
                border-radius: 15px;
                padding: 20px;
                margin: 25px 0;
                position: relative;
                z-index: 1;
            }
            
            .features h4 {
                color: #2E8B57;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .features ul {
                list-style: none;
                padding: 0;
            }
            
            .features li {
                padding: 8px 0;
                color: #495057;
                font-size: 14px;
            }
            
            .features li::before {
                content: '🌾 ';
                margin-right: 8px;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
                animation: statusBlink 2s infinite;
            }
            
            .status-indicator.active {
                background: #28a745;
            }
            
            .status-indicator.inactive {
                background: #6c757d;
            }
            
            @keyframes statusBlink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.5; }
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="header">
                <h1>🌾 AI कृषि सलाहकार</h1>
                <p>Real-Time Voice Call System for Farmers</p>
            </div>
            
            <div class="features">
                <h4>🎯 विशेषताएं</h4>
                <ul>
                    <li>फसल की खेती और बुआई की सलाह</li>
                    <li>खाद और उर्वरक की जानकारी</li>
                    <li>कीट-पतंग नियंत्रण के उपाय</li>
                    <li>सिंचाई और पानी प्रबंधन</li>
                    <li>मंडी भाव और बिक्री की सलाह</li>
                </ul>
            </div>
            
            <div class="call-interface">
                <div class="call-status" id="callStatus">
                    <span class="status-indicator inactive" id="statusIndicator"></span>
                    📞 Call करने के लिए तैयार
                </div>
                
                <div class="call-buttons">
                    <button class="call-btn start" id="startCall" onclick="startVoiceCall()">
                        📞
                    </button>
                    <button class="call-btn end" id="endCall" onclick="endVoiceCall()" disabled>
                        📵
                    </button>
                </div>
            </div>
            
            <div class="conversation" id="conversation">
                <h4>💬 Voice Conversation</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isCallActive = false;
            let currentAudio = null;
            let callStartTime = null;
            let messageCount = 0;
            let isRecognitionRunning = false;
            let recognitionTimeout = null;
            let consecutiveErrors = 0;
            let lastRecognitionTime = 0;
            
            function updateCallStatus(message, type = '') {
                const statusEl = document.getElementById('callStatus');
                const indicatorEl = document.getElementById('statusIndicator');

                statusEl.innerHTML = `<span class="status-indicator ${type === 'connected' || type === 'listening' || type === 'speaking' ? 'active' : 'inactive'}" id="statusIndicator"></span>${message}`;
                statusEl.className = `call-status ${type}`;

                console.log('📞 Status:', message);
            }

            function safeStartRecognition() {
                // Clear any existing timeout
                if (recognitionTimeout) {
                    clearTimeout(recognitionTimeout);
                    recognitionTimeout = null;
                }

                // Only start if call is active and recognition is not running
                if (!isCallActive) {
                    console.log('🛑 Call not active, skipping recognition start');
                    return;
                }

                if (isRecognitionRunning) {
                    console.log('🔄 Recognition already running, skipping start');
                    return;
                }

                if (!recognition) {
                    console.log('❌ Recognition object not available');
                    return;
                }

                // Prevent too frequent restarts
                const now = Date.now();
                if (now - lastRecognitionTime < 2000) {
                    console.log('⏳ Too soon to restart, waiting...');
                    recognitionTimeout = setTimeout(() => {
                        safeStartRecognition();
                    }, 3000);
                    return;
                }

                // Check for too many consecutive errors
                if (consecutiveErrors >= 5) {
                    console.log('🛑 Too many errors, pausing recognition for 10 seconds...');
                    updateCallStatus('🔄 Voice system recovering...', 'processing');
                    consecutiveErrors = 0;
                    recognitionTimeout = setTimeout(() => {
                        if (isCallActive) {
                            updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                            safeStartRecognition();
                        }
                    }, 10000);
                    return;
                }

                try {
                    console.log('🎤 Starting recognition safely...');
                    lastRecognitionTime = now;
                    recognition.start();
                } catch (error) {
                    console.log('⚠️ Recognition start error:', error.message);
                    isRecognitionRunning = false;
                    consecutiveErrors++;

                    // Retry after a longer delay
                    recognitionTimeout = setTimeout(() => {
                        if (isCallActive && !isRecognitionRunning) {
                            safeStartRecognition();
                        }
                    }, 3000);
                }
            }
            
            function startVoiceCall() {
                console.log('📞 Starting voice call...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge browser.');
                    return;
                }
                
                isCallActive = true;
                callStartTime = new Date();
                messageCount = 0;
                consecutiveErrors = 0;
                lastRecognitionTime = 0;
                
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
                    isRecognitionRunning = true;
                    console.log('✅ Voice recognition started');

                    // Clear any pending timeout
                    if (recognitionTimeout) {
                        clearTimeout(recognitionTimeout);
                        recognitionTimeout = null;
                    }

                    // Reset error count on successful start
                    if (consecutiveErrors > 0) {
                        console.log(`🔄 Resetting error count from ${consecutiveErrors} to 0`);
                        consecutiveErrors = 0;
                    }
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;

                    console.log('🎤 Voice input:', transcript, 'Confidence:', confidence.toFixed(2));

                    // Reset consecutive errors on successful recognition
                    consecutiveErrors = 0;

                    // Accept any transcript with reasonable length, ignore confidence for now
                    if (transcript && transcript.length >= 2) {
                        console.log('✅ Processing voice input:', transcript);
                        processVoiceInput(transcript);
                    } else {
                        console.log('⚠️ Empty or too short transcript, restarting...');
                        isRecognitionRunning = false;
                        consecutiveErrors++;
                        if (isCallActive) {
                            recognitionTimeout = setTimeout(() => {
                                safeStartRecognition();
                            }, 2000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('❌ Voice error:', event.error);
                    isRecognitionRunning = false;
                    consecutiveErrors++;

                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied! Please allow microphone access and try again.');
                        endVoiceCall();
                        return;
                    }

                    if (!isCallActive) {
                        return;
                    }

                    // Handle different error types with progressive delays
                    let retryDelay = Math.min(2000 + (consecutiveErrors * 1000), 8000);

                    switch (event.error) {
                        case 'no-speech':
                            console.log('⚠️ No speech detected, restarting...');
                            retryDelay = Math.min(3000 + (consecutiveErrors * 500), 10000);
                            break;
                        case 'audio-capture':
                            console.log('⚠️ Audio capture error, restarting...');
                            retryDelay = Math.min(4000 + (consecutiveErrors * 1000), 12000);
                            break;
                        case 'network':
                            console.log('⚠️ Network error, restarting...');
                            retryDelay = Math.min(5000 + (consecutiveErrors * 1000), 15000);
                            break;
                        default:
                            console.log('⚠️ Other error, restarting...');
                            retryDelay = Math.min(3000 + (consecutiveErrors * 1000), 10000);
                    }

                    console.log(`🔄 Will retry in ${retryDelay}ms (errors: ${consecutiveErrors})`);

                    // Safe restart with progressive delay
                    recognitionTimeout = setTimeout(() => {
                        safeStartRecognition();
                    }, retryDelay);
                };

                recognition.onend = function() {
                    console.log('🔄 Voice recognition ended');
                    isRecognitionRunning = false;

                    if (isCallActive) {
                        // Only restart if no timeout is already set
                        if (!recognitionTimeout) {
                            recognitionTimeout = setTimeout(() => {
                                safeStartRecognition();
                            }, 800);
                        }
                    }
                };
                
                // Start recognition safely
                safeStartRecognition();

                // Welcome message
                setTimeout(() => {
                    const welcomeMsg = 'नमस्कार भाई! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।';
                    addMessage('ai', welcomeMsg);
                    playVoiceResponse(welcomeMsg);
                }, 2000);
            }
            
            function endVoiceCall() {
                console.log('📵 Ending voice call...');
                isCallActive = false;
                isRecognitionRunning = false;

                // Clear any pending timeouts
                if (recognitionTimeout) {
                    clearTimeout(recognitionTimeout);
                    recognitionTimeout = null;
                }

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
                updateCallStatus(`📵 Call Ended (${callDuration}s, ${messageCount} messages)`);
                
                setTimeout(() => {
                    updateCallStatus('📞 Call करने के लिए तैयार');
                }, 5000);
            }
            
            async function processVoiceInput(transcript) {
                console.log('🔄 Processing voice input:', transcript);
                
                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Add farmer message
                addMessage('farmer', transcript);
                messageCount++;
                
                // Update status
                updateCallStatus('🤖 AI सोच रहा है...', 'speaking');
                
                try {
                    // Get AI response
                    const response = await fetch('/api/farming-advice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });
                    
                    const result = await response.json();
                    console.log('📦 AI response received:', result.success);
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        messageCount++;
                        await playVoiceResponse(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें भाई, कुछ तकनीकी समस्या है। फिर से कोशिश करें।';
                        addMessage('ai', errorMsg);
                        await playVoiceResponse(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Voice processing error:', error);
                    const errorMsg = 'नेटवर्क की समस्या है भाई। कनेक्शन चेक करें।';
                    addMessage('ai', errorMsg);
                    await playVoiceResponse(errorMsg);
                }
            }
            
            async function playVoiceResponse(text) {
                console.log('🔊 Playing voice response...');
                updateCallStatus('🔊 AI बोल रहा है...', 'speaking');
                
                try {
                    const response = await fetch('/api/generate-voice', {
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
                                // Ensure recognition is restarted after audio finishes
                                recognitionTimeout = setTimeout(() => {
                                    safeStartRecognition();
                                }, 1200);
                            }
                        };
                        
                        currentAudio.onerror = function(e) {
                            console.error('❌ Audio playback error:', e);
                            if (isCallActive) {
                                updateCallStatus('🎤 Call Connected - आप बोलें!', 'listening');
                            }
                        };
                        
                        await currentAudio.play();
                        console.log('✅ Voice response playing');
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
                    <div class="message-header">
                        <span>${speakerName}</span>
                        <span>${timestamp}</span>
                    </div>
                    <div class="message-text">${text}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
                
                console.log('💬 Message added:', speakerName);
            }
            
            // Initialize
            window.onload = function() {
                console.log('🌾 Farmer Voice Agent ready');
                updateCallStatus('📞 Call करने के लिए तैयार');
            };
            
            // Handle page unload
            window.onbeforeunload = function() {
                if (isCallActive) {
                    endVoiceCall();
                }
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/farming-advice', methods=['POST'])
def farming_advice_api():
    """Main farming advice API"""
    print("🌾 === FARMING ADVICE API ===")
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
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
        print(f"❌ Farming Advice API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate-voice', methods=['POST'])
def generate_voice_api():
    """Voice generation API"""
    print("🔊 === VOICE GENERATION API ===")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_hindi_voice(text)
        
        if audio_file:
            return send_file(audio_file, as_attachment=True, download_name="voice_response.mp3")
        else:
            return jsonify({"success": False, "error": "Voice generation failed"})
            
    except Exception as e:
        print(f"❌ Voice Generation API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """System health check"""
    return jsonify({
        "status": "healthy",
        "api_key": "present" if GROQ_API_KEY else "missing",
        "timestamp": datetime.now().isoformat(),
        "system": "Farmer Voice Agent v1.0"
    })

if __name__ == '__main__':
    print("🌾" + "="*60 + "🌾")
    print("🌾 FINAL FARMER VOICE AGENT - PRODUCTION READY 🌾")
    print("🌾" + "="*60 + "🌾")
    print("🎤 Real-Time Voice Call System for Farmers")
    print("🤖 AI-Powered Agricultural Expert")
    print("🇮🇳 Complete Hindi Language Support")
    print("📞 Phone Call Like Experience")
    print("=" * 64)
    
    print(f"✅ API Key Status: {'READY' if GROQ_API_KEY else 'MISSING'}")
    print(f"✅ Voice Recognition: Browser STT")
    print(f"✅ AI Processing: Groq LLM")
    print(f"✅ Voice Generation: Google TTS")
    print(f"✅ Language: Hindi")
    
    print(f"\n🚀 Starting production server...")
    print(f"🌐 URL: http://localhost:5000")
    print(f"💡 Press Ctrl+C to stop")
    print("🌾" + "="*60 + "🌾")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
