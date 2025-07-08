#!/usr/bin/env python3
"""
Debug Flow System - Complete Input/Output Tracking
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

def debug_nlp_processing(text):
    """Debug NLP processing with detailed logs"""
    print(f"🧠 === NLP DEBUG START ===")
    print(f"🧠 Input Text: '{text}'")
    print(f"🧠 Text Length: {len(text)} characters")
    
    text_lower = text.lower()
    print(f"🧠 Lowercase Text: '{text_lower}'")
    
    # Check each intent category
    intent_results = {}
    
    # Fertilizer keywords
    fertilizer_keywords = ['खाद', 'उर्वरक', 'fertilizer', 'यूरिया', 'dap']
    fertilizer_matches = [word for word in fertilizer_keywords if word in text_lower]
    intent_results['fertilizer'] = fertilizer_matches
    print(f"🧠 Fertilizer matches: {fertilizer_matches}")
    
    # Pest control keywords
    pest_keywords = ['कीड़े', 'कीट', 'pest', 'रोग', 'disease']
    pest_matches = [word for word in pest_keywords if word in text_lower]
    intent_results['pest'] = pest_matches
    print(f"🧠 Pest matches: {pest_matches}")
    
    # Market keywords
    market_keywords = ['भाव', 'price', 'दाम', 'मंडी', 'market']
    market_matches = [word for word in market_keywords if word in text_lower]
    intent_results['market'] = market_matches
    print(f"🧠 Market matches: {market_matches}")
    
    # Determine intent
    if fertilizer_matches:
        intent = "fertilizer_advice"
        confidence = 0.8
    elif pest_matches:
        intent = "pest_control"
        confidence = 0.8
    elif market_matches:
        intent = "market_price"
        confidence = 0.8
    else:
        intent = "general_farming"
        confidence = 0.5
    
    result = {
        "intent": intent,
        "confidence": confidence,
        "matches": intent_results,
        "debug_info": {
            "input_text": text,
            "processed_text": text_lower,
            "total_keywords_checked": len(fertilizer_keywords) + len(pest_keywords) + len(market_keywords)
        }
    }
    
    print(f"🧠 Final Intent: {intent}")
    print(f"🧠 Confidence: {confidence}")
    print(f"🧠 === NLP DEBUG END ===")
    
    return result

def debug_ai_processing(text, nlp_result):
    """Debug AI processing with detailed logs"""
    print(f"🤖 === AI DEBUG START ===")
    print(f"🤖 Input Text: '{text}'")
    print(f"🤖 NLP Intent: {nlp_result.get('intent', 'unknown')}")
    print(f"🤖 NLP Confidence: {nlp_result.get('confidence', 0)}")
    
    try:
        if 'GROQ_API_KEY' not in api_keys:
            print("❌ No GROQ API key found")
            return {"success": False, "response": "API key not configured", "debug": "no_api_key"}
        
        print(f"🤖 Using GROQ API key: {api_keys['GROQ_API_KEY'][:10]}...")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_keys['GROQ_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        intent = nlp_result.get('intent', 'general_farming')
        
        system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं।

Intent: {intent}

जवाब देने का तरीका:
- हिंदी में स्पष्ट जवाब दें
- 2-3 वाक्य में संक्षिप्त रखें
- व्यावहारिक सलाह दें
- "भाई" या "जी" का प्रयोग करें"""

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        print(f"🤖 Making API request to: {url}")
        print(f"🤖 Payload model: {payload['model']}")
        print(f"🤖 Payload messages count: {len(payload['messages'])}")
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        print(f"🤖 API Response Status: {response.status_code}")
        print(f"🤖 API Response Time: {response_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 API Response Keys: {list(result.keys())}")
            
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result["choices"][0]["message"]["content"].strip()
                print(f"🤖 AI Response Length: {len(ai_response)} characters")
                print(f"🤖 AI Response: '{ai_response}'")
                
                final_result = {
                    "success": True,
                    "response": ai_response,
                    "response_time": response_time,
                    "debug": {
                        "api_status": response.status_code,
                        "response_length": len(ai_response),
                        "intent_used": intent
                    }
                }
                
                print(f"🤖 === AI DEBUG END (SUCCESS) ===")
                return final_result
            else:
                print("❌ No choices in API response")
                return {"success": False, "response": "No AI response generated", "debug": "no_choices"}
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"❌ API Error Text: {response.text}")
            return {"success": False, "response": f"API Error: {response.status_code}", "debug": "api_error"}
            
    except Exception as e:
        print(f"❌ AI Exception: {e}")
        print(f"🤖 === AI DEBUG END (ERROR) ===")
        return {"success": False, "response": f"Error: {str(e)}", "debug": "exception"}

