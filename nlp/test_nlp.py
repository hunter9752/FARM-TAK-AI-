#!/usr/bin/env python3
"""
Test script for Farmer NLP Intent Detection System
"""

import json
from farmer_intent_detector import FarmerIntentDetector


def test_intent_detection():
    """Test intent detection with various farmer queries"""
    detector = FarmerIntentDetector()
    
    # Comprehensive test cases
    test_cases = [
        # Crop Planting
        {
            "input": "मुझे गेहूं बोना है",
            "expected_intent": "crop_planting",
            "expected_entities": ["wheat"]
        },
        {
            "input": "I want to plant rice in my field",
            "expected_intent": "crop_planting", 
            "expected_entities": ["rice"]
        },
        {
            "input": "कब मक्का की बुआई करनी चाहिए",
            "expected_intent": "crop_planting",
            "expected_entities": ["corn"]
        },
        
        # Crop Disease
        {
            "input": "मेरी फसल में कीड़े लग गए हैं",
            "expected_intent": "crop_disease",
            "expected_entities": []
        },
        {
            "input": "टमाटर के पौधे में बीमारी है",
            "expected_intent": "crop_disease",
            "expected_entities": ["tomato"]
        },
        
        # Weather Inquiry
        {
            "input": "आज मौसम कैसा है",
            "expected_intent": "weather_inquiry",
            "expected_entities": []
        },
        {
            "input": "कल बारिश होगी क्या",
            "expected_intent": "weather_inquiry",
            "expected_entities": []
        },
        
        # Market Price
        {
            "input": "गेहूं का भाव क्या है",
            "expected_intent": "market_price",
            "expected_entities": ["wheat"]
        },
        {
            "input": "आज मंडी में प्याज का दाम",
            "expected_intent": "market_price",
            "expected_entities": ["onion"]
        },
        
        # Irrigation
        {
            "input": "कब सिंचाई करनी चाहिए",
            "expected_intent": "irrigation_need",
            "expected_entities": []
        },
        {
            "input": "धान में पानी कब देना है",
            "expected_intent": "irrigation_need",
            "expected_entities": ["rice"]
        },
        
        # Fertilizer Advice
        {
            "input": "गेहूं के लिए कौन सी खाद अच्छी है",
            "expected_intent": "fertilizer_advice",
            "expected_entities": ["wheat"]
        },
        {
            "input": "What fertilizer should I use for corn",
            "expected_intent": "fertilizer_advice",
            "expected_entities": ["corn"]
        },
        
        # Government Schemes
        {
            "input": "किसान योजना के बारे में बताओ",
            "expected_intent": "government_scheme",
            "expected_entities": []
        },
        {
            "input": "सब्सिडी कैसे मिलती है",
            "expected_intent": "government_scheme",
            "expected_entities": []
        },
        
        # Mixed Language
        {
            "input": "मुझे wheat plant करना है",
            "expected_intent": "crop_planting",
            "expected_entities": ["wheat"]
        },
        {
            "input": "Rice का price क्या है",
            "expected_intent": "market_price",
            "expected_entities": ["rice"]
        },
        
        # Edge Cases
        {
            "input": "हैलो",
            "expected_intent": "unknown",
            "expected_entities": []
        },
        {
            "input": "मुझे मदद चाहिए",
            "expected_intent": "general_help",
            "expected_entities": []
        }
    ]
    
    print("🧪 Testing Farmer Intent Detection System")
    print("=" * 60)
    
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected_intent = test_case["expected_intent"]
        expected_entities = test_case.get("expected_entities", [])
        
        print(f"\n📝 Test {i}/{total_tests}: {input_text}")
        
        # Run detection
        result = detector.detect_intent(input_text)
        
        # Check intent
        detected_intent = result["intent"]
        confidence = result["confidence"]
        detected_entities = result["entities"]
        
        print(f"🎯 Expected: {expected_intent}")
        print(f"🎯 Detected: {detected_intent}")
        print(f"📊 Confidence: {confidence:.2f}")
        
        # Verify intent
        intent_correct = detected_intent == expected_intent
        
        # Verify entities (check if expected entities are found)
        entities_correct = True
        if expected_entities:
            detected_crops = detected_entities.get("crops", [])
            for expected_entity in expected_entities:
                if expected_entity not in detected_crops:
                    entities_correct = False
                    break
        
        # Overall test result
        test_passed = intent_correct and entities_correct
        
        if test_passed:
            print("✅ PASSED")
            passed_tests += 1
        else:
            print("❌ FAILED")
            failed_tests.append({
                "test_number": i,
                "input": input_text,
                "expected_intent": expected_intent,
                "detected_intent": detected_intent,
                "expected_entities": expected_entities,
                "detected_entities": detected_entities
            })
        
        print("-" * 40)
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {len(failed_tests)}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  Test {failure['test_number']}: {failure['input']}")
            print(f"    Expected: {failure['expected_intent']}")
            print(f"    Got: {failure['detected_intent']}")
    
    return passed_tests, total_tests


