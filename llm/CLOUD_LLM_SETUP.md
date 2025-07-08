# 🌐 Cloud LLM Setup Guide for Farmer Assistant

Complete guide to setup internet-connected LLM APIs with real-time data for better farming responses.

## 🎯 **Why Cloud LLM?**

### **Advantages over Local LLM:**
- ✅ **Better Quality**: Advanced models (GPT-3.5, Llama 3 70B, Gemini Pro)
- ✅ **Real-time Data**: Weather, market prices, agricultural news
- ✅ **No Hardware Requirements**: No need for 8GB+ RAM
- ✅ **Always Updated**: Latest agricultural knowledge
- ✅ **Faster Setup**: No model downloads required
- ✅ **Multiple Options**: Fallback between different providers

### **Comparison:**

| Feature | Local LLM | Cloud LLM |
|---------|-----------|-----------|
| **Quality** | Good | Excellent |
| **Speed** | 2-5s | 1-3s |
| **Hardware** | 8GB+ RAM | Any computer |
| **Real-time Data** | No | Yes |
| **Setup Time** | 30 minutes | 5 minutes |
| **Cost** | Free | Free tier + paid |

## 🚀 **Quick Setup (3 Steps)**

### **Step 1: Get API Keys (Choose One or More)**

#### **🟢 Groq (RECOMMENDED - Fast & Free)**
```
1. Go to: https://console.groq.com/
2. Sign up with email
3. Go to API Keys section
4. Create new API key
5. Copy the key
```
**Benefits**: Very fast, good free tier, excellent for farming

#### **🟡 OpenAI (High Quality)**
```
1. Go to: https://platform.openai.com/api-keys
2. Sign up and verify phone
3. Create API key
4. Add payment method (required)
5. Copy the key
```
**Benefits**: Highest quality, but requires payment

#### **🟡 Google Gemini (Free)**
```
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Copy the key
```
**Benefits**: Free, good quality, Google's latest AI

### **Step 2: Configure API Keys**

#### **Option A: Create Config File**
```bash
cd llm
cp api_keys_template.json api_keys.json
# Edit api_keys.json with your actual keys
```

**Edit `api_keys.json`:**
```json
{
  "groq": "gsk_your_actual_groq_key_here",
  "openai": "sk-your_actual_openai_key_here",
  "gemini": "your_actual_gemini_key_here"
}
```

#### **Option B: Environment Variables**
```bash
# Windows
set GROQ_API_KEY=gsk_your_actual_groq_key_here
set OPENAI_API_KEY=sk_your_actual_openai_key_here
set GEMINI_API_KEY=your_actual_gemini_key_here

# Linux/Mac
export GROQ_API_KEY=gsk_your_actual_groq_key_here
export OPENAI_API_KEY=sk_your_actual_openai_key_here
export GEMINI_API_KEY=your_actual_gemini_key_here
```

### **Step 3: Test Cloud LLM**
```bash
cd llm
python cloud_llm_assistant.py
```

## 🌐 **Supported LLM Providers**

### **1. Groq (RECOMMENDED)**
- **Model**: Llama 3 70B (8192 context)
- **Speed**: Very fast (1-2 seconds)
- **Cost**: Free tier: 6,000 tokens/minute
- **Best for**: Real-time farming assistance
- **Setup**: https://console.groq.com/

### **2. OpenAI**
- **Model**: GPT-3.5-turbo
- **Speed**: Fast (2-3 seconds)
- **Cost**: $0.0015 per 1K tokens (~₹0.12)
- **Best for**: Highest quality responses
- **Setup**: https://platform.openai.com/

### **3. Google Gemini**
- **Model**: Gemini Pro
- **Speed**: Medium (3-4 seconds)
- **Cost**: Free tier: 60 requests/minute
- **Best for**: Free high-quality responses
- **Setup**: https://makersuite.google.com/

