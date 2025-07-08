#!/usr/bin/env python3
"""
Final Working Voice Call System
Complete Voice → STT → NLP → AI → TTS → Voice Output
"""

import os
import sys
import time
import tempfile
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Load API keys
api_keys = {}
try:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if value and value != "your_api_key_here":
                        api_keys[key.strip()] = value.strip()
    print(f"✅ Loaded {len(api_keys)} API keys")
except Exception as e:
    print(f"❌ API key loading failed: {e}")

# Simple NLP for farming intents
def detect_farming_intent(text):
    """Simple farming intent detection"""
    text_lower = text.lower()
    
    # Farming keywords
    if any(word in text_lower for word in ['खाद', 'उर्वरक', 'fertilizer', 'यूरिया', 'dap']):
        return {"intent": "fertilizer_advice", "confidence": 0.8}
    elif any(word in text_lower for word in ['कीड़े', 'कीट', 'pest', 'रोग', 'disease']):
        return {"intent": "pest_control", "confidence": 0.8}
    elif any(word in text_lower for word in ['भाव', 'price', 'दाम', 'मंडी', 'market']):
        return {"intent": "market_price", "confidence": 0.8}
    elif any(word in text_lower for word in ['बीज', 'seed', 'बुआई', 'sowing']):
        return {"intent": "crop_advice", "confidence": 0.8}
    elif any(word in text_lower for word in ['पानी', 'water', 'सिंचाई', 'irrigation']):
        return {"intent": "irrigation", "confidence": 0.8}
    else:
        return {"intent": "general_farming", "confidence": 0.5}

