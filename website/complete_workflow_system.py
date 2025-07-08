#!/usr/bin/env python3
"""
Complete Workflow System for Real-Time Voice Call Agent
Voice → STT → NLP → AI → TTS → Voice Output
"""

import os
import sys
import time
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
CORS(app)

# Global variables for models
api_keys = {}
nlp_model = None
conversation_history = []

def load_api_keys():
    """Load API keys from .env file"""
    global api_keys
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

        print("✅ API Keys loaded:")
        for key in api_keys:
            if 'API_KEY' in key:
                print(f"   - {key}: {'✅' if api_keys[key] else '❌'}")

        return len(api_keys) > 0
    except Exception as e:
        print(f"❌ Failed to load API keys: {e}")
        return False

def load_nlp_model():
    """Load NLP intent detection model"""
    global nlp_model
    try:
        # Import simple NLP model (no pandas dependency)
        from simple_nlp_detector import SimpleNLPDetector

        nlp_model = SimpleNLPDetector()
        print("✅ Simple NLP Model loaded successfully")
        return True

    except Exception as e:
        print(f"❌ Failed to load NLP model: {e}")
        return False

def stt_process(audio_data):
    """Speech-to-Text processing (Browser handles this)"""
    # In real implementation, this would process audio
    # For now, we receive text from browser's speech recognition
    return audio_data

def nlp_process(text):
    """NLP Intent Detection"""
    print(f"🧠 NLP Processing: {text}")

    try:
        if nlp_model:
            result = nlp_model.detect_intent(text)
            print(f"✅ NLP Result: {result}")
            return result
        else:
            # Fallback NLP
            print("⚠️ Using fallback NLP")
            return {
                "intent": "general_farming",
                "confidence": 0.5,
                "entities": {},
                "category": "farming_advice"
            }
    except Exception as e:
        print(f"❌ NLP Error: {e}")
        return {
            "intent": "general_farming",
            "confidence": 0.3,
            "entities": {},
            "category": "farming_advice",
            "error": str(e)
        }

def ai_process(text, nlp_result):
    """AI LLM Processing"""
    print(f"🤖 AI Processing: {text}")
    print(f"🧠 NLP Context: {nlp_result}")

    try:
        # Use Groq API (fastest)
        if 'GROQ_API_KEY' in api_keys:
            return groq_ai_process(text, nlp_result)
        elif 'OPENAI_API_KEY' in api_keys:
            return openai_ai_process(text, nlp_result)
        elif 'GEMINI_API_KEY' in api_keys:
            return gemini_ai_process(text, nlp_result)
        else:
            return {
                "success": False,
                "response": "कोई AI API key configured नहीं है।",
                "provider": "none"
            }
    except Exception as e:
        print(f"❌ AI Processing Error: {e}")
        return {
            "success": False,
            "response": f"AI Error: {str(e)}",
            "provider": "error"
        }

def groq_ai_process(text, nlp_result):
    """Process with Groq AI"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_keys['GROQ_API_KEY']}",
            "Content-Type": "application/json"
        }

        # Enhanced system prompt based on NLP intent
        intent = nlp_result.get('intent', 'general_farming')
        category = nlp_result.get('category', 'farming_advice')

        system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं।

Intent: {intent}
Category: {category}

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
            "max_tokens": 150,
            "stream": False
        }

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print(f"✅ Groq AI Response: {ai_response}")

            return {
                "success": True,
                "response": ai_response,
                "response_time": response_time,
                "provider": "groq",
                "intent_used": intent
            }
        else:
            print(f"❌ Groq API Error: {response.status_code}")
            return {
                "success": False,
                "response": f"Groq API Error: {response.status_code}",
                "provider": "groq"
            }

    except Exception as e:
        print(f"❌ Groq Exception: {e}")
        return {
            "success": False,
            "response": f"Groq Error: {str(e)}",
            "provider": "groq"
        }

def openai_ai_process(text, nlp_result):
    """Process with OpenAI"""
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_keys['OPENAI_API_KEY']}",
            "Content-Type": "application/json"
        }

        intent = nlp_result.get('intent', 'general_farming')

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": f"आप एक भारतीय कृषि विशेषज्ञ हैं। Intent: {intent}. हिंदी में संक्षिप्त जवाब दें।"},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            return {
                "success": True,
                "response": ai_response,
                "provider": "openai"
            }
        else:
            return {
                "success": False,
                "response": f"OpenAI API Error: {response.status_code}",
                "provider": "openai"
            }

    except Exception as e:
        return {
            "success": False,
            "response": f"OpenAI Error: {str(e)}",
            "provider": "openai"
        }

def gemini_ai_process(text, nlp_result):
    """Process with Google Gemini"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_keys['GEMINI_API_KEY']}"
        headers = {"Content-Type": "application/json"}

        intent = nlp_result.get('intent', 'general_farming')

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"आप एक भारतीय कृषि विशेषज्ञ हैं। Intent: {intent}. हिंदी में संक्षिप्त जवाब दें। प्रश्न: {text}"
                }]
            }]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            result = response.json()
            ai_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {
                "success": True,
                "response": ai_response,
                "provider": "gemini"
            }
        else:
            return {
                "success": False,
                "response": f"Gemini API Error: {response.status_code}",
                "provider": "gemini"
            }

    except Exception as e:
        return {
            "success": False,
            "response": f"Gemini Error: {str(e)}",
            "provider": "gemini"
        }

