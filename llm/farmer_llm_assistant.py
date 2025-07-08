#!/usr/bin/env python3
"""
Farmer LLM Assistant
Takes NLP intent output and generates human-like responses using LLM
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nlp'))

try:
    from csv_based_intent_detector import CSVBasedFarmerIntentDetector
except ImportError:
    print("❌ Could not import NLP module. Please ensure 'nlp' folder exists.")
    sys.exit(1)


class FarmerLLMAssistant:
    """Advanced LLM-powered farmer assistant"""
    
    def __init__(self):
        """Initialize the LLM assistant"""
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"  # Good balance of speed and quality
        
        # Initialize NLP detector
        try:
            self.nlp_detector = CSVBasedFarmerIntentDetector()
            print("✅ NLP system loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load NLP system: {e}")
            sys.exit(1)
        
        # Session tracking
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Setup farmer-specific prompts
        self.setup_farmer_prompts()
        
        # Check Ollama availability
        self.check_ollama_availability()
    
    def setup_farmer_prompts(self):
        """Setup farmer-specific prompts for different intents"""
        self.farmer_prompts = {
            "seed_inquiry": {
                "system_prompt": """आप एक अनुभवी कृषि विशेषज्ञ हैं जो किसानों को बीज के बारे में सलाह देते हैं। 
                आपको हिंदी में सरल और व्यावहारिक जानकारी देनी है। बीज की किस्म, बुआई का समय, 
                मात्रा, और कहाँ से खरीदना है - इन सभी की जानकारी दें।""",
                
                "context": "बीज की जानकारी और सलाह"
            },
            
            "fertilizer_advice": {
                "system_prompt": """आप एक मिट्टी और उर्वरक विशेषज्ञ हैं। किसानों को खाद और उर्वरक के बारे में 
                सरल हिंदी में सलाह दें। NPK अनुपात, मात्रा, समय, और कीमत की जानकारी दें। 
                जैविक और रासायनिक दोनों विकल्प बताएं।""",
                
                "context": "खाद और उर्वरक की सलाह"
            },
            
            "crop_disease": {
                "system_prompt": """आप एक पौधों के रोग विशेषज्ञ हैं। फसल की बीमारी और कीट की समस्या का 
                समाधान हिंदी में दें। लक्षण पहचानना, इलाज, दवाई, और बचाव के तरीके बताएं। 
                तुरंत करने वाले उपाय पर जोर दें।""",
                
                "context": "फसल रोग और कीट नियंत्रण"
            },
            
            "market_price": {
                "system_prompt": """आप एक कृषि मार्केटिंग विशेषज्ञ हैं। मंडी भाव, बाजार की स्थिति, 
                और बेचने की सलाह हिंदी में दें। कीमत के रुझान, बेहतर मंडी, और बिक्री का समय बताएं। 
                eNAM और अन्य प्लेटफॉर्म की जानकारी दें।""",
                
                "context": "मंडी भाव और बाजार की जानकारी"
            },
            
            "general": {
                "system_prompt": """आप एक अनुभवी किसान और कृषि सलाहकार हैं। किसानों की हर समस्या का 
                समाधान सरल हिंदी में दें। व्यावहारिक, तुरंत लागू होने वाली सलाह दें। 
                स्थानीय परिस्थितियों को ध्यान में रखें।""",
                
                "context": "सामान्य कृषि सलाह"
            }
        }
    
    def check_ollama_availability(self):
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if self.model_name in model_names:
                    print(f"✅ Ollama is running with {self.model_name}")
                    return True
                else:
                    print(f"⚠️ Model {self.model_name} not found. Available models: {model_names}")
                    print(f"🔄 Attempting to pull {self.model_name}...")
                    self.pull_model()
                    return True
            else:
                print("❌ Ollama is not responding")
                return False
                
        except requests.exceptions.RequestException:
            print("❌ Ollama is not running. Please start Ollama first.")
            print("💡 Install Ollama from: https://ollama.ai")
            print("💡 Then run: ollama serve")
            return False
    
    def pull_model(self):
        """Pull the required model if not available"""
        try:
            print(f"📥 Pulling {self.model_name}... This may take a few minutes.")
            
            pull_data = {"name": self.model_name}
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json=pull_data,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully pulled {self.model_name}")
            else:
                print(f"❌ Failed to pull {self.model_name}")
                
        except Exception as e:
            print(f"❌ Error pulling model: {e}")
    
    def generate_llm_response(self, intent_result: Dict, user_query: str) -> str:
        """Generate human-like response using LLM"""
        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.0)
        entities = intent_result.get("entities", {})
        
        # Get appropriate prompt
        prompt_config = self.farmer_prompts.get(intent, self.farmer_prompts["general"])
        system_prompt = prompt_config["system_prompt"]
        context = prompt_config["context"]
        
        # Build user prompt with context
        user_prompt = f"""
