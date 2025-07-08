#!/usr/bin/env python3
"""
Cloud LLM Farmer Assistant with Real-time Data
Uses internet-connected LLM APIs for better, up-to-date responses
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
nlp_dir = os.path.join(parent_dir, 'nlp')
sys.path.append(nlp_dir)

try:
    from csv_based_intent_detector import CSVBasedFarmerIntentDetector
except ImportError as e:
    print(f"❌ Could not import NLP module: {e}")
    print(f"💡 Looking for NLP module in: {nlp_dir}")
    print("Please ensure 'nlp' folder exists with csv_based_intent_detector.py")
    sys.exit(1)


class CloudLLMFarmerAssistant:
    """Advanced farmer assistant with cloud LLM and real-time data"""
    
    def __init__(self):
        """Initialize the cloud LLM assistant"""
        print("🌐 Initializing Cloud LLM Farmer Assistant...")
        
        # Initialize NLP detector
        try:
            self.nlp_detector = CSVBasedFarmerIntentDetector()
            print("✅ NLP system loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load NLP system: {e}")
            sys.exit(1)
        
        # LLM API configurations
        self.setup_llm_apis()
        
        # Real-time data sources
        self.setup_data_sources()
        
        # Session tracking
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Setup farmer-specific prompts
        self.setup_farmer_prompts()
    
    def setup_llm_apis(self):
        """Setup multiple LLM API options"""
        self.llm_apis = {
            "groq": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama3-70b-8192",  # Fast and good for farming
                "api_key": None,  # User needs to set this
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions", 
                "model": "gpt-3.5-turbo",  # Cost-effective
                "api_key": None,
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            
            "gemini": {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                "model": "gemini-pro",
                "api_key": None,
                "headers": lambda key: {
                    "Content-Type": "application/json"
                }
            },
            
            "huggingface": {
                "url": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
                "model": "microsoft/DialoGPT-large",
                "api_key": None,
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            }
        }
        
        # Default to Groq (fast and good for farming)
        self.current_llm = "groq"
        
        # Load API keys from environment or config
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from .env file, environment variables, or config file"""
        # Try to load from .env file first
        self.load_env_file()

        # Try to load from environment variables
        self.llm_apis["groq"]["api_key"] = os.getenv("GROQ_API_KEY")
        self.llm_apis["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
        self.llm_apis["gemini"]["api_key"] = os.getenv("GEMINI_API_KEY")
        self.llm_apis["huggingface"]["api_key"] = os.getenv("HUGGINGFACE_API_KEY")

        # Try to load from config file as fallback
        try:
            if os.path.exists("api_keys.json"):
                with open("api_keys.json", "r") as f:
                    keys = json.load(f)
                    for provider, key in keys.items():
                        if provider in self.llm_apis and not self.llm_apis[provider]["api_key"]:
                            self.llm_apis[provider]["api_key"] = key
        except Exception as e:
            print(f"⚠️ Could not load API keys from JSON file: {e}")

        # Check which APIs are available
        self.check_available_apis()

    def load_env_file(self):
        """Load environment variables from .env file"""
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            if value and value != "your_api_key_here":
                                os.environ[key] = value
                print("✅ Loaded environment variables from .env file")
            except Exception as e:
                print(f"⚠️ Could not load .env file: {e}")
        else:
            print("💡 No .env file found. Create one from .env.template")
    
    def check_available_apis(self):
        """Check which LLM APIs are available"""
        available_apis = []
        for provider, config in self.llm_apis.items():
            if config["api_key"]:
                available_apis.append(provider)
        
        if available_apis:
            print(f"✅ Available LLM APIs: {', '.join(available_apis)}")
            # Use the first available API
            self.current_llm = available_apis[0]
            print(f"🎯 Using: {self.current_llm}")
        else:
            print("⚠️ No API keys found. Please set up API keys.")
            self.show_api_setup_instructions()
    
    def show_api_setup_instructions(self):
        """Show instructions for setting up API keys"""
        print("\n🔑 API Key Setup Instructions:")
        print("=" * 60)
        print("Option 1: Use .env file (RECOMMENDED)")
        print("1. Copy template: cp .env.template .env")
        print("2. Edit .env file with your actual API keys")
        print("3. Example:")
        print("   GROQ_API_KEY=gsk_your_actual_key_here")
        print("   OPENAI_API_KEY=sk_your_actual_key_here")
        print("")
        print("Option 2: Environment Variables")
        print("set GROQ_API_KEY=your_groq_key")
        print("set OPENAI_API_KEY=your_openai_key")
        print("set GEMINI_API_KEY=your_gemini_key")
        print("")
        print("Option 3: Create api_keys.json file:")
        print('{')
        print('  "groq": "your_groq_api_key",')
        print('  "openai": "your_openai_api_key",')
        print('  "gemini": "your_gemini_api_key"')
        print('}')
        print("")
        print("🌟 Recommended: Groq (Fast + Free tier)")
        print("   Get key from: https://console.groq.com/")
        print("💡 Edit the .env file for easiest setup!")
    
    def setup_data_sources(self):
        """Setup real-time data sources"""
        self.data_sources = {
            "weather": {
                "url": "http://api.openweathermap.org/data/2.5/weather",
                "api_key": os.getenv("WEATHER_API_KEY"),  # Free from openweathermap.org
                "enabled": False
            },
            
            "market_prices": {
                "url": "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
                "api_key": os.getenv("DATA_GOV_API_KEY"),  # Free from data.gov.in
                "enabled": False
            },
            
            "news": {
                "url": "https://newsapi.org/v2/everything",
                "api_key": os.getenv("NEWS_API_KEY"),  # Free from newsapi.org
                "enabled": False
            }
        }
        
        # Check which data sources are available
        for source, config in self.data_sources.items():
            if config["api_key"]:
                config["enabled"] = True
                print(f"✅ {source} data source enabled")
    
    def setup_farmer_prompts(self):
        """Setup enhanced farmer prompts with real-time data context"""
        self.farmer_prompts = {
            "seed_inquiry": {
                "system_prompt": """आप एक अनुभवी कृषि विशेषज्ञ हैं जो भारतीय किसानों को बीज के बारे में सलाह देते हैं। 
                आपके पास real-time market data और weather information है। हिंदी में सरल, व्यावहारिक सलाह दें।
                बीज की किस्म, बुआई का समय, मात्रा, कहाँ से खरीदना है, और current market conditions के अनुसार सलाह दें।""",
                
                "context": "बीज की जानकारी और सलाह"
            },
            
            "fertilizer_advice": {
                "system_prompt": """आप एक मिट्टी और उर्वरक विशेषज्ञ हैं जो current market prices और weather conditions को ध्यान में रखकर 
                सलाह देते हैं। NPK अनुपात, मात्रा, समय, current prices, और weather के अनुसार application timing बताएं।""",
                
                "context": "खाद और उर्वरक की सलाह"
            },
            
            "crop_disease": {
                "system_prompt": """आप एक पौधों के रोग विशेषज्ञ हैं जो current weather patterns और disease outbreaks की 
                real-time information के साथ सलाह देते हैं। तुरंत करने वाले उपाय, weather-specific precautions, और 
                current market में available medicines बताएं।""",
                
                "context": "फसल रोग और कीट नियंत्रण"
            },
            
            "market_price": {
                "system_prompt": """आप एक कृषि मार्केटिंग विशेषज्ञ हैं जो real-time market data, price trends, और 
                current market conditions के साथ सलाह देते हैं। Today's prices, trends, best selling time, 
                और market intelligence provide करें।""",
                
                "context": "मंडी भाव और बाजार की जानकारी"
            },
            
            "weather_inquiry": {
                "system_prompt": """आप एक कृषि मौसम विशेषज्ञ हैं जो real-time weather data के साथ farming advice देते हैं। 
                Current weather, forecast, farming activities के लिए best timing, और weather-based precautions बताएं।""",
                
                "context": "मौसम और कृषि सलाह"
            }
        }
    
    def get_real_time_context(self, intent: str, entities: Dict) -> str:
        """Get real-time data context for better responses"""
        context_data = []
        
        # Get weather data if relevant
        if intent in ["weather_inquiry", "crop_disease", "irrigation_need"] and self.data_sources["weather"]["enabled"]:
            weather_data = self.get_weather_data()
            if weather_data:
                context_data.append(f"Current Weather: {weather_data}")
        
        # Get market prices if relevant
        if intent in ["market_price", "selling_inquiry"] and self.data_sources["market_prices"]["enabled"]:
            price_data = self.get_market_prices(entities.get("crops", []))
            if price_data:
                context_data.append(f"Current Market Prices: {price_data}")
        
        # Get agricultural news if relevant
        if self.data_sources["news"]["enabled"]:
            news_data = self.get_agricultural_news(intent)
            if news_data:
                context_data.append(f"Recent Agricultural News: {news_data}")
        
        return "\n".join(context_data) if context_data else ""
    
    def get_weather_data(self) -> Optional[str]:
        """Get current weather data"""
        try:
            # Default to Delhi, India (can be made configurable)
            params = {
                "q": "Delhi,IN",
                "appid": self.data_sources["weather"]["api_key"],
                "units": "metric"
            }
            
            response = requests.get(self.data_sources["weather"]["url"], params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                
                return f"Temperature: {temp}°C, Weather: {weather}, Humidity: {humidity}%"
        except Exception as e:
            print(f"⚠️ Weather data error: {e}")
        
        return None
    
    def get_market_prices(self, crops: List[str]) -> Optional[str]:
        """Get current market prices for crops"""
        try:
            # This would connect to actual market price APIs
            # For demo, returning sample data
            price_info = []
            for crop in crops:
                if crop == "wheat":
                    price_info.append("Wheat: ₹2200-2300/quintal")
                elif crop == "rice":
                    price_info.append("Rice: ₹1800-1900/quintal")
                elif crop == "corn":
                    price_info.append("Corn: ₹1600-1700/quintal")
            
            return ", ".join(price_info) if price_info else None
        except Exception as e:
            print(f"⚠️ Market price error: {e}")
        
        return None
    
    def get_agricultural_news(self, intent: str) -> Optional[str]:
        """Get relevant agricultural news"""
        try:
            # This would connect to news APIs for agricultural updates
            # For demo, returning sample relevant news
            news_items = {
                "crop_disease": "Recent reports of pest outbreaks in northern states",
                "market_price": "Government announces MSP increase for wheat",
                "weather_inquiry": "IMD predicts normal monsoon this year"
            }
            
            return news_items.get(intent)
        except Exception as e:
            print(f"⚠️ News data error: {e}")
        
        return None
    
    def generate_cloud_llm_response(self, intent_result: Dict, user_query: str) -> str:
        """Generate response using cloud LLM with real-time data"""
        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.0)
        entities = intent_result.get("entities", {})
        
        # Get real-time context
        real_time_context = self.get_real_time_context(intent, entities)
        
        # Get appropriate prompt
        prompt_config = self.farmer_prompts.get(intent, self.farmer_prompts.get("general", {
            "system_prompt": "आप एक अनुभवी किसान और कृषि सलाहकार हैं।",
            "context": "सामान्य कृषि सलाह"
        }))
        
        system_prompt = prompt_config["system_prompt"]
        context = prompt_config["context"]
        
        # Build enhanced user prompt with real-time data
        user_prompt = f"""
किसान का सवाल: "{user_query}"

पहचाना गया विषय: {context}
विश्वसनीयता: {confidence:.2f}

"""
        
        # Add entity information
        if entities:
            user_prompt += "पहचानी गई जानकारी:\n"
            if "crops" in entities:
                user_prompt += f"- फसल: {', '.join(entities['crops'])}\n"
            if "quantities" in entities:
                user_prompt += f"- मात्रा: {', '.join(entities['quantities'])}\n"
            if "time" in entities:
                user_prompt += f"- समय: {', '.join(entities['time'])}\n"
            user_prompt += "\n"
        
        # Add real-time context
        if real_time_context:
            user_prompt += f"Real-time Information:\n{real_time_context}\n\n"
        
        user_prompt += """
कृपया इस किसान को व्यावहारिक और उपयोगी सलाह दें। Real-time data का उपयोग करके current conditions के अनुसार सलाह दें।
जवाब हिंदी में, सरल भाषा में, और तुरंत लागू होने वाला हो। 3-4 वाक्यों में दें।
"""
        
        # Generate response using cloud LLM
        return self.call_cloud_llm(system_prompt, user_prompt)
    
    def call_cloud_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call cloud LLM API"""
        if not self.llm_apis[self.current_llm]["api_key"]:
            return self.get_fallback_response()
        
        try:
            if self.current_llm == "groq":
                return self.call_groq_api(system_prompt, user_prompt)
            elif self.current_llm == "openai":
                return self.call_openai_api(system_prompt, user_prompt)
            elif self.current_llm == "gemini":
                return self.call_gemini_api(system_prompt, user_prompt)
            else:
                return self.get_fallback_response()
                
        except Exception as e:
            print(f"❌ Cloud LLM error: {e}")
            return self.get_fallback_response()
    
    def call_groq_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API (Fast and good for farming)"""
        config = self.llm_apis["groq"]
        
        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "stream": False
        }
        
        headers = config["headers"](config["api_key"])
        
        response = requests.post(config["url"], json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise Exception(f"Groq API error: {response.status_code}")
    
    def call_openai_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        config = self.llm_apis["openai"]
        
        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        headers = config["headers"](config["api_key"])
        
        response = requests.post(config["url"], json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def call_gemini_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Google Gemini API"""
        config = self.llm_apis["gemini"]
        
        # Gemini has different format
        combined_prompt = f"{system_prompt}\n\nUser Query: {user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{"text": combined_prompt}]
            }]
        }
        
        url = f"{config['url']}?key={config['api_key']}"
        headers = config["headers"](config["api_key"])
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            raise Exception(f"Gemini API error: {response.status_code}")
    
    def get_fallback_response(self) -> str:
        """Provide fallback response when cloud LLM fails"""
        return "मुझे खुशी होगी आपकी मदद करने में। कृपया अपना सवाल दोबारा पूछें या नजदीकी कृषि केंद्र से संपर्क करें।"
    
    def process_farmer_query(self, user_query: str) -> Dict:
        """Complete pipeline with cloud LLM and real-time data"""
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
        
        # Step 2: Cloud LLM Response with Real-time Data
        print("🌐 Step 2: Generating cloud LLM response with real-time data...")
        llm_response = self.generate_cloud_llm_response(intent_result, user_query)
        
        # Step 3: Build complete result
        result = {
            "user_query": user_query,
            "nlp_result": intent_result,
            "llm_response": llm_response,
            "llm_provider": self.current_llm,
            "timestamp": datetime.now().isoformat(),
            "processing_pipeline": "STT → NLP → Cloud LLM + Real-time Data"
        }
        
        # Add to conversation history
        self.conversation_history.append(result)
        
        return result


def main():
    """Interactive cloud LLM farmer assistant"""
    print("🌐 Cloud LLM Farmer Assistant - Real-time Data Integration")
    print("="*80)
    
    try:
        # Initialize assistant
        assistant = CloudLLMFarmerAssistant()
        
        print("\n✅ System Ready!")
        print("💡 Type your farming questions in Hindi or English")
        print("💡 Type 'quit' to exit")
        print("💡 Type 'switch' to change LLM provider")
        print("-"*80)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎤 आपका सवाल: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'बाहर', 'बंद']:
                    print("\n👋 धन्यवाद! खेती में सफलता की शुभकामनाएं!")
                    break
                
                if user_input.lower() == 'switch':
                    # Show available APIs and switch
                    available = [k for k, v in assistant.llm_apis.items() if v["api_key"]]
                    if len(available) > 1:
                        print(f"Available APIs: {available}")
                        current_index = available.index(assistant.current_llm)
                        next_index = (current_index + 1) % len(available)
                        assistant.current_llm = available[next_index]
                        print(f"Switched to: {assistant.current_llm}")
                    else:
                        print("Only one API available")
                    continue
                
                if not user_input:
                    print("⚠️ कृपया अपना सवाल लिखें।")
                    continue
                
                # Process query
                start_time = time.time()
                result = assistant.process_farmer_query(user_input)
                processing_time = time.time() - start_time
                
                # Display response
                print("\n" + "🌾" * 30)
                print("🤖 किसान सहायक का जवाब:")
                print("🌾" * 30)
                print(f"💬 {result['llm_response']}")
                print("🌾" * 30)
                
                # Technical details
                print(f"⏱️ Response Time: {processing_time:.2f}s")
                print(f"🌐 LLM Provider: {result['llm_provider']}")
                print(f"📊 Confidence: {result['nlp_result']['confidence']:.2f}")
                print(f"🎯 Intent: {result['nlp_result']['intent']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 सिस्टम बंद कर रहे हैं...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
            
    except Exception as e:
        print(f"❌ System initialization failed: {e}")


if __name__ == "__main__":
    main()
