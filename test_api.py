#!/usr/bin/env python3
"""
Test API for Farmer Assistant
Quick test to check if API is working
"""

import requests
import json

def test_api():
    """Test the API"""
    print("🧪 Testing Farmer Assistant API...")
    
    # Test query
    test_query = "गेहूं के लिए खाद की सलाह दो"
    
    try:
        # Make API call
        url = "http://localhost:5000/api/query"
        payload = {"query": test_query}
        
        print(f"📤 Sending request to: {url}")
        print(f"📝 Query: {test_query}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print("🎉 API is working correctly!")
                return True
            else:
                print("❌ API returned error:", result.get("error"))
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    
    try:
        url = "http://localhost:5000/api/stats"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats received:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Stats error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats test failed: {e}")
        return False

if __name__ == "__main__":
    print("🌾 Farmer Assistant API Test")
    print("=" * 50)
    
    # Test main API
    api_success = test_api()
    
    # Test stats
    stats_success = test_stats()
    
    print("\n" + "=" * 50)
    if api_success and stats_success:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("❌ Some tests failed. Check the logs above.")
