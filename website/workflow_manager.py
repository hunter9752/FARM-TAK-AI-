#!/usr/bin/env python3
"""
Complete Workflow Manager for Farmer Assistant Website
Manages STT → NLP → LLM → TTS pipeline in web environment
"""

import os
import sys
import json
import time
import tempfile
import threading
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, 'nlp'))
sys.path.append(os.path.join(parent_dir, 'llm'))

import requests


class WebWorkflowManager:
    """Complete workflow manager for web-based farmer assistant"""
    
    def __init__(self):
        """Initialize workflow manager"""
        self.session_start = datetime.now()
        self.workflow_stats = {
            "total_requests": 0,
            "successful_completions": 0,
            "component_stats": {
                "stt": {"calls": 0, "successes": 0, "avg_time": 0},
                "nlp": {"calls": 0, "successes": 0, "avg_time": 0},
                "llm": {"calls": 0, "successes": 0, "avg_time": 0},
                "tts": {"calls": 0, "successes": 0, "avg_time": 0}
            }
        }
        
        # Initialize components
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all workflow components"""
        
        # 1. Initialize NLP
        try:
            from csv_based_intent_detector import CSVBasedFarmerIntentDetector
            self.nlp_detector = CSVBasedFarmerIntentDetector()
            print("✅ NLP component initialized")
        except Exception as e:
            print(f"⚠️ NLP component failed: {e}")
            self.nlp_detector = None
        
        # 2. Initialize LLM
        self.load_env()
        self.api_key = os.getenv('GROQ_API_KEY')
        if self.api_key:
            print("✅ LLM component initialized")
        else:
            print("⚠️ LLM component: No API key")
        
        # 3. Initialize TTS
        try:
            from gtts import gTTS
            self.tts_available = True
            print("✅ TTS component initialized")
        except ImportError:
            self.tts_available = False
            print("⚠️ TTS component not available")
    
    def load_env(self):
        """Load environment variables"""
        env_file = os.path.join(parent_dir, 'llm', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value and value != "your_api_key_here":
                            os.environ[key] = value
    
    def process_complete_workflow(self, user_input: str, input_type: str = "text") -> Dict:
        """
        Process complete workflow: Input → NLP → LLM → TTS
        
        Args:
            user_input: User's farming question
            input_type: "text" or "audio"
        
        Returns:
            Complete workflow result
        """
        workflow_start = time.time()
        self.workflow_stats["total_requests"] += 1
        
        result = {
            "workflow_id": f"wf_{int(time.time())}",
            "input": user_input,
            "input_type": input_type,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "success": False,
            "total_time": 0,
            "error": None
        }
        
        try:
            # Step 1: STT (if audio input)
            if input_type == "audio":
                stt_result = self.process_stt_step(user_input)
                result["steps"]["stt"] = stt_result
                
                if not stt_result["success"]:
                    result["error"] = "STT processing failed"
                    return result
                
                text_input = stt_result["transcribed_text"]
            else:
                text_input = user_input
                result["steps"]["stt"] = {"success": True, "skipped": True, "reason": "text input"}
            
            # Step 2: NLP Intent Detection
            nlp_result = self.process_nlp_step(text_input)
            result["steps"]["nlp"] = nlp_result
            
            # Step 3: LLM Response Generation
            llm_result = self.process_llm_step(text_input, nlp_result)
            result["steps"]["llm"] = llm_result
            
            if not llm_result["success"]:
                result["error"] = "LLM processing failed"
                return result
            
            # Step 4: TTS Audio Generation
            tts_result = self.process_tts_step(llm_result["response"])
            result["steps"]["tts"] = tts_result
            
            # Calculate total time
            result["total_time"] = time.time() - workflow_start
            result["success"] = True
            
            # Update stats
            self.workflow_stats["successful_completions"] += 1
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            result["total_time"] = time.time() - workflow_start
            return result
    
    def process_stt_step(self, audio_data) -> Dict:
        """Process STT step (placeholder for web implementation)"""
        step_start = time.time()
        
        # In web environment, STT is handled by browser
        # This is a placeholder for future server-side STT
        
        result = {
            "success": True,
            "transcribed_text": audio_data,  # Placeholder
            "confidence": 0.9,
            "processing_time": time.time() - step_start,
            "method": "browser_stt"
        }
        
        # Update component stats
        self.update_component_stats("stt", result["success"], result["processing_time"])
        
        return result
    
    def process_nlp_step(self, text: str) -> Dict:
        """Process NLP intent detection step"""
        step_start = time.time()
        
        try:
            if self.nlp_detector:
                nlp_result = self.nlp_detector.detect_intent(text)
                
                result = {
                    "success": True,
                    "intent": nlp_result["intent"],
                    "confidence": nlp_result["confidence"],
                    "entities": nlp_result["entities"],
                    "processing_time": time.time() - step_start,
                    "method": "csv_based_detector"
                }
            else:
                # Fallback NLP
                result = {
                    "success": True,
                    "intent": "general",
                    "confidence": 0.5,
                    "entities": {},
                    "processing_time": time.time() - step_start,
                    "method": "fallback"
                }
            
            # Update component stats
            self.update_component_stats("nlp", result["success"], result["processing_time"])
            
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - step_start,
                "method": "failed"
            }
            
            self.update_component_stats("nlp", False, result["processing_time"])
            return result
    
    def process_llm_step(self, text: str, nlp_result: Dict) -> Dict:
        """Process LLM response generation step"""
        step_start = time.time()
        
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "No API key configured",
                    "processing_time": time.time() - step_start
                }
            
            # Enhanced system prompt with workflow context
            system_prompt = f"""आप एक अनुभवी भारतीय कृषि विशेषज्ञ हैं। किसानों को हिंदी में सरल, व्यावहारिक सलाह देते हैं।

