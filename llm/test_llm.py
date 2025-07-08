#!/usr/bin/env python3
"""
Test script for Farmer LLM Assistant
"""

import sys
import os
import time
import json

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nlp'))

try:
    from farmer_llm_assistant import FarmerLLMAssistant
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_llm_basic_functionality():
    """Test basic LLM functionality"""
    print("🧪 Testing LLM Basic Functionality")
    print("=" * 50)
    
    try:
        assistant = FarmerLLMAssistant()
        print("✅ LLM Assistant initialized successfully")
        return True
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return False


def test_farmer_queries():
    """Test LLM with various farmer queries"""
    print("\n🌾 Testing Farmer Queries")
    print("=" * 50)
    
    assistant = FarmerLLMAssistant()
    
    test_queries = [
        {
            "query": "मुझे गेहूं के लिए खाद की सलाह चाहिए",
            "expected_intent": "fertilizer_advice",
            "expected_keywords": ["खाद", "उर्वरक", "NPK", "गेहूं"]
        },
        {
            "query": "फसल में कीड़े लग गए हैं",
            "expected_intent": "crop_disease", 
            "expected_keywords": ["कीड़े", "कीटनाशक", "छिड़काव", "दवाई"]
        },
        {
            "query": "बीज की जानकारी चाहिए",
            "expected_intent": "seed_inquiry",
            "expected_keywords": ["बीज", "किस्म", "बुआई"]
        },
        {
            "query": "मंडी भाव क्या है",
            "expected_intent": "market_price",
            "expected_keywords": ["भाव", "मंडी", "कीमत", "eNAM"]
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_queries)
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\n📝 Test {i}/{total_tests}: {query}")
        
        try:
            # Process query
            start_time = time.time()
            result = assistant.process_farmer_query(query)
            response_time = time.time() - start_time
            
            # Extract results
            nlp_result = result["nlp_result"]
            llm_response = result["llm_response"]
            detected_intent = nlp_result["intent"]
            confidence = nlp_result["confidence"]
            
            print(f"🎯 Detected Intent: {detected_intent}")
            print(f"📊 Confidence: {confidence:.2f}")
            print(f"⏱️ Response Time: {response_time:.2f}s")
            print(f"💬 LLM Response: {llm_response}")
            
            # Validate results
            intent_correct = detected_intent == expected_intent
            keywords_found = any(keyword in llm_response.lower() for keyword in expected_keywords)
            response_length_ok = 50 <= len(llm_response) <= 500
            response_time_ok = response_time <= 10.0
            
            # Overall test result
            test_passed = intent_correct and keywords_found and response_length_ok and response_time_ok
            
            if test_passed:
                print("✅ PASSED")
                passed_tests += 1
            else:
                print("❌ FAILED")
                if not intent_correct:
                    print(f"   Intent mismatch: expected {expected_intent}, got {detected_intent}")
                if not keywords_found:
                    print(f"   Missing expected keywords: {expected_keywords}")
                if not response_length_ok:
                    print(f"   Response length issue: {len(llm_response)} characters")
                if not response_time_ok:
                    print(f"   Response too slow: {response_time:.2f}s")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print("-" * 40)
    
    # Summary
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    return passed_tests, total_tests


def test_response_quality():
    """Test LLM response quality"""
    print("\n📝 Testing Response Quality")
    print("=" * 50)
    
    assistant = FarmerLLMAssistant()
    
    quality_tests = [
        {
            "query": "गेहूं में पीले पत्ते हो रहे हैं",
            "quality_checks": {
                "contains_hindi": True,
                "actionable_advice": True,
                "technical_accuracy": True,
                "appropriate_length": True
            }
        },
        {
            "query": "धान की रोपाई कब करें",
            "quality_checks": {
                "contains_hindi": True,
                "mentions_timing": True,
                "practical_advice": True,
                "appropriate_length": True
            }
        }
    ]
    
    for i, test_case in enumerate(quality_tests, 1):
        query = test_case["query"]
        quality_checks = test_case["quality_checks"]
        
        print(f"\n📝 Quality Test {i}: {query}")
        
        try:
            result = assistant.process_farmer_query(query)
            response = result["llm_response"]
            
            print(f"💬 Response: {response}")
            
            # Quality checks
            checks_passed = 0
            total_checks = len(quality_checks)
            
            # Check Hindi content
            if quality_checks.get("contains_hindi"):
                has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in response)
                if has_hindi:
                    print("✅ Contains Hindi text")
                    checks_passed += 1
                else:
                    print("❌ Missing Hindi text")
            
            # Check length
            if quality_checks.get("appropriate_length"):
                length_ok = 50 <= len(response) <= 300
                if length_ok:
                    print(f"✅ Appropriate length ({len(response)} chars)")
                    checks_passed += 1
                else:
                    print(f"❌ Length issue ({len(response)} chars)")
            
            # Check for actionable advice
            if quality_checks.get("actionable_advice"):
                actionable_words = ["करें", "दें", "डालें", "छिड़काव", "प्रयोग"]
                has_actionable = any(word in response for word in actionable_words)
                if has_actionable:
                    print("✅ Contains actionable advice")
                    checks_passed += 1
                else:
                    print("❌ Missing actionable advice")
            
            quality_score = (checks_passed / total_checks) * 100
            print(f"📊 Quality Score: {quality_score:.1f}%")
            
        except Exception as e:
            print(f"❌ Quality test failed: {e}")
        
        print("-" * 40)


