#!/usr/bin/env python3
"""
Comprehensive test for CSV-based Farmer Intent Detection System
"""

import json
from csv_based_intent_detector import CSVBasedFarmerIntentDetector


def test_csv_intent_detection():
    """Test CSV-based intent detection with comprehensive test cases"""
    detector = CSVBasedFarmerIntentDetector()
    
    # Comprehensive test cases covering all major intents
    test_cases = [
        # Seed Inquiry
        {
            "input": "मुझे बीज की जानकारी चाहिए",
            "expected_intent": "seed_inquiry",
            "description": "Direct seed inquiry"
        },
        {
            "input": "गेहूं के बीज कहाँ मिलेंगे",
            "expected_intent": "seed_inquiry",
            "description": "Wheat seed inquiry"
        },
        {
            "input": "बीज की जानकारी कैसे करें",
            "expected_intent": "seed_inquiry",
            "description": "How to get seed information"
        },
        
        # Fertilizer Advice
        {
            "input": "खाद की जानकारी दो",
            "expected_intent": "fertilizer_advice",
            "description": "Direct fertilizer inquiry"
        },
        {
            "input": "गेहूं के लिए कौन सी खाद अच्छी है",
            "expected_intent": "fertilizer_advice",
            "description": "Wheat fertilizer advice"
        },
        {
            "input": "उर्वरक की सलाह चाहिए",
            "expected_intent": "fertilizer_advice",
            "description": "Fertilizer advice needed"
        },
        
        # Crop Disease
        {
            "input": "फसल में कीड़े लग गए हैं",
            "expected_intent": "crop_disease",
            "description": "Pest problem"
        },
        {
            "input": "कीटनाशक से जुड़ी समस्या है",
            "expected_intent": "crop_disease",
            "description": "Pesticide related problem"
        },
        {
            "input": "फसल की बीमारी का इलाज",
            "expected_intent": "crop_disease",
            "description": "Crop disease treatment"
        },
        
        # Market Price
        {
            "input": "आज मंडी में भाव क्या है",
            "expected_intent": "market_price",
            "description": "Today's market price"
        },
        {
            "input": "मंडी भाव पूछना है",
            "expected_intent": "market_price",
            "description": "Want to ask market price"
        },
        {
            "input": "गेहूं का दाम क्या है",
            "expected_intent": "market_price",
            "description": "Wheat price inquiry"
        },
        
        # Mixed Language
        {
            "input": "मुझे seed की जानकारी चाहिए",
            "expected_intent": "seed_inquiry",
            "description": "Mixed Hindi-English seed"
        },
        {
            "input": "fertilizer के बारे में बताओ",
            "expected_intent": "fertilizer_advice",
            "description": "Mixed Hindi-English fertilizer"
        },
        {
            "input": "crop में disease है",
            "expected_intent": "crop_disease",
            "description": "Mixed Hindi-English disease"
        },
        
        # Edge Cases
        {
            "input": "हैलो",
            "expected_intent": "unknown",
            "description": "Greeting - should be unknown"
        },
        {
            "input": "मौसम कैसा है",
            "expected_intent": "unknown",
            "description": "Weather query - not in main intents"
        },
        {
            "input": "धन्यवाद",
            "expected_intent": "unknown",
            "description": "Thank you - should be unknown"
        }
    ]
    
    print("🧪 Testing CSV-based Farmer Intent Detection System")
    print("=" * 70)
    
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected_intent = test_case["expected_intent"]
        description = test_case["description"]
        
        print(f"\n📝 Test {i}/{total_tests}: {description}")
        print(f"   Input: {input_text}")
        
        # Run detection
        result = detector.detect_intent(input_text)
        
        # Check result
        detected_intent = result["intent"]
        confidence = result["confidence"]
        
        print(f"   Expected: {expected_intent}")
        print(f"   Detected: {detected_intent}")
        print(f"   Confidence: {confidence:.3f}")
        
        # Verify intent
        test_passed = detected_intent == expected_intent
        
        if test_passed:
            print("   ✅ PASSED")
            passed_tests += 1
        else:
            print("   ❌ FAILED")
            failed_tests.append({
                "test_number": i,
                "description": description,
                "input": input_text,
                "expected": expected_intent,
                "detected": detected_intent,
                "confidence": confidence
            })
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {len(failed_tests)}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  Test {failure['test_number']}: {failure['description']}")
            print(f"    Input: {failure['input']}")
            print(f"    Expected: {failure['expected']}")
            print(f"    Got: {failure['detected']} (confidence: {failure['confidence']:.3f})")
    
    # Show conversation summary
    print(f"\n📈 Conversation Summary:")
    summary = detector.get_conversation_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    return passed_tests, total_tests


