#!/usr/bin/env python3
"""
Test API keys are working
"""

import os
import requests
import time


def load_env():
    """Load .env file manually"""
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
                            print(f"  Loaded: {key} = {value[:20]}...")
        except Exception as e:
            print(f"Error loading .env: {e}")
            # Try with different encoding
            try:
                with open('.env', 'r', encoding='cp1252') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if value and value != "your_api_key_here":
                                os.environ[key] = value
                                print(f"  Loaded: {key} = {value[:20]}...")
            except Exception as e2:
                print(f"Error with cp1252: {e2}")


def test_groq():
    """Test Groq API"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return False, "No API key"
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "आप एक कृषि विशेषज्ञ हैं।"},
                {"role": "user", "content": "गेहूं के लिए खाद की सलाह दें।"}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        start = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        duration = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return True, f"Success! ({duration:.1f}s) - {answer[:100]}..."
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"


def test_openai():
    """Test OpenAI API"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return False, "No API key"
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "आप एक कृषि विशेषज्ञ हैं।"},
                {"role": "user", "content": "गेहूं के लिए खाद की सलाह दें।"}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        start = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        duration = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return True, f"Success! ({duration:.1f}s) - {answer[:100]}..."
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"


def main():
    """Test all APIs"""
    print("🌐 Testing Cloud LLM APIs")
    print("=" * 50)
    
    # Load environment
    load_env()
    
    # Test Groq
    print("\n🧪 Testing Groq API...")
    groq_success, groq_msg = test_groq()
    print(f"Groq: {'✅' if groq_success else '❌'} {groq_msg}")
    
    # Test OpenAI
    print("\n🧪 Testing OpenAI API...")
    openai_success, openai_msg = test_openai()
    print(f"OpenAI: {'✅' if openai_success else '❌'} {openai_msg}")
    
    # Summary
    print(f"\n📊 Results:")
    print(f"Groq: {'✅ Working' if groq_success else '❌ Failed'}")
    print(f"OpenAI: {'✅ Working' if openai_success else '❌ Failed'}")
    
    if groq_success or openai_success:
        print("\n🎉 At least one API is working!")
        print("💡 You can now use the cloud LLM system")
        
        if groq_success:
            print("🌟 Groq is working - this is the fastest option!")
        if openai_success:
            print("🌟 OpenAI is working - this gives highest quality!")
    else:
        print("\n❌ No APIs working")
        print("💡 Please check your API keys")


if __name__ == "__main__":
    main()