def test_performance_benchmark():
    """Test LLM performance under load"""
    print("\n⚡ Performance Benchmark")
    print("=" * 50)
    
    assistant = FarmerLLMAssistant()
    
    test_queries = [
        "गेहूं की खेती कैसे करें",
        "फसल में रोग है",
        "बीज कहाँ मिलेगा",
        "मंडी भाव बताओ",
        "खाद की सलाह दो"
    ]
    
    total_queries = len(test_queries) * 3  # Run each query 3 times
    response_times = []
    successful_responses = 0
    
    print(f"🔄 Running {total_queries} queries...")
    
    start_time = time.time()
    
    for round_num in range(3):
        print(f"\nRound {round_num + 1}:")
        for i, query in enumerate(test_queries):
            try:
                query_start = time.time()
                result = assistant.process_farmer_query(query)
                query_time = time.time() - query_start
                
                response_times.append(query_time)
                successful_responses += 1
                
                print(f"  Query {i+1}: {query_time:.2f}s ✅")
                
            except Exception as e:
                print(f"  Query {i+1}: Failed ❌ ({e})")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        print(f"\n📊 Performance Results:")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Successful Queries: {successful_responses}/{total_queries}")
        print(f"   Success Rate: {(successful_responses/total_queries)*100:.1f}%")
        print(f"   Average Response Time: {avg_response_time:.2f}s")
        print(f"   Min Response Time: {min_response_time:.2f}s")
        print(f"   Max Response Time: {max_response_time:.2f}s")
        print(f"   Queries per Minute: {(successful_responses/total_time)*60:.1f}")
    else:
        print("❌ No successful responses to analyze")


def main():
    """Run all LLM tests"""
    print("🤖 Farmer LLM Assistant - Comprehensive Testing")
    print("=" * 80)
    
    try:
        # Test 1: Basic functionality
        if not test_llm_basic_functionality():
            print("❌ Basic functionality test failed. Stopping tests.")
            return
        
        # Test 2: Farmer queries
        passed, total = test_farmer_queries()
        
        # Test 3: Response quality
        test_response_quality()
        
        # Test 4: Performance benchmark
        test_performance_benchmark()
        
        print(f"\n🎉 All Tests Completed!")
        print(f"📊 Overall Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("✅ All tests passed! LLM system is ready for production.")
        else:
            print("⚠️ Some tests failed. Please review and improve the system.")
            
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")


if __name__ == "__main__":
    main()