def test_performance_benchmark():
    """Test performance with multiple queries"""
    import time
    
    print("\n⚡ Performance Benchmark")
    print("=" * 50)
    
    detector = CSVBasedFarmerIntentDetector()
    
    test_queries = [
        "मुझे बीज की जानकारी चाहिए",
        "खाद की सलाह दो",
        "फसल में कीड़े हैं",
        "मंडी भाव क्या है",
        "गेहूं के लिए fertilizer"
    ] * 50  # 250 total queries
    
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


def test_entity_extraction():
    """Test entity extraction capabilities"""
    print("\n🏷️ Entity Extraction Test")
    print("=" * 50)
    
    detector = CSVBasedFarmerIntentDetector()
    
    entity_test_cases = [
        {
            "input": "गेहूं के लिए 50 किलो खाद चाहिए",
            "expected_crops": ["wheat"],
            "expected_quantities": ["50 किलो"]
        },
        {
            "input": "आज धान में कीड़े लग गए हैं",
            "expected_crops": ["rice"],
            "expected_time": ["आज"]
        },
        {
            "input": "कल मक्का का भाव देखना है",
            "expected_crops": ["corn"],
            "expected_time": ["कल"]
        }
    ]
    
    for i, test_case in enumerate(entity_test_cases, 1):
        input_text = test_case["input"]
        result = detector.detect_intent(input_text)
        entities = result["entities"]
        
        print(f"\n📝 Entity Test {i}: {input_text}")
        print(f"   Detected Entities: {entities}")
        
        # Check crops
        if "expected_crops" in test_case:
            expected_crops = test_case["expected_crops"]
            detected_crops = entities.get("crops", [])
            crops_match = all(crop in detected_crops for crop in expected_crops)
            print(f"   Crops: Expected {expected_crops}, Got {detected_crops} {'✅' if crops_match else '❌'}")
        
        # Check quantities
        if "expected_quantities" in test_case:
            expected_quantities = test_case["expected_quantities"]
            detected_quantities = entities.get("quantities", [])
            quantities_match = len(detected_quantities) > 0
            print(f"   Quantities: Expected {expected_quantities}, Got {detected_quantities} {'✅' if quantities_match else '❌'}")
        
        # Check time
        if "expected_time" in test_case:
            expected_time = test_case["expected_time"]
            detected_time = entities.get("time", [])
            time_match = len(detected_time) > 0
            print(f"   Time: Expected {expected_time}, Got {detected_time} {'✅' if time_match else '❌'}")


def main():
    """Run all tests"""
    print("🌾 CSV-based Farmer NLP System - Comprehensive Testing")
    print("=" * 80)
    
    try:
        # Test 1: Intent Detection
        passed, total = test_csv_intent_detection()
        
        # Test 2: Performance Benchmark
        test_performance_benchmark()
        
        # Test 3: Entity Extraction
        test_entity_extraction()
        
        print(f"\n🎉 All Tests Completed!")
        print(f"📊 Overall Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("✅ All tests passed! CSV-based system is ready for production.")
        else:
            print("⚠️ Some tests failed. System needs improvement.")
            
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")


if __name__ == "__main__":
    main()