किसान का सवाल: "{user_query}"

पहचाना गया विषय: {context}
विश्वसनीयता: {confidence:.2f}

"""
        
        # Add entity information if available
        if entities:
            user_prompt += "पहचानी गई जानकारी:\n"
            if "crops" in entities:
                user_prompt += f"- फसल: {', '.join(entities['crops'])}\n"
            if "quantities" in entities:
                user_prompt += f"- मात्रा: {', '.join(entities['quantities'])}\n"
            if "time" in entities:
                user_prompt += f"- समय: {', '.join(entities['time'])}\n"
            user_prompt += "\n"
        
        user_prompt += """
कृपया इस किसान को व्यावहारिक और उपयोगी सलाह दें। जवाब हिंदी में, सरल भाषा में, और तुरंत लागू होने वाला हो।
जवाब 3-4 वाक्यों में दें, बहुत लंबा न करें।
"""
        
        try:
            # Prepare request for Ollama
            ollama_request = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Balanced creativity
                    "top_p": 0.9,
                    "max_tokens": 200,   # Keep responses concise
                    "stop": ["\n\n", "किसान:", "सवाल:"]
                }
            }
            
            # Make request to Ollama
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=ollama_request,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result["message"]["content"].strip()
                
                # Clean up response
                llm_response = self.clean_llm_response(llm_response)
                
                print(f"🤖 LLM Response Time: {response_time:.2f}s")
                return llm_response
            else:
                print(f"❌ LLM API Error: {response.status_code}")
                return self.get_fallback_response(intent, entities)
                
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return self.get_fallback_response(intent, entities)
    
    def clean_llm_response(self, response: str) -> str:
        """Clean and format LLM response"""
        # Remove unwanted prefixes/suffixes
        unwanted_prefixes = [
            "किसान जी,", "भाई साहब,", "जी हाँ,", "देखिए,", 
            "आपको बताना चाहूंगा कि", "मेरी सलाह है कि"
        ]
        
        for prefix in unwanted_prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Ensure proper Hindi formatting
        response = response.replace("।।", "।")
        response = response.strip()
        
        # Add appropriate ending if missing
        if not response.endswith(('।', '।', '!')):
            response += "।"
        
        return response
    
    def get_fallback_response(self, intent: str, entities: Dict) -> str:
        """Provide fallback response when LLM fails"""
        fallback_responses = {
            "seed_inquiry": "बीज की जानकारी के लिए नजदीकी कृषि केंद्र या बीज भंडार से संपर्क करें। अच्छी किस्म के प्रमाणित बीज ही खरीदें।",
            
            "fertilizer_advice": "मिट्टी परीक्षण कराकर उसके अनुसार संतुलित उर्वरक का प्रयोग करें। NPK अनुपात का ध्यान रखें।",
            
            "crop_disease": "फसल में रोग के लक्षण दिखने पर तुरंत कृषि विशेषज्ञ से संपर्क करें। सही दवाई का छिड़काव करें।",
            
            "market_price": "मंडी भाव की जानकारी के लिए eNAM पोर्टल देखें या स्थानीय मंडी से संपर्क करें।",
            
            "general": "आपकी समस्या के लिए नजदीकी कृषि विज्ञान केंद्र या कृषि विभाग से संपर्क करें।"
        }
        
        base_response = fallback_responses.get(intent, fallback_responses["general"])
        
        # Add entity-specific information
        if "crops" in entities:
            crops = ", ".join(entities["crops"])
            base_response = f"{crops} के लिए {base_response}"
        
        return base_response
    
    def process_farmer_query(self, user_query: str) -> Dict:
        """Complete pipeline: NLP → LLM → Response"""
        print(f"\n🌾 Processing: {user_query}")
        
        # Step 1: NLP Intent Detection
        print("🔍 Step 1: Detecting intent...")
        intent_result = self.nlp_detector.detect_intent(user_query)
        
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        entities = intent_result["entities"]
        
        print(f"🎯 Intent: {intent} (Confidence: {confidence:.2f})")
        if entities:
            print(f"🏷️ Entities: {entities}")
        
        # Step 2: LLM Response Generation
        print("🤖 Step 2: Generating LLM response...")
        llm_response = self.generate_llm_response(intent_result, user_query)
        
        # Step 3: Build complete result
        result = {
            "user_query": user_query,
            "nlp_result": intent_result,
            "llm_response": llm_response,
            "timestamp": datetime.now().isoformat(),
            "processing_pipeline": "STT → NLP → LLM"
        }
        
        # Add to conversation history
        self.conversation_history.append(result)
        
        return result
    
    def display_response(self, result: Dict):
        """Display formatted response to user"""
        print("\n" + "="*60)
        print("🌾 किसान सहायक का जवाब:")
        print("="*60)
        print(f"💬 {result['llm_response']}")
        print("="*60)
        
        # Show technical details
        nlp_result = result["nlp_result"]
        print(f"📊 विश्वसनीयता: {nlp_result['confidence']:.2f}")
        print(f"🎯 विषय: {nlp_result['intent']}")
        if nlp_result['entities']:
            print(f"🏷️ पहचानी गई जानकारी: {nlp_result['entities']}")
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary"""
        if not self.conversation_history:
            return {"message": "No conversation history"}
        
        total_queries = len(self.conversation_history)
        intents = [entry["nlp_result"]["intent"] for entry in self.conversation_history]
        intent_counts = {}
        
        for intent in intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        avg_confidence = sum(entry["nlp_result"]["confidence"] for entry in self.conversation_history) / total_queries
        
        session_duration = datetime.now() - self.session_start
        
        return {
            "session_duration": str(session_duration),
            "total_queries": total_queries,
            "intent_distribution": intent_counts,
            "average_confidence": avg_confidence,
            "llm_model": self.model_name
        }