def tts_process(text):
    """Text-to-Speech processing"""
    print(f"🔊 TTS Processing: {text}")

    try:
        from gtts import gTTS

        # Create TTS
        tts = gTTS(text=text, lang="hi", slow=False)

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        print(f"✅ TTS Generated: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

def check_all_models():
    """Check connectivity of all models"""
    print("🔍 Checking all models connectivity...")

    status = {
        "api_keys": False,
        "nlp_model": False,
        "ai_model": False,
        "tts_model": False,
        "overall": False
    }

    # Check API Keys
    status["api_keys"] = load_api_keys()

    # Check NLP Model
    status["nlp_model"] = load_nlp_model()

    # Check AI Model
    try:
        if 'GROQ_API_KEY' in api_keys:
            test_result = groq_ai_process("Test query", {"intent": "test", "category": "test"})
            status["ai_model"] = test_result["success"]
        else:
            status["ai_model"] = False
    except:
        status["ai_model"] = False

    # Check TTS Model
    try:
        test_audio = tts_process("Test")
        status["tts_model"] = test_audio is not None
        if test_audio:
            os.unlink(test_audio)  # Clean up test file
    except:
        status["tts_model"] = False

    # Overall status
    status["overall"] = all([
        status["api_keys"],
        status["ai_model"],
        status["tts_model"]
    ])

    print("📊 Model Status:")
    print(f"   API Keys: {'✅' if status['api_keys'] else '❌'}")
    print(f"   NLP Model: {'✅' if status['nlp_model'] else '⚠️'}")
    print(f"   AI Model: {'✅' if status['ai_model'] else '❌'}")
    print(f"   TTS Model: {'✅' if status['tts_model'] else '❌'}")
    print(f"   Overall: {'✅' if status['overall'] else '❌'}")

    return status

# Routes for complete workflow
@app.route('/')
def index():
    """Complete workflow interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Complete Workflow Voice Agent</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

            h1 { color: #2c3e50; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }

            .workflow {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }

            .workflow h3 { color: #495057; margin-bottom: 15px; }

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
            .btn.primary { background: #007bff; color: white; }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }

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
            <h1>🎤 Complete Workflow Voice Agent</h1>
            <p class="subtitle">Voice → STT → NLP → AI → TTS → Voice Output</p>

            <div class="workflow">
                <h3>🔄 Real-Time Workflow:</h3>
                <div class="step">
                    <div class="step-icon">🎤</div>
                    <div class="step-text">
                        <strong>Voice Input</strong><br>
                        Browser Speech Recognition (STT)
                    </div>
                    <div class="step-status" id="stt-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🧠</div>
                    <div class="step-text">
                        <strong>NLP Processing</strong><br>
                        Intent Detection & Entity Extraction
                    </div>
                    <div class="step-status" id="nlp-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🤖</div>
                    <div class="step-text">
                        <strong>AI Processing</strong><br>
                        LLM Farming Expert Response
                    </div>
                    <div class="step-status" id="ai-status">⏳</div>
                </div>
                <div class="step">
                    <div class="step-icon">🔊</div>
                    <div class="step-text">
                        <strong>TTS Output</strong><br>
                        Hindi Voice Synthesis
                    </div>
                    <div class="step-status" id="tts-status">⏳</div>
                </div>
            </div>

            <div class="status" id="status">
                Checking system connectivity...
            </div>

            <div>
                <button class="btn primary" onclick="checkSystem()">
                    🔍 Check All Models
                </button>
                <button class="btn success" id="voiceBtn" onclick="startVoiceAgent()" disabled>
                    🎤 Start Voice Agent
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopVoiceAgent()" disabled>
                    🛑 Stop Agent
                </button>
            </div>

            <button class="btn primary" onclick="toggleDebug()" style="font-size: 14px; padding: 8px 16px;">
                🔍 Show Debug Logs
            </button>

            <div class="debug" id="debugLog">
                Debug information will appear here...
            </div>

            <div class="conversation" id="conversation">
                <h4>💬 Voice Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>

        <script>
            let recognition = null;
            let isAgentActive = false;
            let currentAudio = null;
            let systemStatus = {};

            function log(message) {
                const debugEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                debugEl.innerHTML += `[${timestamp}] ${message}\\n`;
                debugEl.scrollTop = debugEl.scrollHeight;
                console.log(`[LOG] ${message}`);
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

            function updateStepStatus(step, status) {
                const stepEl = document.getElementById(`${step}-status`);
                if (stepEl) {
                    stepEl.textContent = status;
                }
            }

            async function checkSystem() {
                log('🔍 Checking system connectivity...');
                updateStatus('Checking all models...', 'processing');

                try {
                    const response = await fetch('/api/check-system');
                    const result = await response.json();

                    log(`📊 System check result: ${JSON.stringify(result)}`);

                    systemStatus = result;

                    // Update step statuses
                    updateStepStatus('stt', '✅'); // Browser handles STT
                    updateStepStatus('nlp', result.nlp_model ? '✅' : '⚠️');
                    updateStepStatus('ai', result.ai_model ? '✅' : '❌');
                    updateStepStatus('tts', result.tts_model ? '✅' : '❌');

                    if (result.overall) {
                        updateStatus('✅ All systems ready for voice agent!', 'listening');
                        document.getElementById('voiceBtn').disabled = false;
                    } else {
                        updateStatus('❌ Some systems not ready. Check logs.', 'error');
                        document.getElementById('voiceBtn').disabled = true;
                    }

                } catch (error) {
                    log(`❌ System check error: ${error.message}`);
                    updateStatus('❌ System check failed', 'error');
                }
            }

            function startVoiceAgent() {
                log('🎤 Starting voice agent...');

                if (!('webkitSpeechRecognition' in window)) {
                    alert('❌ Voice recognition not supported! Please use Chrome or Edge.');
                    return;
                }

                isAgentActive = true;
                document.getElementById('voiceBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('conversation').style.display = 'block';

                // Initialize speech recognition
                recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';

                recognition.onstart = function() {
                    log('✅ Voice agent started');
                    updateStatus('🎤 Voice Agent Active - Speak now!', 'listening');
                };

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript.trim();
                    const confidence = event.results[0][0].confidence;

                    log(`🎤 Voice input: "${transcript}" (confidence: ${confidence.toFixed(2)})`);

                    if (transcript && confidence > 0.3) {
                        processVoiceWorkflow(transcript);
                    } else {
                        log('❌ Low confidence, restarting...');
                        if (isAgentActive) {
                            setTimeout(() => recognition.start(), 1000);
                        }
                    }
                };

                recognition.onerror = function(event) {
                    log(`❌ Voice error: ${event.error}`);
                    if (event.error === 'not-allowed') {
                        alert('❌ Microphone access denied!');
                        stopVoiceAgent();
                    }
                };

                recognition.onend = function() {
                    if (isAgentActive) {
                        setTimeout(() => recognition.start(), 500);
                    }
                };

                // Start recognition
                recognition.start();

                // Welcome message
                setTimeout(() => {
                    addMessage('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
                }, 1000);
            }

            function stopVoiceAgent() {
                log('🛑 Stopping voice agent');
                isAgentActive = false;

                if (recognition) {
                    recognition.stop();
                }

                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }

                document.getElementById('voiceBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Voice agent stopped', '');
            }

            async function processVoiceWorkflow(transcript) {
                log(`🔄 Processing complete workflow for: "${transcript}"`);

                // Stop current audio
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }

                // Add user message
                addMessage('farmer', transcript);

                // Update status
                updateStatus('🔄 Processing complete workflow...', 'processing');

                try {
                    // Call complete workflow API
                    const response = await fetch('/api/workflow', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: transcript })
                    });

                    const result = await response.json();
                    log(`📦 Workflow result: ${JSON.stringify(result)}`);

                    if (result.success) {
                        const aiResponse = result.final_response;
                        addMessage('ai', aiResponse);

                        // Show workflow steps
                        log('📊 Workflow steps completed:');
                        if (result.workflow_steps) {
                            log(`   STT: ${result.workflow_steps.stt?.status || 'unknown'}`);
                            log(`   NLP: ${result.workflow_steps.nlp?.status || 'unknown'}`);
                            log(`   AI: ${result.workflow_steps.ai?.status || 'unknown'}`);
                        }

                        // Generate TTS
                        await playTTS(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, कुछ गलती हुई है।';
                        addMessage('ai', errorMsg);
                        await playTTS(errorMsg);
                    }
                } catch (error) {
                    log(`❌ Workflow error: ${error.message}`);
                    const errorMsg = 'नेटवर्क की समस्या है।';
                    addMessage('ai', errorMsg);
                    await playTTS(errorMsg);
                }
            }

            async function playTTS(text) {
                log(`🔊 Playing TTS: "${text}"`);
                updateStatus('🔊 AI is speaking...', 'processing');

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
                            if (isAgentActive) {
                                updateStatus('🎤 Voice Agent Active - Speak now!', 'listening');
                            }
                        };

                        await currentAudio.play();
                    }
                } catch (error) {
                    log(`❌ TTS error: ${error.message}`);
                    if (isAgentActive) {
                        updateStatus('🎤 Voice Agent Active - Speak now!', 'listening');
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

            // Auto-check system on load
            window.onload = function() {
                log('🚀 Complete workflow system initialized');
                setTimeout(checkSystem, 1000);
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/check-system', methods=['GET'])
def check_system_api():
    """Check all models connectivity"""
    print("🔍 === SYSTEM CHECK API CALLED ===")

    try:
        status = check_all_models()
        print(f"📊 System Status: {status}")
        return jsonify(status)
    except Exception as e:
        print(f"❌ System check error: {e}")
        return jsonify({
            "api_keys": False,
            "nlp_model": False,
            "ai_model": False,
            "tts_model": False,
            "overall": False,
            "error": str(e)
        })

@app.route('/api/workflow', methods=['POST'])
def complete_workflow():
    """Complete workflow: Voice → STT → NLP → AI → TTS"""
    print("🔄 === COMPLETE WORKFLOW API CALLED ===")

    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()

        print(f"🎤 Voice Input: {user_input}")

        if not user_input:
            return jsonify({
                "success": False,
                "error": "Empty voice input",
                "workflow_step": "input_validation"
            })

        workflow_result = {
            "success": True,
            "input": user_input,
            "workflow_steps": {},
            "final_response": "",
            "timestamp": datetime.now().isoformat()
        }

        # Step 1: STT (Already done by browser)
        print("✅ Step 1: STT - Voice to Text completed by browser")
        workflow_result["workflow_steps"]["stt"] = {
            "status": "success",
            "output": user_input,
            "method": "browser_speech_recognition"
        }

        # Step 2: NLP Processing
        print("🧠 Step 2: NLP Processing...")
        nlp_result = nlp_process(user_input)
        workflow_result["workflow_steps"]["nlp"] = {
            "status": "success" if nlp_result else "warning",
            "output": nlp_result,
            "method": "csv_based_intent_detection"
        }

        # Step 3: AI Processing
        print("🤖 Step 3: AI Processing...")
        ai_result = ai_process(user_input, nlp_result)
        workflow_result["workflow_steps"]["ai"] = {
            "status": "success" if ai_result["success"] else "error",
            "output": ai_result,
            "method": "groq_llm"
        }

        if ai_result["success"]:
            workflow_result["final_response"] = ai_result["response"]
        else:
            workflow_result["final_response"] = "माफ करें, AI में कुछ समस्या है।"
            workflow_result["success"] = False

        print(f"📤 Workflow Result: {workflow_result['success']}")
        return jsonify(workflow_result)

    except Exception as e:
        print(f"❌ Workflow Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "workflow_step": "exception"
        })

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

        # Step 4: TTS Processing
        audio_file = tts_process(text)

        if audio_file:
            print(f"✅ TTS Generated: {audio_file}")
            return send_file(audio_file, as_attachment=True, download_name="response.mp3")
        else:
            print("❌ TTS Generation failed")
            return jsonify({"success": False, "error": "TTS generation failed"})

    except Exception as e:
        print(f"❌ TTS API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🔄 Starting Complete Workflow System...")
    print("🌾 Voice → STT → NLP → AI → TTS → Voice Output")
    print("=" * 60)

    # Initialize system
    print("\n🔧 Initializing all models...")

    # Load API keys
    api_loaded = load_api_keys()
    print(f"API Keys: {'✅' if api_loaded else '❌'}")

    # Load NLP model
    nlp_loaded = load_nlp_model()
    print(f"NLP Model: {'✅' if nlp_loaded else '⚠️'}")

    # Check overall system
    system_status = check_all_models()

    print(f"\n🚀 Starting server...")
    print(f"🌐 URL: http://localhost:5009")
    print(f"💡 Press Ctrl+C to stop")
    print(f"\n📊 System Status: {'✅ READY' if system_status['overall'] else '⚠️ PARTIAL'}")

    app.run(debug=True, host='0.0.0.0', port=5009)