Workflow Context:
- पहचाना गया विषय: {nlp_result.get('intent', 'general')}
- विश्वसनीयता: {nlp_result.get('confidence', 0):.2f}
- Entities: {nlp_result.get('entities', {})}

जवाब हमेशा:
- हिंदी में दें
- 3-4 वाक्यों में संक्षिप्त हो
- तुरंत लागू होने वाला हो
- व्यावहारिक और उपयोगी हो
- Web interface के लिए उपयुक्त हो"""

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7,
                "max_tokens": 200,
                "stream": False
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            processing_time = time.time() - step_start
            
            if response.status_code == 200:
                api_result = response.json()
                llm_response = api_result["choices"][0]["message"]["content"].strip()
                
                result = {
                    "success": True,
                    "response": llm_response,
                    "processing_time": processing_time,
                    "provider": "groq",
                    "model": "llama3-70b-8192",
                    "tokens_used": api_result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                result = {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "processing_time": processing_time,
                    "provider": "groq"
                }
            
            # Update component stats
            self.update_component_stats("llm", result["success"], result["processing_time"])
            
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - step_start,
                "provider": "groq"
            }
            
            self.update_component_stats("llm", False, result["processing_time"])
            return result
    
    def process_tts_step(self, text: str) -> Dict:
        """Process TTS audio generation step"""
        step_start = time.time()
        
        try:
            if not self.tts_available:
                return {
                    "success": False,
                    "error": "TTS not available",
                    "processing_time": time.time() - step_start
                }
            
            from gtts import gTTS
            
            # Generate TTS
            tts = gTTS(text=text, lang="hi", slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            
            result = {
                "success": True,
                "audio_file": temp_file.name,
                "text_length": len(text),
                "processing_time": time.time() - step_start,
                "method": "gtts",
                "language": "hi"
            }
            
            # Update component stats
            self.update_component_stats("tts", result["success"], result["processing_time"])
            
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - step_start,
                "method": "gtts"
            }
            
            self.update_component_stats("tts", False, result["processing_time"])
            return result
    
    def update_component_stats(self, component: str, success: bool, processing_time: float):
        """Update component statistics"""
        stats = self.workflow_stats["component_stats"][component]
        
        stats["calls"] += 1
        if success:
            stats["successes"] += 1
        
        # Update average time
        if stats["calls"] == 1:
            stats["avg_time"] = processing_time
        else:
            stats["avg_time"] = (stats["avg_time"] * (stats["calls"] - 1) + processing_time) / stats["calls"]
    
    def get_workflow_stats(self) -> Dict:
        """Get comprehensive workflow statistics"""
        uptime = datetime.now() - self.session_start
        
        success_rate = 0
        if self.workflow_stats["total_requests"] > 0:
            success_rate = (self.workflow_stats["successful_completions"] / 
                          self.workflow_stats["total_requests"]) * 100
        
        return {
            "session_start": self.session_start.isoformat(),
            "uptime": str(uptime),
            "total_requests": self.workflow_stats["total_requests"],
            "successful_completions": self.workflow_stats["successful_completions"],
            "success_rate": success_rate,
            "component_stats": self.workflow_stats["component_stats"],
            "system_health": self.get_system_health()
        }
    
    def get_system_health(self) -> Dict:
        """Get system health status"""
        health = {
            "overall": "healthy",
            "components": {
                "nlp": "available" if self.nlp_detector else "unavailable",
                "llm": "available" if self.api_key else "unavailable",
                "tts": "available" if self.tts_available else "unavailable"
            }
        }
        
        # Determine overall health
        unavailable_count = sum(1 for status in health["components"].values() 
                              if status == "unavailable")
        
        if unavailable_count == 0:
            health["overall"] = "healthy"
        elif unavailable_count <= 1:
            health["overall"] = "degraded"
        else:
            health["overall"] = "unhealthy"
        
        return health
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        # This would clean up old TTS audio files
        # Implementation depends on file management strategy
        pass


# Global workflow manager instance
workflow_manager = WebWorkflowManager()


def get_workflow_manager():
    """Get the global workflow manager instance"""
    return workflow_manager
