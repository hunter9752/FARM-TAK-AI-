#!/usr/bin/env python3
"""
Simple NLP Intent Detector without pandas dependency
For farmer voice call agent
"""

import re
import os
import csv
from collections import defaultdict

class SimpleNLPDetector:
    """Simple NLP intent detector without external dependencies"""
    
    def __init__(self):
        """Initialize simple NLP detector"""
        self.intent_keywords = {
            # Crop related
            'crop_advice': [
                'फसल', 'खेती', 'बुआई', 'बीज', 'किस्म', 'variety', 'crop', 'farming',
                'गेहूं', 'धान', 'मक्का', 'सरसों', 'चना', 'मटर', 'आलू', 'प्याज'
            ],
            
            # Fertilizer related
            'fertilizer_advice': [
                'खाद', 'उर्वरक', 'fertilizer', 'यूरिया', 'डीएपी', 'dap', 'npk',
                'पोषक', 'nutrition', 'compost', 'organic', 'जैविक'
            ],
            
            # Pest control
            'pest_control': [
                'कीड़े', 'कीट', 'pest', 'insect', 'रोग', 'disease', 'बीमारी',
                'दवा', 'medicine', 'spray', 'छिड़काव', 'treatment', 'इलाज'
            ],
            
            # Weather related
            'weather_query': [
                'मौसम', 'weather', 'बारिश', 'rain', 'तापमान', 'temperature',
                'धूप', 'sun', 'ठंड', 'cold', 'गर्मी', 'heat'
            ],
            
            # Market prices
            'market_price': [
                'भाव', 'price', 'दाम', 'rate', 'मंडी', 'market', 'बेचना', 'sell',
                'खरीदना', 'buy', 'cost', 'value'
            ],
            
            # Irrigation
            'irrigation': [
                'पानी', 'water', 'सिंचाई', 'irrigation', 'ड्रिप', 'drip',
                'sprinkler', 'बोरवेल', 'borewell', 'tube well'
            ],
            
            # Soil related
            'soil_advice': [
                'मिट्टी', 'soil', 'भूमि', 'land', 'ph', 'testing', 'जांच',
                'quality', 'गुणवत्ता', 'fertility', 'उर्वरता'
            ],
            
            # General farming
            'general_farming': [
                'किसान', 'farmer', 'agriculture', 'कृषि', 'खेत', 'field',
                'farm', 'cultivation', 'उत्पादन', 'production'
            ]
        }
        
        # Load CSV data if available
        self.load_csv_data()
        
        print("✅ Simple NLP Detector initialized")
    
    def load_csv_data(self):
        """Load CSV data without pandas"""
        try:
            nlp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nlp')
            csv_files = [
                'farmer_intents_dataset.csv',
                'farmer_intents_dataset_2.csv',
                'farmer_intents_dataset_3.csv'
            ]
            
            for csv_file in csv_files:
                file_path = os.path.join(nlp_path, csv_file)
                if os.path.exists(file_path):
                    self.load_single_csv(file_path)
                    print(f"✅ Loaded: {csv_file}")
            
        except Exception as e:
            print(f"⚠️ CSV loading error: {e}")
    
    def load_single_csv(self, file_path):
        """Load single CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract keywords from CSV data
                    if 'query' in row and 'intent' in row:
                        query = row['query'].lower()
                        intent = row['intent']
                        
                        # Add keywords to intent mapping
                        words = re.findall(r'\b\w+\b', query)
                        if intent in self.intent_keywords:
                            self.intent_keywords[intent].extend(words)
                        else:
                            self.intent_keywords[intent] = words
        except Exception as e:
            print(f"⚠️ Error loading {file_path}: {e}")
    
    def detect_intent(self, text):
        """Detect intent from text"""
        text_lower = text.lower()
        
        # Clean text
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Score each intent
        intent_scores = defaultdict(float)
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for word in words:
                if word in keywords:
                    score += 1
            
            # Normalize score
            if len(words) > 0:
                intent_scores[intent] = score / len(words)
        
        # Find best intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # Minimum confidence threshold
            if confidence >= 0.1:
                return {
                    "intent": best_intent,
                    "confidence": confidence,
                    "entities": self.extract_entities(text),
                    "category": self.get_category(best_intent),
                    "method": "simple_keyword_matching"
                }
        
        # Default fallback
        return {
            "intent": "general_farming",
            "confidence": 0.3,
            "entities": {},
            "category": "farming_advice",
            "method": "fallback"
        }
    
    def extract_entities(self, text):
        """Extract entities from text"""
        entities = {}
        text_lower = text.lower()
        
        # Crop entities
        crops = ['गेहूं', 'धान', 'मक्का', 'सरसों', 'चना', 'मटर', 'आलू', 'प्याज']
        for crop in crops:
            if crop in text_lower:
                entities['crop'] = crop
                break
        
        # Fertilizer entities
        fertilizers = ['यूरिया', 'डीएपी', 'dap', 'npk', 'खाद']
        for fert in fertilizers:
            if fert in text_lower:
                entities['fertilizer'] = fert
                break
        
        # Problem entities
        problems = ['कीड़े', 'रोग', 'बीमारी', 'पीले पत्ते']
        for problem in problems:
            if problem in text_lower:
                entities['problem'] = problem
                break
        
        return entities
    
    def get_category(self, intent):
        """Get category for intent"""
        category_mapping = {
            'crop_advice': 'farming_advice',
            'fertilizer_advice': 'input_advice',
            'pest_control': 'problem_solving',
            'weather_query': 'information',
            'market_price': 'market_info',
            'irrigation': 'water_management',
            'soil_advice': 'soil_management',
            'general_farming': 'farming_advice'
        }
        
        return category_mapping.get(intent, 'farming_advice')

# Test function
def test_nlp():
    """Test NLP detector"""
    detector = SimpleNLPDetector()
    
    test_queries = [
        "गेहूं के लिए खाद की सलाह दो",
        "मेरी फसल में कीड़े लग गए हैं",
        "आज मंडी भाव क्या है",
        "धान कब बोना चाहिए",
        "मिट्टी की जांच कैसे करें"
    ]
    
    print("\n🧪 Testing NLP Detector:")
    for query in test_queries:
        result = detector.detect_intent(query)
        print(f"Query: {query}")
        print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        print(f"Entities: {result['entities']}")
        print("-" * 50)

if __name__ == "__main__":
    test_nlp()