def test_response_generation():
    """Test response generation for different intents"""
    from integrated_farmer_assistant import IntegratedFarmerAssistant
    
    print("\n🗣️ Testing Response Generation")
    print("=" * 60)
    
    # Create assistant (without STT initialization)
    assistant = IntegratedFarmerAssistant.__new__(IntegratedFarmerAssistant)
    assistant.nlp = FarmerIntentDetector()
    assistant.setup_response_database()
    
    test_queries = [
        "गेहूं बोना है",
        "धान में बीमारी है", 
        "मक्का का भाव क्या है",
        "खाद की सलाह चाहिए",
        "सरकारी योजना बताओ"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        # Detect intent
        intent_result = assistant.nlp.detect_intent(query)
        
        # Generate response
        response = assistant.get_detailed_response(intent_result)
        
        print(f"🎯 Intent: {intent_result['intent']}")
        print(f"📊 Confidence: {intent_result['confidence']:.2f}")
        print(f"💬 Response: {response}")
        print("-" * 40)


def test_conversation_flow():
    """Test conversation flow and context tracking"""
    print("\n💬 Testing Conversation Flow")
    print("=" * 60)
    
    detector = FarmerIntentDetector()
    
    conversation = [
        "मुझे गेहूं बोना है",
        "कब बोना चाहिए",
        "कितनी खाद देनी होगी",
        "मंडी में भाव क्या है",
        "धन्यवाद"
    ]
    
    for i, query in enumerate(conversation, 1):
        print(f"\n👤 User {i}: {query}")
        result = detector.detect_intent(query)
        print(f"🤖 Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
    
    # Show conversation summary
    summary = detector.get_conversation_summary()
    print(f"\n📈 Conversation Summary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def benchmark_performance():
    """Benchmark system performance"""
    import time
    
    print("\n⚡ Performance Benchmark")
    print("=" * 60)
    
    detector = FarmerIntentDetector()
    
    test_queries = [
        "गेहूं बोना है",
        "मौसम कैसा है", 
        "फसल में कीड़े हैं",
        "भाव क्या है",
        "खाद चाहिए"
    ] * 20  # 100 total queries
    
    start_time = time.time()
    
    for query in test_queries:
        detector.detect_intent(query)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_queries)
    
    print(f"📊 Performance Results:")
    print(f"   Total Queries: {len(test_queries)}")
    print(f"   Total Time: {total_time:.2f} seconds")
    print(f"   Average Time: {avg_time*1000:.2f} ms per query")
    print(f"   Queries per Second: {len(test_queries)/total_time:.1f}")


def main():
    """Run all tests"""
    print("🌾 Farmer NLP System - Comprehensive Testing")
    print("=" * 80)
    
    try:
        # Test 1: Intent Detection
        passed, total = test_intent_detection()
        
        # Test 2: Response Generation
        test_response_generation()
        
        # Test 3: Conversation Flow
        test_conversation_flow()
        
        # Test 4: Performance Benchmark
        benchmark_performance()
        
        print(f"\n🎉 All Tests Completed!")
        print(f"📊 Overall Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("✅ All tests passed! System is ready for production.")
        else:
            print("⚠️ Some tests failed. Please review and improve the system.")
            
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")


if __name__ == "__main__":
    main()
