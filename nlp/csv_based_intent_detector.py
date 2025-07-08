#!/usr/bin/env python3
"""
CSV-based Farmer Intent Detection System
Uses the provided CSV datasets for improved accuracy
"""

import pandas as pd
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import os


class CSVBasedFarmerIntentDetector:
    """Enhanced NLP system using CSV training data"""
    
    def __init__(self):
        """Initialize the CSV-based intent detection system"""
        self.datasets = []
        self.intent_patterns = defaultdict(list)
        self.intent_keywords = defaultdict(set)
        self.intent_mapping = {}
        
        # Load CSV datasets
        self.load_csv_datasets()
        
        # Process datasets
        self.process_datasets()
        
        # Session tracking
        self.conversation_history = []
        self.confidence_threshold = 0.2  # Lowered for better detection
        
        # Setup response database
        self.setup_response_database()
    
    def load_csv_datasets(self):
        """Load all CSV datasets"""
        csv_files = [
            'farmer_intents_dataset.csv',
            'farmer_intents_dataset_2.csv', 
            'farmer_intents_dataset_3.csv'
        ]
        
        for csv_file in csv_files:
            try:
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    self.datasets.append(df)
                    print(f"✅ Loaded {csv_file}: {len(df)} records")
                else:
                    print(f"⚠️ File not found: {csv_file}")
            except Exception as e:
                print(f"❌ Error loading {csv_file}: {e}")
    
    def process_datasets(self):
        """Process CSV datasets to extract patterns and keywords"""
        print("🔄 Processing datasets...")
        
        # Combine all datasets
        all_data = []
        for df in self.datasets:
            all_data.extend(zip(df['intent'], df['message']))
        
        print(f"📊 Total training samples: {len(all_data)}")
        
        # Map Hindi intents to English with additional keywords
        self.intent_mapping = {
            'बीज की जानकारी': 'seed_inquiry',
            'खाद की जानकारी': 'fertilizer_advice',
            'कीटनाशक से जुड़ी समस्या': 'crop_disease',
            'फसल की बीमारी': 'crop_disease',
            'मंडी भाव पूछना': 'market_price'
        }

        # Add direct keyword mapping for better detection
        self.keyword_intent_mapping = {
            'बीज': 'seed_inquiry',
            'seed': 'seed_inquiry',
            'खाद': 'fertilizer_advice',
            'fertilizer': 'fertilizer_advice',
            'उर्वरक': 'fertilizer_advice',
            'कीड़े': 'crop_disease',
            'बीमारी': 'crop_disease',
            'disease': 'crop_disease',
            'pest': 'crop_disease',
            'कीटनाशक': 'crop_disease',
            'भाव': 'market_price',
            'price': 'market_price',
            'मंडी': 'market_price',
            'market': 'market_price',
            'दाम': 'market_price',
            'rate': 'market_price'
        }
        
        # Process each intent-message pair
        intent_counts = Counter()
        for intent, message in all_data:
            # Map to English intent
            english_intent = self.intent_mapping.get(intent, intent)
            intent_counts[english_intent] += 1
            
            # Extract keywords from message
            keywords = self.extract_keywords_from_message(message)
            self.intent_keywords[english_intent].update(keywords)
            
            # Store message patterns
            self.intent_patterns[english_intent].append(message.lower().strip())
        
        print("📈 Intent distribution:")
        for intent, count in intent_counts.most_common():
            print(f"   {intent}: {count} samples")
        
        print("🔑 Top keywords per intent:")
        for intent, keywords in self.intent_keywords.items():
            top_keywords = list(keywords)[:10]  # Show top 10
            print(f"   {intent}: {top_keywords}")
    
    def extract_keywords_from_message(self, message: str) -> List[str]:
        """Extract meaningful keywords from a message"""
        # Remove common stop words
        stop_words = {
            'क्या', 'है', 'के', 'की', 'को', 'में', 'से', 'और', 'या', 'पर',
            'मुझे', 'आप', 'यह', 'वह', 'कैसे', 'कब', 'कहाँ', 'कौन', 'कितना',
            'what', 'is', 'the', 'of', 'to', 'in', 'for', 'and', 'or', 'on',
            'me', 'you', 'this', 'that', 'how', 'when', 'where', 'who', 'much'
        }
        
        # Clean and tokenize
        message = re.sub(r'[^\w\s\u0900-\u097F]', ' ', message.lower())
        words = message.split()
        
        # Filter meaningful words
        keywords = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def calculate_similarity_score(self, input_text: str, intent: str) -> float:
        """Calculate similarity score between input and intent patterns"""
        input_keywords = set(self.extract_keywords_from_message(input_text))
        intent_keywords = self.intent_keywords[intent]

        if not input_keywords:
            return 0.0

        # Keyword overlap score (improved)
        overlap = len(input_keywords.intersection(intent_keywords))
        if overlap > 0:
            keyword_score = overlap / len(input_keywords)  # Changed denominator
        else:
            keyword_score = 0.0

        # Pattern matching score (improved)
        input_lower = input_text.lower()
        input_words = set(input_lower.split())

        # Check against stored patterns
        max_pattern_score = 0.0
        for pattern in self.intent_patterns[intent][:100]:  # Check more patterns
            pattern_words = set(pattern.split())

            if pattern_words and input_words:
                # Calculate Jaccard similarity
                intersection = len(pattern_words.intersection(input_words))
                union = len(pattern_words.union(input_words))

                if union > 0:
                    jaccard_score = intersection / union
                    max_pattern_score = max(max_pattern_score, jaccard_score)

                # Also check for substring matches
                for input_word in input_words:
                    for pattern_word in pattern_words:
                        if input_word in pattern_word or pattern_word in input_word:
                            if len(input_word) > 2 and len(pattern_word) > 2:
                                substring_score = min(len(input_word), len(pattern_word)) / max(len(input_word), len(pattern_word))
                                max_pattern_score = max(max_pattern_score, substring_score * 0.8)

        # Combined score with higher weight to keywords
        final_score = (keyword_score * 0.7) + (max_pattern_score * 0.3)

        # Boost score if intent name matches input
        intent_boost = 0.0
        if intent in input_lower or any(word in input_lower for word in intent.split('_')):
            intent_boost = 0.2

        return min(final_score + intent_boost, 1.0)
    
    def detect_intent(self, text: str) -> Dict:
        """Main intent detection function using CSV data"""
        # Preprocess text
        processed_text = text.lower().strip()

        # First check direct keyword mapping
        keyword_intent = None
        keyword_confidence = 0.0

        for keyword, intent in self.keyword_intent_mapping.items():
            if keyword.lower() in processed_text:
                keyword_confidence = 0.8  # High confidence for direct keyword match
                keyword_intent = intent
                break

        # Calculate scores for all intents
        intent_scores = {}
        for intent in self.intent_keywords.keys():
            score = self.calculate_similarity_score(processed_text, intent)
            if score > 0:
                intent_scores[intent] = score

        # Boost keyword intent if found
        if keyword_intent and keyword_intent in intent_scores:
            intent_scores[keyword_intent] = max(intent_scores[keyword_intent], keyword_confidence)
        elif keyword_intent:
            intent_scores[keyword_intent] = keyword_confidence

        # Get best intent
        best_intent = None
        best_confidence = 0.0

        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            best_confidence = intent_scores[best_intent]
        
        # Extract entities (basic implementation)
        entities = self.extract_entities(processed_text)
        
        # Build response
        result = {
            "original_text": text,
            "processed_text": processed_text,
            "intent": best_intent if best_confidence >= self.confidence_threshold else "unknown",
            "confidence": best_confidence,
            "all_intents": intent_scores,
            "entities": entities,
            "timestamp": datetime.now().isoformat(),
            "is_confident": best_confidence >= self.confidence_threshold,
            "training_samples": len(self.intent_patterns.get(best_intent, []))
        }
        
        # Add to conversation history
        self.conversation_history.append(result)
        
        return result
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract farming-related entities from text"""
        entities = {}
        
        # Crop names (Hindi and English)
        crops = {
            "wheat": ["wheat", "गेहूं"],
            "rice": ["rice", "paddy", "धान", "चावल"],
            "corn": ["corn", "maize", "मक्का"],
            "cotton": ["cotton", "कपास"],
            "sugarcane": ["sugarcane", "गन्ना"],
            "potato": ["potato", "आलू"],
            "tomato": ["tomato", "टमाटर"],
            "onion": ["onion", "प्याज"]
        }
        
        crops_found = []
        for crop, keywords in crops.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    crops_found.append(crop)
        
        if crops_found:
            entities["crops"] = crops_found
        
        # Quantities
        quantity_pattern = r'\b\d+\s*(?:kg|quintal|ton|acre|hectare|किलो|क्विंटल|टन|एकड़|हेक्टेयर)\b'
        quantities = re.findall(quantity_pattern, text, re.IGNORECASE)
        if quantities:
            entities["quantities"] = quantities
        
        # Time references
        time_pattern = r'\b(?:today|tomorrow|next week|अगले|आज|कल|अभी)\b'
        time_refs = re.findall(time_pattern, text, re.IGNORECASE)
        if time_refs:
            entities["time"] = time_refs
        
        return entities
    
    def setup_response_database(self):
        """Setup detailed responses for farming intents"""
        self.detailed_responses = {
            "seed_inquiry": {
                "default": "बीज की जानकारी के लिए स्थानीय कृषि केंद्र से संपर्क करें। अच्छी किस्म के बीज चुनें।",
                "wheat": "गेहूं के लिए HD-2967, PBW-343 जैसी किस्में अच्छी हैं।",
                "rice": "धान के लिए बासमती, IR-64 जैसी किस्में उपयुक्त हैं।"
            },
            
            "fertilizer_advice": {
                "default": "मिट्टी परीक्षण के आधार पर संतुलित उर्वरक का प्रयोग करें। NPK अनुपात का ध्यान रखें।",
                "wheat": "गेहूं के लिए 120:60:40 NPK किलो प्रति हेक्टेयर दें।",
                "rice": "धान के लिए 150:75:75 NPK और जिंक सल्फेट दें।"
            },
            
            "crop_disease": {
                "default": "फसल में रोग के लक्षण दिखने पर तुरंत कृषि विशेषज्ञ से संपर्क करें।",
                "wheat": "गेहूं में रतुआ रोग के लिए प्रोपिकोनाजोल का छिड़काव करें।",
                "rice": "धान में ब्लास्ट रोग के लिए ट्राइसाइक्लाजोल का प्रयोग करें।"
            },
            
            "market_price": {
                "default": "मंडी भाव के लिए eNAM पोर्टल देखें या स्थानीय मंडी से संपर्क करें।",
                "wheat": "गेहूं का आज का भाव ₹2100-2200 प्रति क्विंटल है।",
                "rice": "धान का भाव ₹1800-1900 प्रति क्विंटल चल रहा है।"
            }
        }
    
    def get_detailed_response(self, intent_result: Dict) -> str:
        """Generate detailed farming advice based on intent and entities"""
        intent = intent_result["intent"]
        entities = intent_result["entities"]
        confidence = intent_result["confidence"]
        
        if intent == "unknown":
            return "मुझे आपकी बात समझ नहीं आई। कृपया स्पष्ट रूप से अपना सवाल पूछें।"
        
        # Get crop-specific response if crop is detected
        detected_crop = None
        if "crops" in entities and entities["crops"]:
            detected_crop = entities["crops"][0]
        
        # Get response from database
        if intent in self.detailed_responses:
            responses = self.detailed_responses[intent]
            if detected_crop and detected_crop in responses:
                response = responses[detected_crop]
            else:
                response = responses.get("default", "आपकी समस्या समझ गई है।")
        else:
            response = "इस विषय पर अधिक जानकारी के लिए कृषि विशेषज्ञ से संपर्क करें।"
        
        # Add training data info
        training_samples = intent_result.get("training_samples", 0)
        if training_samples > 0:
            response += f"\n\n📊 यह जानकारी {training_samples} training samples पर आधारित है।"
        
        # Add confidence indicator
        if confidence < 0.6:
            response += "\n\n⚠️ कृपया अपना सवाल और स्पष्ट करें।"
        
        return response
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return {"message": "No conversation history"}
        
        # Count intents
        intent_counts = {}
        total_confidence = 0
        confident_predictions = 0
        
        for entry in self.conversation_history:
            intent = entry["intent"]
            confidence = entry["confidence"]
            
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            total_confidence += confidence
            
            if entry["is_confident"]:
                confident_predictions += 1
        
        return {
            "total_interactions": len(self.conversation_history),
            "intent_distribution": intent_counts,
            "average_confidence": total_confidence / len(self.conversation_history),
            "confident_predictions": confident_predictions,
            "accuracy_rate": confident_predictions / len(self.conversation_history) * 100,
            "total_training_samples": sum(len(patterns) for patterns in self.intent_patterns.values())
        }


def main():
    """Test the CSV-based farmer intent detection system"""
    detector = CSVBasedFarmerIntentDetector()
    
    # Test cases from CSV data
    test_inputs = [
        "मुझे बीज की जानकारी चाहिए",
        "गेहूं के लिए कौन सी खाद अच्छी है",
        "फसल में कीड़े लग गए हैं",
        "आज मंडी में भाव क्या है",
        "बीज की जानकारी कैसे करें",
        "खाद की जानकारी दो",
        "कीटनाशक से जुड़ी समस्या है",
        "फसल की बीमारी का इलाज",
        "मंडी भाव पूछना है"
    ]
    
    print("\n🌾 CSV-based Farmer Intent Detection System")
    print("=" * 60)
    
    for text in test_inputs:
        print(f"\n📝 Input: {text}")
        result = detector.detect_intent(text)
        
        print(f"🎯 Intent: {result['intent']}")
        print(f"📊 Confidence: {result['confidence']:.3f}")
        print(f"🏷️ Entities: {result['entities']}")
        print(f"📈 Training samples: {result.get('training_samples', 0)}")
        
        response = detector.get_detailed_response(result)
        print(f"💬 Response: {response}")
        print("-" * 40)
    
    # Show conversation summary
    print("\n📈 Conversation Summary:")
    summary = detector.get_conversation_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
