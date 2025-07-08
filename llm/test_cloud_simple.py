#!/usr/bin/env python3
"""
Simple test for Cloud LLM without NLP dependency
"""

import os
import json
import requests
import time


def load_env_file():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            loaded_count = 0
            with open(env_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
                            loaded_count += 1
                            print(f"  Loaded: {key} = {value[:20]}...")
                        elif "API_KEY" in key:
                            print(f"  Skipped empty: {key}")
            print(f"✅ Loaded {loaded_count} environment variables from .env file")
            return True
        except Exception as e:
            print(f"⚠️ Could not load .env file: {e}")
            return False
    else:
        print("💡 No .env file found")
        return False


def test_openai_api():
    """Test OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found")
        return False
    
    print("🧪 Testing OpenAI API...")
    
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
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            print("✅ OpenAI API working!")
            print(f"⏱️ Response Time: {response_time:.2f}s")
            print(f"💬 Response: {llm_response}")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False


def test_huggingface_api():
    """Test Hugging Face API"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ No Hugging Face API key found")
        return False
    
    print("🧪 Testing Hugging Face API...")
    
    try:
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": "गेहूं के लिए खाद की सलाह दें।",
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hugging Face API working!")
            print(f"⏱️ Response Time: {response_time:.2f}s")
            print(f"💬 Response: {result}")
            return True
        else:
            print(f"❌ Hugging Face API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Hugging Face API test failed: {e}")
        return False


def main():
    """Test cloud LLM APIs"""
    print("🌐 Cloud LLM API Test")
    print("=" * 50)
    
    # Load environment
    load_env_file()
    
    # Test available APIs
    openai_works = test_openai_api()
    print()
    huggingface_works = test_huggingface_api()
    
    print("\n📊 Test Results:")
    print(f"OpenAI: {'✅ Working' if openai_works else '❌ Failed'}")
    print(f"Hugging Face: {'✅ Working' if huggingface_works else '❌ Failed'}")
    
    if openai_works or huggingface_works:
        print("\n🎉 At least one API is working!")
        print("💡 You can now use the cloud LLM system")
    else:
        print("\n❌ No APIs working")
        print("💡 Please check your API keys in .env file")


if __name__ == "__main__":
    main()
