#!/usr/bin/env python3
"""
🧪 COMPLETE TEST SUITE 🧪
All System Tests for Farmer Voice Agent
"""

import os
import sys
import requests
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_api_connectivity():
    """Test API connectivity"""
    print("🧪 Testing API Connectivity...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Check: {result['status']}")
            print(f"✅ API Key: {result['api_key']}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Connectivity Error: {e}")
        return False

def test_farming_advice_api():
    """Test farming advice API"""
    print("🧪 Testing Farming Advice API...")
    
    test_queries = [
        "गेहूं के लिए खाद की सलाह दो",
        "मेरी फसल में कीड़े लग गए हैं",
        "आज मंडी भाव क्या है",
        "धान कब बोना चाहिए",
        "मिट्टी की जांच कैसे करें"
    ]
    
    passed_tests = 0
    total_tests = len(test_queries)
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"  Test {i}/{total_tests}: {query}")
            
            response = requests.post(
                "http://localhost:5000/api/farming-advice",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✅ Response: {result['response'][:50]}...")
                    passed_tests += 1
                else:
                    print(f"    ❌ API Error: {result.get('error', 'Unknown')}")
            else:
                print(f"    ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
    
    print(f"🧪 Farming Advice API: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

def test_voice_generation_api():
    """Test voice generation API"""
    print("🧪 Testing Voice Generation API...")
    
    test_texts = [
        "नमस्कार भाई!",
        "गेहूं के लिए DAP और यूरिया का इस्तेमाल करें।",
        "कीड़ों के लिए नीम का तेल स्प्रे करें।"
    ]
    
    passed_tests = 0
    total_tests = len(test_texts)
    
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"  Test {i}/{total_tests}: {text[:30]}...")
            
            response = requests.post(
                "http://localhost:5000/api/generate-voice",
                json={"text": text},
                timeout=20
            )
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('audio/'):
                    print(f"    ✅ Audio generated: {len(response.content)} bytes")
                    passed_tests += 1
                else:
                    print(f"    ❌ Invalid content type: {response.headers.get('content-type')}")
            else:
                print(f"    ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
    
    print(f"🧪 Voice Generation API: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

def test_system_performance():
    """Test system performance"""
    print("🧪 Testing System Performance...")
    
    query = "गेहूं के लिए खाद की सलाह दो"
    response_times = []
    
    for i in range(5):
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:5000/api/farming-advice",
                json={"query": query},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"  Test {i+1}/5: {response_time:.2f}s")
            
        except Exception as e:
            print(f"  Test {i+1}/5: Error - {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"🧪 Performance Results:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Maximum: {max_time:.2f}s")
        print(f"  Minimum: {min_time:.2f}s")
        
        # Performance criteria: average < 10s, max < 20s
        performance_ok = avg_time < 10.0 and max_time < 20.0
        print(f"🧪 Performance: {'✅ PASS' if performance_ok else '❌ FAIL'}")
        return performance_ok
    
    return False

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing Error Handling...")
    
    test_cases = [
        {"query": "", "description": "Empty query"},
        {"query": None, "description": "Null query"},
        {"invalid": "data", "description": "Invalid request format"}
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"  Test {i}/{total_tests}: {test_case['description']}")
            
            response = requests.post(
                "http://localhost:5000/api/farming-advice",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('success'):
                    print(f"    ✅ Properly handled error: {result.get('error', 'Unknown')}")
                    passed_tests += 1
                else:
                    print(f"    ❌ Should have failed but succeeded")
            else:
                print(f"    ✅ HTTP Error handled: {response.status_code}")
                passed_tests += 1
                
        except Exception as e:
            print(f"    ✅ Exception handled: {e}")
            passed_tests += 1
    
    print(f"🧪 Error Handling: {passed_tests}/{total_tests} tests passed")
    return passed_tests == total_tests

def run_complete_test_suite():
    """Run complete test suite"""
    print("🌾" + "="*60 + "🌾")
    print("🧪 COMPLETE TEST SUITE - FARMER VOICE AGENT 🧪")
    print("🌾" + "="*60 + "🌾")
    print(f"🕒 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if server is running
    try:
        requests.get("http://localhost:5000", timeout=5)
        print("✅ Server is running on http://localhost:5000")
    except:
        print("❌ Server is not running! Please start the server first.")
        print("   Run: python FINAL_FARMER_VOICE_AGENT.py")
        return False
    
    print()
    
    # Run all tests
    test_results = []
    
    test_results.append(("API Connectivity", test_api_connectivity()))
    test_results.append(("Farming Advice API", test_farming_advice_api()))
    test_results.append(("Voice Generation API", test_voice_generation_api()))
    test_results.append(("System Performance", test_system_performance()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print()
    print("🌾" + "="*60 + "🌾")
    print("📊 TEST RESULTS SUMMARY")
    print("🌾" + "="*60 + "🌾")
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed_count += 1
    
    print()
    print(f"📊 Overall Result: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    print(f"🕒 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌾" + "="*60 + "🌾")
    
    return passed_count == total_count

if __name__ == '__main__':
    success = run_complete_test_suite()
    sys.exit(0 if success else 1)
