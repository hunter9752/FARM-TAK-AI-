#!/usr/bin/env python3
"""
Simple Cloud Farmer Assistant - Direct Groq API
Works without NLP dependency for quick testing
"""

import os
import requests
import time
import json


def load_env():
    """Load .env file"""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and value != "your_api_key_here":
                        os.environ[key] = value


def get_farming_response(user_query):
    """Get farming response from Groq API"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return "❌ No Groq API key found. Please add it to .env file"
    
    # Farmer-specific system prompt
    system_prompt = """आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।
    
आपकी विशेषताएं:
- बीज, खाद, कीटनाशक की सलाह
- फसल रोग की पहचान और इलाज  
- मंडी भाव और बिक्री की सलाह
- मौसम के अनुसार खेती की सलाह
- सरकारी योजनाओं की जानकारी

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
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
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


def display_response(query, result):
    """Display formatted response"""
    print("\n" + "🌾" * 30)
    print("🤖 Cloud Farmer Assistant का जवाब:")
    print("🌾" * 30)
    
    if result["success"]:
        print(f"💬 {result['response']}")
    else:
        print(f"❌ {result['response']}")
    
    print("🌾" * 30)
    print(f"⏱️ Response Time: {result['response_time']:.2f}s")
    print(f"🌐 Provider: {result['provider']}")
    print("-" * 60)


def main():
    """Interactive farmer assistant"""
    print("🌐 Simple Cloud Farmer Assistant")
    print("=" * 60)
    print("💡 Powered by Groq API (Llama 3 70B)")
    print("💡 Type your farming questions in Hindi or English")
    print("💡 Type 'quit' to exit")
    print("=" * 60)
    
    # Load environment
    load_env()
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        print("❌ No Groq API key found!")
        print("💡 Please add GROQ_API_KEY to .env file")
        print("💡 Get free key from: https://console.groq.com/")
        return
    
    print("✅ Groq API key loaded")
    print("🎯 Ready for farming questions!")
    
    while True:
        try:
            # Get user input
            user_input = input("\n🎤 आपका सवाल: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'बाहर', 'बंद']:
                print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                break
            
            if not user_input:
                print("⚠️ कृपया अपना सवाल लिखें।")
                continue
            
            # Get response
            print("🔄 Processing...")
            result = get_farming_response(user_input)
            
            # Display response
            display_response(user_input, result)
            
        except KeyboardInterrupt:
            print("\n\n👋 सिस्टम बंद कर रहे हैं...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
