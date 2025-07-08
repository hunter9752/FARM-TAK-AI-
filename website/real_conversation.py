#!/usr/bin/env python3
"""
Real Interactive Voice Conversation System
AI talks with farmer in real-time like phone call
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

def get_conversational_response(query, conversation_history=[]):
    """Get conversational AI response"""
    print(f"🗣️ Conversational query: {query}")
    
    if not api_key:
        return {
            "success": False,
            "response": "API key not configured",
            "response_time": 0
        }
    
    # Build conversation context
    context = ""
    if conversation_history:
        context = "\n".join([f"{msg['speaker']}: {msg['text']}" for msg in conversation_history[-6:]])
    
    system_prompt = f"""आप एक दोस्ताना भारतीय कृषि विशेषज्ञ हैं जो किसान से real-time बातचीत कर रहे हैं। 

बातचीत का तरीका:
- बिल्कुल natural conversation करें
- किसान को "भाई", "जी हाँ", "अच्छा" जैसे शब्दों से जवाब दें
- सवाल का direct जवाब दें
- 1-2 वाक्य में संक्षिप्त रखें
- अगर कोई follow-up question हो तो पूछें
- बिल्कुल phone call की तरह बात करें

पिछली बातचीत:
{context}

अब किसान का नया सवाल है। Natural तरीके से जवाब दें।"""

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
            "temperature": 0.8,
            "max_tokens": 100,
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
    """Real-time conversation interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Real-Time Farmer Conversation</title>
        
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
                max-width: 700px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
                text-align: center;
                color: #333;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            .call-status {
                font-size: 28px;
                font-weight: bold;
                margin: 20px 0;
                padding: 20px;
                border-radius: 15px;
                transition: all 0.3s;
            }
            
            .call-status.idle {
                background: #f8f9fa;
                color: #666;
            }
            
            .call-status.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: pulse 2s infinite;
            }
            
            .call-status.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: pulse 1s infinite;
            }
            
            .call-status.speaking {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }
            
            .voice-circle {
                width: 200px;
                height: 200px;
                border-radius: 50%;
                margin: 30px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 80px;
                transition: all 0.3s;
                cursor: pointer;
            }
            
            .voice-circle.idle {
                background: linear-gradient(45deg, #6c757d, #495057);
                color: white;
            }
            
            .voice-circle.listening {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                animation: listening-pulse 1.5s infinite;
            }
            
            .voice-circle.speaking {
                background: linear-gradient(45deg, #007bff, #6610f2);
                color: white;
                animation: speaking-wave 1s infinite;
            }
            
            .voice-circle.processing {
                background: linear-gradient(45deg, #ffc107, #fd7e14);
                color: white;
                animation: processing-spin 2s linear infinite;
            }
            
            @keyframes listening-pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            @keyframes speaking-wave {
                0%, 100% { transform: scale(1); }
                25% { transform: scale(1.05); }
                50% { transform: scale(1.1); }
                75% { transform: scale(1.05); }
            }
            
            @keyframes processing-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
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
            
            .btn.start {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
            }
            
            .btn.end {
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
            
            .speaker {
                font-weight: bold;
                margin-bottom: 8px;
                font-size: 16px;
            }
            
            .text {
                font-size: 18px;
                line-height: 1.4;
            }
            
            .timestamp {
                font-size: 12px;
                color: #666;
                margin-top: 8px;
            }
            
            .instructions {
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Real-Time Farmer Conversation</h1>
            <p style="font-size: 18px; color: #666;">AI से बात करें जैसे phone call पर बात करते हैं</p>
            
            <div class="call-status idle" id="status">
                बातचीत शुरू करने के लिए तैयार
            </div>
            
            <div class="voice-circle idle" id="voiceCircle" onclick="toggleCall()">
                📞
            </div>
            
            <div class="controls">
                <button class="btn start" id="startBtn" onclick="startConversation()">
                    🎤 बातचीत शुरू करें
                </button>
                <button class="btn end" id="endBtn" onclick="endConversation()" style="display: none;">
                    📵 बातचीत बंद करें
                </button>
            </div>
            
            <div class="instructions">
                <strong>📋 Instructions:</strong><br>
                1. "बातचीत शुरू करें" पर click करें<br>
                2. Microphone access allow करें<br>
                3. Natural तरीके से बोलें जैसे phone पर बात करते हैं<br>
                4. AI आपसे real-time conversation करेगा
            </div>
            
            <div class="conversation" id="conversation" style="display: none;">
                <h4>💬 Live Conversation:</h4>
                <div id="messages"></div>
            </div>
        </div>
        
        <script>
            let isConversationActive = false;
            let recognition = null;
            let currentAudio = null;
            let conversationHistory = [];
            
            function startConversation() {
                console.log('🎤 Starting real-time conversation...');
                
                if (!('webkitSpeechRecognition' in window)) {
                    alert('Voice recognition not supported. Please use Chrome or Edge.');
                    return;
                }
                
                isConversationActive = true;
                conversationHistory = [];
                
                // Update UI
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('endBtn').style.display = 'inline-block';
                document.getElementById('conversation').style.display = 'block';
                
                updateStatus('बातचीत शुरू हो रही है...', 'processing');
                updateVoiceCircle('processing');
                
                // Initialize speech recognition
                recognition = new webkitSpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'hi-IN';
                
                recognition.onstart = function() {
                    console.log('🎤 Listening started');
                    updateStatus('आप बोलिए... मैं सुन रहा हूं', 'listening');
                    updateVoiceCircle('listening');
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript.trim();
                    if (transcript) {
                        console.log('🎤 Farmer said:', transcript);
                        handleFarmerInput(transcript);
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('🎤 Recognition error:', event.error);
                    if (isConversationActive) {
                        setTimeout(() => {
                            if (isConversationActive) {
                                recognition.start();
                            }
                        }, 1000);
                    }
                };
                
                recognition.onend = function() {
                    if (isConversationActive) {
                        setTimeout(() => {
                            if (isConversationActive) {
                                recognition.start();
                            }
                        }, 500);
                    }
                };
                
                // Start listening
                recognition.start();
                
                // AI starts the conversation
                setTimeout(() => {
                    const welcomeMsg = 'नमस्कार भाई! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कुछ भी पूछ सकते हैं। क्या सवाल है?';
                    addMessage('ai', welcomeMsg);
                    speakText(welcomeMsg);
                }, 1000);
            }
            
            function endConversation() {
                console.log('📵 Ending conversation...');
                
                isConversationActive = false;
                
                if (recognition) {
                    recognition.stop();
                }
                
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                updateStatus('बातचीत समाप्त', 'idle');
                updateVoiceCircle('idle');
                
                // Update UI
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('endBtn').style.display = 'none';
            }
            
            function toggleCall() {
                if (isConversationActive) {
                    endConversation();
                } else {
                    startConversation();
                }
            }
            
            async function handleFarmerInput(transcript) {
                // Stop current audio if AI is speaking
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // Add farmer message
                addMessage('farmer', transcript);
                
                // Update status
                updateStatus('AI सोच रहा है...', 'processing');
                updateVoiceCircle('processing');
                
                try {
                    const response = await fetch('/api/conversation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            query: transcript,
                            history: conversationHistory
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const aiResponse = result.response;
                        addMessage('ai', aiResponse);
                        await speakText(aiResponse);
                    } else {
                        const errorMsg = 'माफ करें, मुझे समझ नहीं आया। दोबारा बोलिए।';
                        addMessage('ai', errorMsg);
                        await speakText(errorMsg);
                    }
                } catch (error) {
                    console.error('❌ Conversation error:', error);
                    const errorMsg = 'कुछ technical problem है। दोबारा try करिए।';
                    addMessage('ai', errorMsg);
                    await speakText(errorMsg);
                }
            }
            
            async function speakText(text) {
                console.log('🔊 AI speaking:', text);
                updateStatus('AI बोल रहा है...', 'speaking');
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
                            if (isConversationActive) {
                                updateStatus('आप बोलिए... मैं सुन रहा हूं', 'listening');
                                updateVoiceCircle('listening');
                            }
                        };
                        
                        await currentAudio.play();
                    }
                } catch (error) {
                    console.error('🔊 TTS error:', error);
                    if (isConversationActive) {
                        updateStatus('आप बोलिए... मैं सुन रहा हूं', 'listening');
                        updateVoiceCircle('listening');
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
                    case 'speaking':
                        circleEl.textContent = '🔊';
                        break;
                    case 'processing':
                        circleEl.textContent = '🧠';
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
                    <div class="speaker">${speakerName}</div>
                    <div class="text">${text}</div>
                    <div class="timestamp">${timestamp}</div>
                `;
                
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
                
                // Add to conversation history
                conversationHistory.push({
                    speaker: speaker === 'farmer' ? 'Farmer' : 'AI',
                    text: text,
                    timestamp: timestamp
                });
                
                // Keep only last 10 messages
                if (conversationHistory.length > 10) {
                    conversationHistory = conversationHistory.slice(-10);
                }
            }
            
            console.log('🎤 Real-time conversation system ready');
        </script>
    </body>
    </html>
    """

@app.route('/api/conversation', methods=['POST'])
def handle_conversation():
    """Handle conversational exchange"""
    print("🗣️ Conversation API called")
    
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        history = data.get('history', [])
        
        print(f"👨‍🌾 Farmer: {user_query}")
        
        if not user_query:
            return jsonify({"success": False, "error": "Empty query"})
        
        # Get conversational response
        result = get_conversational_response(user_query, history)
        
        return jsonify({
            "success": result["success"],
            "response": result["response"],
            "response_time": result["response_time"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Conversation error: {e}")
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
    print("🗣️ Starting Real-Time Conversation System...")
    print("🌾 Interactive AI Farmer Assistant")
    print("=" * 60)
    
    if api_key:
        print("✅ API key configured")
    else:
        print("⚠️ API key not found")
    
    print("\n🚀 Starting server...")
    print("🌐 URL: http://localhost:5002")
    print("💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