@app.route('/')
def index():
    """Debug flow interface"""
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔍 Debug Flow System</title>
        
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
                max-width: 900px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 40px;
                text-align: center;
                color: #333;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            
            h1 { color: #2c3e50; margin-bottom: 10px; }
            
            .debug-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                text-align: left;
            }
            
            .step {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
            }
            
            .step h4 { margin: 0 0 10px 0; color: #495057; }
            .step-status { font-size: 20px; float: right; }
            
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
            
            .btn.primary { background: #007bff; color: white; }
            .btn:hover { transform: translateY(-2px); }
            
            .debug-log {
                background: #343a40;
                color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                font-family: monospace;
                font-size: 12px;
                max-height: 300px;
                overflow-y: auto;
                text-align: left;
            }
            
            .test-input {
                width: 70%;
                padding: 10px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-right: 10px;
            }
            
            .result {
                background: #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Debug Flow System</h1>
            <p>Complete Input/Output Flow Tracking</p>
            
            <div class="debug-section">
                <h3>🧪 Test Complete Flow:</h3>
                <input type="text" id="testInput" class="test-input" placeholder="Type: गेहूं के लिए खाद की सलाह दो">
                <button class="btn primary" onclick="testCompleteFlow()">Test Flow</button>
                <div id="testResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="debug-section">
                <h3>🔄 Flow Steps:</h3>
                <div class="step">
                    <h4>Step 1: Input Validation</h4>
                    <div class="step-status" id="step1">⏳</div>
                    <div id="step1-details"></div>
                </div>
                <div class="step">
                    <h4>Step 2: NLP Processing</h4>
                    <div class="step-status" id="step2">⏳</div>
                    <div id="step2-details"></div>
                </div>
                <div class="step">
                    <h4>Step 3: AI Processing</h4>
                    <div class="step-status" id="step3">⏳</div>
                    <div id="step3-details"></div>
                </div>
                <div class="step">
                    <h4>Step 4: Response Delivery</h4>
                    <div class="step-status" id="step4">⏳</div>
                    <div id="step4-details"></div>
                </div>
            </div>
            
            <div class="debug-log" id="debugLog">
                Debug logs will appear here...
            </div>
        </div>
        
        <script>
            function log(message) {
                const debugEl = document.getElementById('debugLog');
                const timestamp = new Date().toLocaleTimeString();
                debugEl.innerHTML += `[${timestamp}] ${message}\\n`;
                debugEl.scrollTop = debugEl.scrollHeight;
                console.log(`[DEBUG] ${message}`);
            }
            
            function updateStep(stepNum, status, details = '') {
                document.getElementById(`step${stepNum}`).textContent = status;
                document.getElementById(`step${stepNum}-details`).innerHTML = details;
            }
            
            async function testCompleteFlow() {
                const query = document.getElementById('testInput').value.trim();
                if (!query) {
                    document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                    return;
                }
                
                log(`🧪 Starting complete flow test with: "${query}"`);
                document.getElementById('testResult').style.display = 'block';
                document.getElementById('testResult').innerHTML = '<div style="color: #007bff;">🔄 Testing complete flow...</div>';
                
                // Reset steps
                for (let i = 1; i <= 4; i++) {
                    updateStep(i, '⏳', '');
                }
                
                try {
                    // Step 1: Input validation
                    updateStep(1, '🔄', 'Validating input...');
                    log(`✅ Step 1: Input validation passed`);
                    updateStep(1, '✅', `Input: "${query}" (${query.length} chars)`);
                    
                    // Step 2-4: API call
                    updateStep(2, '🔄', 'Calling API...');
                    updateStep(3, '🔄', 'Waiting for response...');
                    
                    const response = await fetch('/api/debug-flow', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    log(`📡 API response status: ${response.status}`);
                    const result = await response.json();
                    log(`📦 API response: ${JSON.stringify(result, null, 2)}`);
                    
                    // Update steps based on result
                    if (result.nlp_result) {
                        updateStep(2, '✅', `Intent: ${result.nlp_result.intent} (${result.nlp_result.confidence})`);
                        log(`✅ Step 2: NLP completed - ${result.nlp_result.intent}`);
                    } else {
                        updateStep(2, '❌', 'NLP processing failed');
                        log(`❌ Step 2: NLP failed`);
                    }
                    
                    if (result.ai_result && result.ai_result.success) {
                        updateStep(3, '✅', `Response: ${result.ai_result.response.substring(0, 50)}...`);
                        log(`✅ Step 3: AI completed successfully`);
                    } else {
                        updateStep(3, '❌', `AI Error: ${result.ai_result?.response || 'Unknown error'}`);
                        log(`❌ Step 3: AI failed - ${result.ai_result?.response || 'Unknown error'}`);
                    }
                    
                    if (result.success) {
                        updateStep(4, '✅', 'Response delivered successfully');
                        log(`✅ Step 4: Response delivered`);
                        
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #d4edda; padding: 15px; border-radius: 8px; color: #155724;">
                                <h4>✅ Complete Flow Success!</h4>
                                <p><strong>Intent:</strong> ${result.nlp_result.intent} (${result.nlp_result.confidence})</p>
                                <p><strong>AI Response:</strong> ${result.ai_result.response}</p>
                                <p><strong>Response Time:</strong> ${result.ai_result.response_time?.toFixed(2)}s</p>
                            </div>`;
                    } else {
                        updateStep(4, '❌', 'Flow failed');
                        log(`❌ Step 4: Flow failed`);
                        
                        document.getElementById('testResult').innerHTML = 
                            `<div style="background: #f8d7da; padding: 15px; border-radius: 8px; color: #721c24;">
                                <h4>❌ Flow Failed!</h4>
                                <p><strong>Error:</strong> ${result.error || 'Unknown error'}</p>
                            </div>`;
                    }
                    
                } catch (error) {
                    log(`❌ Network error: ${error.message}`);
                    updateStep(4, '❌', `Network error: ${error.message}`);
                    
                    document.getElementById('testResult').innerHTML = 
                        `<div style="background: #f8d7da; padding: 15px; border-radius: 8px; color: #721c24;">
                            <h4>❌ Network Error!</h4>
                            <p>${error.message}</p>
                        </div>`;
                }
            }
            
            // Auto-test on load
            window.onload = function() {
                log('🚀 Debug flow system initialized');
                document.getElementById('testInput').value = 'गेहूं के लिए खाद की सलाह दो';
                setTimeout(testCompleteFlow, 1000);
            };
        </script>
    </body>
    </html>
    """

@app.route('/api/debug-flow', methods=['POST'])
def debug_complete_flow():
    """Debug complete flow with detailed tracking"""
    print("🔍 === DEBUG FLOW API CALLED ===")
    
    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()
        
        print(f"🔍 Input received: '{user_input}'")
        print(f"🔍 Input length: {len(user_input)} characters")
        
        if not user_input:
            print("❌ Empty input")
            return jsonify({"success": False, "error": "Empty input", "step": "input_validation"})
        
        # Step 1: NLP Processing
        print("🔍 Starting NLP processing...")
        nlp_result = debug_nlp_processing(user_input)
        print(f"🔍 NLP completed: {nlp_result}")
        
        # Step 2: AI Processing
        print("🔍 Starting AI processing...")
        ai_result = debug_ai_processing(user_input, nlp_result)
        print(f"🔍 AI completed: {ai_result['success']}")
        
        # Final result
        final_result = {
            "success": ai_result["success"],
            "nlp_result": nlp_result,
            "ai_result": ai_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if not ai_result["success"]:
            final_result["error"] = ai_result["response"]
        
        print(f"🔍 Final result success: {final_result['success']}")
        print("🔍 === DEBUG FLOW API END ===")
        
        return jsonify(final_result)
        
    except Exception as e:
        print(f"❌ Debug flow error: {e}")
        return jsonify({"success": False, "error": str(e), "step": "exception"})

if __name__ == '__main__':
    print("🔍 Starting Debug Flow System...")
    print("🌾 Complete Input/Output Flow Tracking")
    print("=" * 60)
    
    print(f"✅ API Keys: {len(api_keys)} loaded")
    
    print(f"\n🚀 Starting debug server...")
    print(f"🌐 URL: http://localhost:5011")
    print(f"💡 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5011)
