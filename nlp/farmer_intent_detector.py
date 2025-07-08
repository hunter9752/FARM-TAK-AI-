#!/usr/bin/env python3
"""
Farmer Intent Detection System
Takes STT output and detects farming-related intents
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class FarmerIntentDetector:
    """NLP system for detecting farmer intents from speech"""
    
    def __init__(self):
        """Initialize the farmer intent detection system"""
        self.setup_farming_intents()
        self.setup_keywords()
        self.setup_entities()
        
        # Intent confidence threshold
        self.confidence_threshold = 0.3  # Lowered for better detection
        
        # Session tracking
        self.conversation_history = []
        self.current_context = None
        
    def setup_farming_intents(self):
        """Define farming-specific intents"""
        self.intents = {
            # Crop Management
            "crop_planting": {
                "description": "User wants to plant crops",
                "keywords": ["plant", "sow", "seed", "बोना", "लगाना", "खेती", "बुआई", "रोपाई", "बीज", "want"],
                "patterns": [
                    r".*plant.*crop.*",
                    r".*sow.*seed.*",
                    r".*when.*plant.*",
                    r".*कब.*बोना.*",
                    r".*कैसे.*लगाना.*",
                    r".*बुआई.*करना.*",
                    r".*रोपाई.*करना.*",
                    r".*want.*plant.*",
                    r".*मुझे.*बोना.*"
                ]
            },
            
            "crop_harvesting": {
                "description": "User wants to harvest crops",
                "keywords": ["harvest", "cut", "reap", "काटना", "फसल", "तैयार"],
                "patterns": [
                    r".*harvest.*ready.*",
                    r".*crop.*ready.*",
                    r".*when.*harvest.*",
                    r".*फसल.*तैयार.*",
                    r".*कब.*काटना.*"
                ]
            },
            
            "crop_disease": {
                "description": "User reporting crop disease/pest issues",
                "keywords": ["disease", "pest", "insect", "fungus", "बीमारी", "कीड़े", "रोग", "लग", "गए"],
                "patterns": [
                    r".*crop.*disease.*",
                    r".*plant.*sick.*",
                    r".*pest.*problem.*",
                    r".*फसल.*बीमारी.*",
                    r".*पौधे.*रोग.*",
                    r".*कीड़े.*लग.*गए.*",
                    r".*में.*कीड़े.*"
                ]
            },
            
            # Weather & Irrigation
            "weather_inquiry": {
                "description": "User asking about weather",
                "keywords": ["weather", "rain", "temperature", "मौसम", "बारिश", "तापमान"],
                "patterns": [
                    r".*weather.*today.*",
                    r".*rain.*coming.*",
                    r".*temperature.*",
                    r".*आज.*मौसम.*",
                    r".*बारिश.*होगी.*"
                ]
            },
            
            "irrigation_need": {
                "description": "User asking about watering/irrigation",
                "keywords": ["water", "irrigation", "watering", "पानी", "सिंचाई", "कब", "करनी"],
                "patterns": [
                    r".*need.*water.*",
                    r".*irrigation.*required.*",
                    r".*when.*water.*",
                    r".*पानी.*देना.*",
                    r".*सिंचाई.*कब.*",
                    r".*कब.*सिंचाई.*करनी.*"
                ]
            },
            
            # Market & Pricing
            "market_price": {
                "description": "User asking about crop prices",
                "keywords": ["price", "rate", "market", "sell", "भाव", "दाम", "मंडी", "कीमत", "रेट"],
                "patterns": [
                    r".*price.*crop.*",
                    r".*market.*rate.*",
                    r".*sell.*price.*",
                    r".*आज.*भाव.*",
                    r".*मंडी.*दाम.*",
                    r".*का.*भाव.*",
                    r".*की.*कीमत.*"
                ]
            },
            
            "selling_inquiry": {
                "description": "User wants to sell crops",
                "keywords": ["sell", "market", "buyer", "बेचना", "खरीदार"],
                "patterns": [
                    r".*want.*sell.*",
                    r".*where.*sell.*",
                    r".*buyer.*needed.*",
                    r".*कहाँ.*बेचना.*",
                    r".*खरीदार.*चाहिए.*"
                ]
            },
            
            # Fertilizer & Seeds
            "fertilizer_advice": {
                "description": "User asking about fertilizers",
                "keywords": ["fertilizer", "manure", "nutrients", "खाद", "उर्वरक", "good", "अच्छी", "what"],
                "patterns": [
                    r".*fertilizer.*needed.*",
                    r".*which.*fertilizer.*",
                    r".*nutrients.*required.*",
                    r".*कौन.*खाद.*",
                    r".*उर्वरक.*चाहिए.*",
                    r".*अच्छी.*खाद.*",
                    r".*good.*fertilizer.*",
                    r".*what.*fertilizer.*"
                ]
            },
            
            "seed_inquiry": {
                "description": "User asking about seeds",
                "keywords": ["seed", "variety", "hybrid", "बीज", "किस्म"],
                "patterns": [
                    r".*seed.*variety.*",
                    r".*which.*seed.*",
                    r".*best.*variety.*",
                    r".*कौन.*बीज.*",
                    r".*अच्छी.*किस्म.*"
                ]
            },
            
            # Government Schemes
            "government_scheme": {
                "description": "User asking about government schemes",
                "keywords": ["scheme", "subsidy", "government", "योजना", "सब्सिडी", "सरकार"],
                "patterns": [
                    r".*government.*scheme.*",
                    r".*subsidy.*available.*",
                    r".*farmer.*scheme.*",
                    r".*सरकारी.*योजना.*",
                    r".*सब्सिडी.*मिलती.*"
                ]
            },
            
            # General Help
            "general_help": {
                "description": "User asking for general farming help",
                "keywords": ["help", "advice", "suggestion", "मदद", "सलाह"],
                "patterns": [
                    r".*need.*help.*",
                    r".*advice.*farming.*",
                    r".*suggestion.*crop.*",
                    r".*मदद.*चाहिए.*",
                    r".*सलाह.*दो.*"
                ]
            }
        }
    
    def setup_keywords(self):
        """Setup crop and farming-related keywords"""
        self.crops = {
            "wheat": ["wheat", "गेहूं"],
            "rice": ["rice", "paddy", "धान", "चावल"],
            "corn": ["corn", "maize", "मक्का"],
            "cotton": ["cotton", "कपास"],
            "sugarcane": ["sugarcane", "गन्ना"],
            "potato": ["potato", "आलू"],
            "tomato": ["tomato", "टमाटर"],
            "onion": ["onion", "प्याज"],
            "soybean": ["soybean", "सोयाबीन"],
            "mustard": ["mustard", "सरसों"]
        }
        
        self.seasons = {
            "kharif": ["kharif", "खरीफ", "monsoon", "बारिश"],
            "rabi": ["rabi", "रबी", "winter", "सर्दी"],
            "zaid": ["zaid", "जायद", "summer", "गर्मी"]
        }
        
        self.farming_tools = {
            "tractor": ["tractor", "ट्रैक्टर"],
            "plow": ["plow", "plough", "हल"],
            "harvester": ["harvester", "हार्वेस्टर"],
            "sprayer": ["sprayer", "स्प्रेयर"]
        }
    
    def setup_entities(self):
        """Setup entity extraction patterns"""
        self.entity_patterns = {
            "crop_name": r"\b(?:wheat|rice|corn|cotton|गेहूं|धान|मक्का|कपास)\b",
            "quantity": r"\b\d+\s*(?:kg|quintal|ton|acre|hectare|किलो|क्विंटल|टन|एकड़|हेक्टेयर)\b",
            "time": r"\b(?:today|tomorrow|next week|अगले|आज|कल)\b",
            "location": r"\b(?:field|farm|खेत|फार्म)\b"
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation but keep Hindi characters
        text = re.sub(r'[^\w\s\u0900-\u097F]', ' ', text)
        
        return text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract farming-related entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        # Extract crop names
        crops_found = []
        for crop, keywords in self.crops.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    crops_found.append(crop)
        
        if crops_found:
            entities["crops"] = crops_found
        
        # Extract seasons
        seasons_found = []
        for season, keywords in self.seasons.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    seasons_found.append(season)
        
        if seasons_found:
            entities["seasons"] = seasons_found
        
        return entities
    
    def calculate_intent_confidence(self, text: str, intent_data: Dict) -> float:
        """Calculate confidence score for an intent"""
        score = 0.0

        # Check keywords - give higher weight to keyword matches
        keyword_matches = 0
        for keyword in intent_data["keywords"]:
            if keyword.lower() in text:
                keyword_matches += 1

        if intent_data["keywords"] and keyword_matches > 0:
            keyword_score = keyword_matches / len(intent_data["keywords"])
            score += keyword_score * 0.7  # Higher weight for keywords

        # Check patterns
        pattern_matches = 0
        for pattern in intent_data["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1

        if intent_data["patterns"] and pattern_matches > 0:
            pattern_score = pattern_matches / len(intent_data["patterns"])
            score += pattern_score * 0.3  # Lower weight for patterns

        # Boost score if both keywords and patterns match
        if keyword_matches > 0 and pattern_matches > 0:
            score += 0.2  # Bonus for multiple match types

        return min(score, 1.0)  # Cap at 1.0
    
    def detect_intent(self, text: str) -> Dict:
        """Main intent detection function"""
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Calculate confidence for each intent
        intent_scores = {}
        for intent_name, intent_data in self.intents.items():
            confidence = self.calculate_intent_confidence(processed_text, intent_data)
            if confidence > 0:
                intent_scores[intent_name] = confidence
        
        # Get best intent
        best_intent = None
        best_confidence = 0.0
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            best_confidence = intent_scores[best_intent]
        
        # Extract entities
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
            "is_confident": best_confidence >= self.confidence_threshold
        }
        
        # Add to conversation history
        self.conversation_history.append(result)
        
        return result
    
    def get_response_suggestion(self, intent_result: Dict) -> str:
        """Generate appropriate response based on detected intent"""
        intent = intent_result["intent"]
        entities = intent_result["entities"]
        
        if intent == "unknown":
            return "मुझे समझ नहीं आया। कृपया अपना सवाल दोबारा पूछें।"
        
        # Intent-specific responses
        responses = {
            "crop_planting": "आप फसल बोना चाहते हैं। कौन सी फसल और कब बोना चाहते हैं?",
            "crop_harvesting": "फसल काटने के बारे में पूछ रहे हैं। कौन सी फसल तैयार है?",
            "crop_disease": "फसल में बीमारी की समस्या है। कृपया लक्षण बताएं।",
            "weather_inquiry": "मौसम की जानकारी चाहिए। आज का मौसम देखता हूं।",
            "irrigation_need": "सिंचाई के बारे में पूछ रहे हैं। कौन सी फसल में पानी चाहिए?",
            "market_price": "बाजार भाव जानना चाहते हैं। कौन सी फसल का भाव चाहिए?",
            "selling_inquiry": "फसल बेचना चाहते हैं। कौन सी फसल और कितनी मात्रा है?",
            "fertilizer_advice": "खाद के बारे में सलाह चाहिए। कौन सी फसल के लिए?",
            "seed_inquiry": "बीज की जानकारी चाहिए। कौन सी फसल के बीज चाहिए?",
            "government_scheme": "सरकारी योजना के बारे में पूछ रहे हैं। किस प्रकार की योजना?",
            "general_help": "खेती में मदद चाहिए। कृपया अपनी समस्या विस्तार से बताएं।"
        }
        
        base_response = responses.get(intent, "आपकी बात समझ गई है।")
        
        # Add entity-specific information
        if "crops" in entities:
            crops = ", ".join(entities["crops"])
            base_response += f" आपने {crops} के बारे में पूछा है।"
        
        if "quantity" in entities:
            quantities = ", ".join(entities["quantity"])
            base_response += f" मात्रा: {quantities}"
        
        return base_response
    
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
            "accuracy_rate": confident_predictions / len(self.conversation_history) * 100
        }


def main():
    """Test the farmer intent detection system"""
    detector = FarmerIntentDetector()
    
    # Test cases
    test_inputs = [
        "मुझे गेहूं बोना है",
        "आज मौसम कैसा है",
        "टमाटर का भाव क्या है",
        "फसल में कीड़े लग गए हैं",
        "कब सिंचाई करनी चाहिए",
        "सरकारी योजना के बारे में बताओ",
        "I want to plant rice",
        "When should I harvest wheat",
        "What fertilizer is good for corn"
    ]
    
    print("🌾 Farmer Intent Detection System")
    print("=" * 50)
    
    for text in test_inputs:
        print(f"\n📝 Input: {text}")
        result = detector.detect_intent(text)
        
        print(f"🎯 Intent: {result['intent']}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"🏷️ Entities: {result['entities']}")
        
        response = detector.get_response_suggestion(result)
        print(f"💬 Response: {response}")
        print("-" * 30)
    
    # Show conversation summary
    print("\n📈 Conversation Summary:")
    summary = detector.get_conversation_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