### **4. Hugging Face (Optional)**
- **Model**: Various open-source models
- **Speed**: Variable
- **Cost**: Free tier available
- **Best for**: Experimental features
- **Setup**: https://huggingface.co/

## 📊 **Real-time Data Integration**

### **Weather Data (Optional)**
```bash
# Get free API key from OpenWeatherMap
# https://openweathermap.org/api

# Add to api_keys.json:
"weather_api_key": "your_openweathermap_key"
```

**Benefits**: Weather-based farming advice
- "आज बारिश है तो छिड़काव न करें"
- "तापमान 35°C है, सिंचाई करें"

### **Market Prices (Optional)**
```bash
# Get free API key from data.gov.in
# https://data.gov.in/

# Add to api_keys.json:
"data_gov_api_key": "your_data_gov_key"
```

**Benefits**: Current market price information
- "आज गेहूं ₹2200 प्रति क्विंटल है"
- "कल बेचना बेहतर होगा"

### **Agricultural News (Optional)**
```bash
# Get free API key from NewsAPI
# https://newsapi.org/

# Add to api_keys.json:
"news_api_key": "your_newsapi_key"
```

**Benefits**: Latest agricultural updates
- "सरकार ने MSP बढ़ाया है"
- "नए कीट का प्रकोप रिपोर्ट हुआ है"

## 🧪 **Testing & Validation**

### **Test 1: Basic Cloud LLM**
```bash
cd llm
python cloud_llm_assistant.py
```

**Expected Output:**
```
🌐 Cloud LLM Farmer Assistant - Real-time Data Integration
✅ Available LLM APIs: groq
🎯 Using: groq
✅ System Ready!

🎤 आपका सवाल: गेहूं के लिए खाद की सलाह दो

🔍 Step 1: Detecting intent...
🎯 Intent: fertilizer_advice (Confidence: 0.80)
🌐 Step 2: Generating cloud LLM response with real-time data...

🌾 किसान सहायक का जवाब:
💬 गेहूं के लिए 120:60:40 NPK अनुपात में खाद दें। बुआई के समय DAP 
और यूरिया का प्रयोग करें। मिट्टी परीक्षण कराकर जिंक की कमी भी पूरी करें।

⏱️ Response Time: 2.1s
🌐 LLM Provider: groq
📊 Confidence: 0.80
🎯 Intent: fertilizer_advice
```

### **Test 2: Complete Pipeline**
```bash
cd llm
python complete_cloud_farmer_assistant.py
```

**Expected Flow:**
```
🌐 Complete Cloud Farmer Assistant
🎤 → 🧠 → 🌐 → 📊 (Speech → Intent → Cloud LLM → Real-time Data)

🤖 Current LLM: groq (llama3-70b-8192)
📊 Real-time Data: weather, market_prices (if configured)

🎤 Listening for speech...
[User speaks]: "मेरी फसल में कीड़े हैं"

🔄 Processing through cloud pipeline...
🤖 Cloud Farmer Assistant का जवाब:
💬 तुरंत कीटनाशक का छिड़काव करें। इमिडाक्लोप्रिड का प्रयोग करें। 
आज मौसम साफ है तो शाम को छिड़काव करना बेहतर होगा।

⏱️ Total Response Time: 3.4s
🌐 LLM Provider: groq
📊 Real-time Data: weather
```

## 🎯 **Usage Examples**

### **Basic Farming Queries:**
```
👨‍🌾 "मुझे गेहूं के बीज चाहिए"
🤖 "गेहूं के लिए HD-2967 या PBW-343 किस्म अच्छी है। नवंबर-दिसंबर में 
    बुआई करें। 100-120 किलो बीज प्रति हेक्टेयर चाहिए।"

👨‍🌾 "आज मंडी भाव क्या है"
🤖 "आज गेहूं का भाव ₹2200-2300 प्रति क्विंटल है। eNAM पोर्टल पर 
    बेहतर दाम मिल सकता है। कल तक इंतजार करना बेहतर होगा।"
```

