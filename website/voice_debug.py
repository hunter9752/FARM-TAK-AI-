#!/usr/bin/env python3
"""
Voice Recognition Debug System
Simple voice test to check microphone and speech recognition
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Voice debug interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎤 Voice Debug Test</title>
        
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
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                color: #333;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
            }
            
            .status {
                font-size: 20px;
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                transition: all 0.3s;
            }
            
            .status.idle {
                background: #f8f9fa;
                color: #666;
                border: 2px solid #dee2e6;
            }
            
            .status.listening {
                background: #d4edda;
                color: #155724;
                border: 2px solid #28a745;
                animation: pulse 2s infinite;
            }
            
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 2px solid #dc3545;
            }
            
            .status.success {
                background: #d1ecf1;
                color: #0c5460;
                border: 2px solid #17a2b8;
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
                transition: all 0.3s;
                font-weight: bold;
            }
            
            .btn.primary {
                background: #007bff;
                color: white;
            }
            
            .btn.success {
                background: #28a745;
                color: white;
            }
            
            .btn.danger {
                background: #dc3545;
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
            
            .debug-info {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
                border-left: 4px solid #007bff;
            }
            
            .debug-info h4 {
                color: #007bff;
                margin-bottom: 10px;
            }
            
            .log {
                background: #343a40;
                color: #fff;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                font-family: monospace;
                font-size: 14px;
                max-height: 200px;
                overflow-y: auto;
                text-align: left;
            }
            
            .result {
                background: #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
                border-left: 4px solid #28a745;
            }
            
            .error-msg {
                background: #f8d7da;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }
            
            .steps {
                background: #fff3cd;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
                border-left: 4px solid #ffc107;
                color: #856404;
            }
            
            .steps ol {
                margin: 10px 0;
                padding-left: 20px;
            }
            
            .steps li {
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Voice Recognition Debug</h1>
            <p>Let's test your microphone and voice recognition step by step</p>
            
            <div class="status idle" id="status">
                Ready to test voice recognition
            </div>
            
            <div class="debug-info">
                <h4>🔍 System Check:</h4>
                <div id="systemCheck">Checking browser compatibility...</div>
            </div>
            
            <div>
                <button class="btn primary" id="testBtn" onclick="testVoiceRecognition()">
                    🎤 Test Voice Recognition
                </button>
                <button class="btn danger" id="stopBtn" onclick="stopTest()" disabled>
                    🛑 Stop Test
                </button>
            </div>
            
            <div class="steps">
                <h4>📋 Test Steps:</h4>
                <ol>
                    <li>Click "Test Voice Recognition" button</li>
                    <li>Allow microphone access when prompted</li>
                    <li>Speak clearly: "Hello test"</li>
                    <li>Check if your voice is detected</li>
                    <li>Try Hindi: "नमस्कार टेस्ट"</li>
                </ol>
            </div>
            
            <div class="log" id="debugLog">
                Debug log will appear here...
            </div>
            
            <div id="results"></div>
        </div>
        
        <script>
            let recognition = null;
            let isTestRunning = false;
            
            function log(message) {
                const logEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                logEl.innerHTML += `[${timestamp}] ${message}\\n`;
                logEl.scrollTop = logEl.scrollHeight;
                console.log(message);
            }
            
            function updateStatus(message, type) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
            }
            
            function showResult(message, isError = false) {
                const resultsEl = document.getElementById('results');
                const className = isError ? 'error-msg' : 'result';
                resultsEl.innerHTML += `<div class="${className}">${message}</div>`;
            }
            
            // Check browser compatibility
            function checkBrowserCompatibility() {
                log('🔍 Checking browser compatibility...');
                
                const checks = [];
                
                // Check if speech recognition is available
                if ('webkitSpeechRecognition' in window) {
                    checks.push('✅ webkitSpeechRecognition supported');
                    log('✅ webkitSpeechRecognition is available');
                } else if ('SpeechRecognition' in window) {
                    checks.push('✅ SpeechRecognition supported');
                    log('✅ SpeechRecognition is available');
                } else {
                    checks.push('❌ Speech Recognition NOT supported');
                    log('❌ Speech Recognition is NOT available');
                }
                
                // Check if getUserMedia is available
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    checks.push('✅ getUserMedia supported');
                    log('✅ getUserMedia is available');
                } else {
                    checks.push('❌ getUserMedia NOT supported');
                    log('❌ getUserMedia is NOT available');
                }
                
                // Check browser
                const userAgent = navigator.userAgent;
                if (userAgent.includes('Chrome')) {
                    checks.push('✅ Chrome browser detected');
                    log('✅ Chrome browser detected');
                } else if (userAgent.includes('Edge')) {
                    checks.push('✅ Edge browser detected');
                    log('✅ Edge browser detected');
                } else {
                    checks.push('⚠️ Browser may not fully support voice recognition');
                    log('⚠️ Browser may not fully support voice recognition');
                }
                
                // Check HTTPS
                if (location.protocol === 'https:' || location.hostname === 'localhost') {
                    checks.push('✅ Secure context (HTTPS/localhost)');
                    log('✅ Secure context detected');
                } else {
                    checks.push('❌ Insecure context - voice may not work');
                    log('❌ Insecure context detected');
                }
                
                document.getElementById('systemCheck').innerHTML = checks.join('<br>');
            }
            
            async function testMicrophoneAccess() {
                log('🎤 Testing microphone access...');
                
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    log('✅ Microphone access granted');
                    showResult('✅ Microphone access: GRANTED');
                    
                    // Stop the stream
                    stream.getTracks().forEach(track => track.stop());
                    return true;
                } catch (error) {
                    log(`❌ Microphone access denied: ${error.message}`);
                    showResult(`❌ Microphone access: DENIED - ${error.message}`, true);
                    return false;
                }
            }
            
            function testVoiceRecognition() {
                if (isTestRunning) {
                    log('⚠️ Test already running');
                    return;
                }
                
                log('🎤 Starting voice recognition test...');
                isTestRunning = true;
                
                document.getElementById('testBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                
                updateStatus('Testing voice recognition...', 'listening');
                
                // Check if speech recognition is available
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    log('❌ Speech Recognition not supported in this browser');
                    showResult('❌ Speech Recognition not supported. Please use Chrome or Edge.', true);
                    stopTest();
                    return;
                }
                
                // Initialize speech recognition
                const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'hi-IN';
                recognition.maxAlternatives = 3;
                
                log('🔧 Speech recognition configured');
                log(`   - Language: ${recognition.lang}`);
                log(`   - Continuous: ${recognition.continuous}`);
                log(`   - Interim results: ${recognition.interimResults}`);
                
                recognition.onstart = function() {
                    log('✅ Speech recognition started');
                    updateStatus('🎤 Listening... Speak now!', 'listening');
                    showResult('✅ Voice recognition started - speak now!');
                };
                
                recognition.onresult = function(event) {
                    log('📝 Speech recognition result received');
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const result = event.results[i];
                        const transcript = result[0].transcript;
                        const confidence = result[0].confidence;
                        const isFinal = result.isFinal;
                        
                        log(`   - Result ${i}: "${transcript}" (confidence: ${confidence.toFixed(2)}, final: ${isFinal})`);
                        
                        if (isFinal) {
                            showResult(`✅ FINAL RESULT: "${transcript}" (Confidence: ${(confidence * 100).toFixed(1)}%)`);
                            updateStatus('Voice detected successfully!', 'success');
                        } else {
                            showResult(`⏳ Interim: "${transcript}"`);
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    log(`❌ Speech recognition error: ${event.error}`);
                    
                    let errorMessage = '';
                    switch(event.error) {
                        case 'not-allowed':
                            errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
                            break;
                        case 'no-speech':
                            errorMessage = 'No speech detected. Please speak louder or closer to the microphone.';
                            break;
                        case 'audio-capture':
                            errorMessage = 'Audio capture failed. Check if microphone is working.';
                            break;
                        case 'network':
                            errorMessage = 'Network error. Check your internet connection.';
                            break;
                        default:
                            errorMessage = `Unknown error: ${event.error}`;
                    }
                    
                    showResult(`❌ ERROR: ${errorMessage}`, true);
                    updateStatus('Voice recognition failed', 'error');
                    stopTest();
                };
                
                recognition.onend = function() {
                    log('🔚 Speech recognition ended');
                    if (isTestRunning) {
                        updateStatus('Test completed', 'idle');
                        stopTest();
                    }
                };
                
                // Start recognition
                try {
                    recognition.start();
                    log('🚀 Starting speech recognition...');
                } catch (error) {
                    log(`❌ Failed to start recognition: ${error.message}`);
                    showResult(`❌ Failed to start: ${error.message}`, true);
                    stopTest();
                }
            }
            
            function stopTest() {
                log('🛑 Stopping voice recognition test...');
                isTestRunning = false;
                
                if (recognition) {
                    recognition.stop();
                    recognition = null;
                }
                
                document.getElementById('testBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Test stopped', 'idle');
            }
            
            // Initialize
            window.onload = function() {
                log('🚀 Voice Debug System initialized');
                checkBrowserCompatibility();
                
                // Test microphone access
                setTimeout(async () => {
                    await testMicrophoneAccess();
                }, 1000);
            };
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🔍 Starting Voice Debug System...")
    print("🎤 Testing Voice Recognition Step by Step")
    print("=" * 60)
    
    print("\n🚀 Starting debug server...")
    print("🌐 URL: http://localhost:5005")
    print("💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5005)