def get_ai_response(text, intent_info):
    """Get AI response using Groq"""
    try:
        if 'GROQ_API_KEY' not in api_keys:
            return {"success": False, "response": "API key not configured"}
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_keys['GROQ_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        intent = intent_info.get('intent', 'general_farming')
        
        system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं।

Intent: {intent}

जवाब देने का तरीका:
- हिंदी में स्पष्ट जवाब दें
- 2-3 वाक्य में संक्षिप्त रखें
- व्यावहारिक सलाह दें
- "भाई" या "जी" का प्रयोग करें
- Intent के अनुसार specific advice दें"""

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ AI Response Generated: {ai_response}")
            return {"success": True, "response": ai_response}
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {"success": False, "response": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "response": f"Error: {str(e)}"}

def generate_tts(text):
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
    """Final working voice interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Final Working Voice Call</title>
        
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
            
            h1 { color: #2c3e50; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            
            .workflow {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            
            .step {
                display: flex;
                align-items: center;
                margin: 10px 0;
                padding: 10px;
                background: white;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }
            
            .step-icon { font-size: 24px; margin-right: 15px; }
            .step-text { flex: 1; }
            .step-status { font-size: 20px; }
            
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Final Working Voice Call</h1>
            <p class="subtitle">Complete Voice → STT → NLP → AI → TTS → Voice Output</p>
            
            <div class="workflow">
                <h3>🔄 Real-Time Workflow:</h3>
                <div class="step">
                    <div class="step-icon">🎤</div>
                    <div class="step-text"><strong>Voice Input</strong><br>Browser Speech Recognition</div>
                    <div class="step-status" id="stt-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🧠</div>
                    <div class="step-text"><strong>NLP Processing</strong><br>Intent Detection</div>
                    <div class="step-status" id="nlp-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🤖</div>
                    <div class="step-text"><strong>AI Processing</strong><br>Farming Expert Response</div>
                    <div class="step-status" id="ai-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🔊</div>
                    <div class="step-text"><strong>TTS Output</strong><br>Hindi Voice Synthesis</div>
                    <div class="step-status" id="tts-status">⏳</div>
                </div>
            </div>
            
            <div class="status" id="status">
                Ready for voice call
            </div>
            
            <div>
                <button class="btn success" id="startBtn" onclick="startVoiceCall()">
                    🎤 Start Voice Call
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoiceCall()" disabled>
                    📵 End Voice Call
                </button>
            </div>

            <div style="margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 10px;">
                <h4 style="color: #495057; margin-bottom: 10px;">🧪 Test API First:</h4>
                <input type="text" id="testInput" placeholder="Type: गेहूं के लिए खाद की सलाह दो"
                       style="width: 70%; padding: 8px; margin-right: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <button onclick="testAPI()" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 5px;">
                    Test API
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
            }
            
            function updateStepStatus(step, status) {
                const stepEl = document.getElementById(`${step}-status`);
                if (stepEl) stepEl.textContent = status;
            }
            
            function startVoiceCall() {
                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge.');
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
                    updateStatus('🎤 Voice Call Active - Speak now!', 'listening');
                    updateStepStatus('stt', '✅');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;
                    
                    if (transcript && confidence > 0.3) {
                        processCompleteWorkflow(transcript);
                    } else {
                        if (isCallActive) {
                            setTimeout(() => recognition.start(), 1000);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
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
                updateStatus('Voice call ended', '');
                
                // Reset step statuses
                updateStepStatus('stt', '⏳');
                updateStepStatus('nlp', '⏳');
                updateStepStatus('ai', '⏳');
                updateStepStatus('tts', '⏳');
            }
            
            async function processCompleteWorkflow(transcript) {
                console.log('🔄 Processing workflow for:', transcript);

                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }

                addMessage('farmer', transcript);
                updateStatus('🔄 Processing complete workflow...', 'processing');

                try {
                    // Step 1: STT already done
                    updateStepStatus('stt', '✅');
                    console.log('✅ STT completed');

                    // Step 2: NLP Processing
                    updateStatus('🧠 NLP Processing...', 'processing');
                    updateStepStatus('nlp', '🔄');
                    console.log('🧠 Starting NLP processing...');

                    // Step 3: AI Processing
                    updateStatus('🤖 AI Processing...', 'processing');
                    updateStepStatus('ai', '🔄');
                    console.log('🤖 Starting AI processing...');

                    // Call complete workflow API
                    console.log('📡 Making API call...');
                    const response = await fetch('/api/complete-workflow', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });

                    console.log('📡 API response status:', response.status);
                    const result = await response.json();
                    console.log('📦 API result:', result);

                    if (result.success) {
                        updateStepStatus('nlp', '✅');
                        updateStepStatus('ai', '✅');
                        console.log('✅ NLP and AI completed successfully');

                        addMessage('ai', result.response);
                        await playTTS(result.response);
                    } else {
                        console.error('❌ API error:', result.error);
                        updateStepStatus('nlp', '❌');
                        updateStepStatus('ai', '❌');

                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await playTTS(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Network error:', error);
                    updateStepStatus('nlp', '❌');
                    updateStepStatus('ai', '❌');

                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await playTTS(errorMsg);
                }
            }
            
            async function playTTS(text) {
                updateStatus('🔊 AI is speaking...', 'processing');
                
                try {
                    const response = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    if (response.ok) {
                        updateStepStatus('tts', '✅');
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        currentAudio = new Audio(audioUrl);
                        
                        currentAudio.onended = function() {
                            currentAudio = null;
                            if (isCallActive) {
                                updateStatus('🎤 Voice Call Active - Speak now!', 'listening');
                                updateStepStatus('nlp', '⏳');
                                updateStepStatus('ai', '⏳');
                                updateStepStatus('tts', '⏳');
                            }
                        };
                        
                        await currentAudio.play();
                    }
                } catch (error) {
                    if (isCallActive) {
                        updateStatus('🎤 Voice Call Active - Speak now!', 'listening');
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

            async function testAPI() {
                const query = document.getElementById('testInput').value.trim();
                if (!query) {
                    document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                    return;
                }

                console.log('🧪 Testing API with:', query);
                document.getElementById('testResult').innerHTML = '<div style="color: #007bff;">🔄 Testing API...</div>';

                try {
                    const response = await fetch('/api/complete-workflow', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    console.log('📡 Test API response status:', response.status);
                    const result = await response.json();
                    console.log('📦 Test API result:', result);

                    if (result.success) {
                        document.getElementById('testResult').innerHTML =
                            `<div style="background: #d4edda; padding: 10px; border-radius: 5px; color: #155724; margin-top: 10px;">
                                <strong>✅ API Working!</strong><br>
                                Intent: ${result.intent} (${result.confidence})<br>
                                Response: ${result.response}
                            </div>`;
                    } else {
                        document.getElementById('testResult').innerHTML =
                            `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-top: 10px;">
                                <strong>❌ API Error:</strong> ${result.error}
                            </div>`;
                    }
                } catch (error) {
                    console.error('❌ Test API error:', error);
                    document.getElementById('testResult').innerHTML =
                        `<div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-top: 10px;">
                            <strong>❌ Network Error:</strong> ${error.message}
                        </div>`;
                }
            }

            // Auto-test API on load
            window.onload = function() {
                document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                setTimeout(testAPI, 1000);
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/complete-workflow', methods=['POST'])
def complete_workflow():
    """Complete workflow: Voice → STT → NLP → AI → TTS"""
    print("🔄 === COMPLETE WORKFLOW API CALLED ===")
    
    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()
        
        print(f"🎤 Voice Input: {user_input}")
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty voice input"})
        
        # Step 2: NLP Processing
        print("🧠 Step 2: NLP Processing...")
        intent_info = detect_farming_intent(user_input)
        print(f"✅ NLP Result: {intent_info}")
        
        # Step 3: AI Processing
        print("🤖 Step 3: AI Processing...")
        ai_result = get_ai_response(user_input, intent_info)
        print(f"✅ AI Result: {ai_result['success']}")
        
        if ai_result["success"]:
            final_response = {
                "success": True,
                "response": ai_result["response"],
                "intent": intent_info["intent"],
                "confidence": intent_info["confidence"]
            }
            print(f"📤 Final Response: {final_response}")
            return jsonify(final_response)
        else:
            error_response = {
                "success": False,
                "error": ai_result["response"]
            }
            print(f"❌ Error Response: {error_response}")
            return jsonify(error_response)
        
    except Exception as e:
        print(f"❌ Workflow Error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def tts_api():
    """Text-to-Speech API"""
    print("🔊 === TTS API CALLED ===")
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        print(f"🔊 TTS Input: {text}")
        
        if not text:
            return jsonify({"success": False, "error": "Empty text"})
        
        audio_file = generate_tts(text)
        
        if audio_file:
            print(f"✅ TTS Generated: {audio_file}")
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            return jsonify({"success": False, "error": "TTS generation failed"})
            
    except Exception as e:
        print(f"❌ TTS API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🎤 Starting Final Working Voice Call System...")
    print("🌾 Complete Voice → STT → NLP → AI → TTS → Voice Output")
    print("=" * 60)
    
    print(f"✅ API Keys: {len(api_keys)} loaded")
    print(f"✅ NLP: Simple keyword-based intent detection")
    print(f"✅ AI: Groq LLM for farming advice")
    print(f"✅ TTS: Google Text-to-Speech")
    
    print(f"\n🚀 Starting server...")
    print(f"🌐 URL: http://localhost:5010")
    print(f"💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5010)