### **Weather-Integrated Responses:**
```
👨‍🌾 "कब छिड़काव करूं"
🤖 "आज तापमान 28°C है और हवा शांत है। शाम 5-6 बजे छिड़काव करना 
    बेहतर होगा। कल बारिश की संभावना है तो आज ही कर लें।"
```

### **Market-Integrated Responses:**
```
👨‍🌾 "फसल कब बेचूं"
🤖 "आज गेहूं ₹2250 प्रति क्विंटल है। पिछले हफ्ते से 50 रुपए बढ़ा है। 
    अगले सप्ताह और बढ़ने की उम्मीद है तो थोड़ा इंतजार करें।"
```

## 🔧 **Advanced Configuration**

### **Switch Between LLM Providers:**
```python
# In interactive mode, type 'switch' to change provider
🎤 आपका सवाल: switch
Available APIs: ['groq', 'openai', 'gemini']
Switched to: openai
```

### **Custom System Prompts:**
```python
# Edit cloud_llm_assistant.py
farmer_prompts = {
    "fertilizer_advice": {
        "system_prompt": "आप एक मिट्टी विशेषज्ञ हैं जो current weather और 
                         market prices के साथ सलाह देते हैं..."
    }
}
```

### **Response Quality Control:**
```python
# Adjust response parameters
payload = {
    "temperature": 0.7,    # Creativity (0.1-1.0)
    "max_tokens": 200,     # Response length
    "top_p": 0.9          # Diversity
}
```

## 💰 **Cost Estimation**

### **Free Tiers:**
- **Groq**: 6,000 tokens/minute (≈300 farmer queries/day)
- **Gemini**: 60 requests/minute (≈3,600 queries/day)
- **OpenAI**: $5 free credit (≈3,000 queries)

### **Paid Usage (if needed):**
- **OpenAI**: ₹0.12 per query (very affordable)
- **Groq**: Pay-as-you-go after free tier
- **Gemini**: Pay-per-use after free tier

### **Daily Cost for 100 Farmer Queries:**
- **Groq**: Free (within limits)
- **Gemini**: Free (within limits)
- **OpenAI**: ₹12 per day (very affordable)

## 🚨 **Troubleshooting**

### **Problem: "No API keys found"**
**Solution:**
```bash
# Check if api_keys.json exists and has correct format
cat api_keys.json

# Or set environment variable
set GROQ_API_KEY=your_actual_key
```

### **Problem: "API request failed"**
**Solutions:**
1. Check internet connection
2. Verify API key is correct
3. Check API quota/limits
4. Try different provider: type 'switch'

### **Problem: "Slow responses"**
**Solutions:**
1. Use Groq (fastest)
2. Check internet speed
3. Reduce max_tokens to 100

### **Problem: "Poor Hindi quality"**
**Solutions:**
1. Use OpenAI or Gemini for better Hindi
2. Adjust system prompts
3. Add more Hindi context

## 🎉 **Production Deployment**

### **Recommended Setup:**
- **Primary LLM**: Groq (fast, free tier)
- **Backup LLM**: Gemini (free, good quality)
- **Real-time Data**: Weather API (optional)
- **Monitoring**: Response time and quality tracking

### **Scaling:**
- **Small Farm**: Free tiers sufficient
- **Large Operation**: Paid APIs (very affordable)
- **Commercial**: Multiple API keys for redundancy

---

## 🌾 **Ready for Cloud-Powered Farming!**

Your farmer assistant now has access to:
- **🌐 Advanced LLM models** (GPT-3.5, Llama 3 70B, Gemini Pro)
- **📊 Real-time data** (Weather, market prices, news)
- **⚡ Fast responses** (1-3 seconds)
- **🌍 Internet connectivity** for latest information

**Happy Cloud Farming!** 🌾🌐🤖✨