def main():
    """Interactive farmer assistant"""
    print("🌾 Farmer LLM Assistant - STT → NLP → LLM Pipeline")
    print("="*70)
    
    try:
        # Initialize assistant
        assistant = FarmerLLMAssistant()
        
        print("\n✅ System Ready!")
        print("💡 Type your farming questions in Hindi or English")
        print("💡 Type 'quit' to exit")
        print("💡 Type 'summary' to see conversation summary")
        print("-"*70)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎤 आपका सवाल: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर', 'बंद']:
                    print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                    break
                
                if user_input.lower() in ['summary', 'सारांश']:
                    summary = assistant.get_conversation_summary()
                    print("\n📊 Conversation Summary:")
                    print(json.dumps(summary, indent=2, ensure_ascii=False))
                    continue
                
                if not user_input:
                    print("⚠️ कृपया अपना सवाल लिखें।")
                    continue
                
                # Process query through complete pipeline
                result = assistant.process_farmer_query(user_input)
                
                # Display response
                assistant.display_response(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 सिस्टम बंद कर रहे हैं...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        # Show final summary
        summary = assistant.get_conversation_summary()
        if summary.get("total_queries", 0) > 0:
            print("\n📈 Final Session Summary:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"❌ System initialization failed: {e}")


if __name__ == "__main__":
    main()
