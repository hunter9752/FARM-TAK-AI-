# 🤖 Ollama Setup Guide for Farmer LLM Assistant

Complete guide to setup Ollama for farmer-specific LLM responses.

## 🚀 **Quick Setup (3 Steps)**

### **Step 1: Install Ollama**
```bash
# Windows (Download from website)
# Go to: https://ollama.ai
# Download and install Ollama for Windows

# Linux/Mac (Terminal)
curl -fsSL https://ollama.ai/install.sh | sh
```

### **Step 2: Start Ollama Service**
```bash
# Start Ollama server
ollama serve
```

### **Step 3: Pull Farmer-Optimized Model**
```bash
# Pull recommended model (3B parameters - good balance)
ollama pull llama3.2:3b

# Alternative models:
# ollama pull llama3.2:1b    # Faster, less accurate
# ollama pull llama3.1:8b    # Slower, more accurate
```

## 🎯 **Recommended Models for Farmers**

### **🟢 llama3.2:3b (RECOMMENDED)**
- **Size**: ~2GB download
- **Speed**: Fast responses (2-5 seconds)
- **Quality**: Good for farming advice
- **Memory**: ~4GB RAM required
- **Best for**: Real-time farmer assistance

### **🟡 llama3.2:1b (FAST)**
- **Size**: ~1GB download  
- **Speed**: Very fast (1-2 seconds)
- **Quality**: Basic but adequate
- **Memory**: ~2GB RAM required
- **Best for**: Quick responses, low-end hardware

### **🔴 llama3.1:8b (HIGH QUALITY)**
- **Size**: ~4.7GB download
- **Speed**: Slower (5-10 seconds)
- **Quality**: Excellent farming knowledge
- **Memory**: ~8GB RAM required
- **Best for**: Detailed agricultural consultation

## 🔧 **Installation Steps**

### **Windows Installation:**

1. **Download Ollama:**
   - Go to https://ollama.ai
   - Click "Download for Windows"
   - Run the installer

2. **Start Ollama:**
   ```cmd
   # Open Command Prompt or PowerShell
   ollama serve
   ```

3. **Pull Model:**
   ```cmd
   # In another terminal window
   ollama pull llama3.2:3b
   ```

### **Linux Installation:**

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Service:**
   ```bash
   ollama serve
   ```

3. **Pull Model:**
   ```bash
   ollama pull llama3.2:3b
   ```

## 🧪 **Testing Ollama Setup**

### **Test 1: Check if Ollama is Running**
```bash
curl http://localhost:11434/api/tags
```

**Expected Output:**
```json
{
  "models": [
    {
      "name": "llama3.2:3b",
      "modified_at": "2024-01-01T00:00:00Z",
      "size": 2019393792
    }
  ]
}
```

### **Test 2: Test Model Response**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "गेहूं की खेती के लिए सलाह दो",
  "stream": false
}'
```

### **Test 3: Test with Python**
```python
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.2:3b", 
    "prompt": "मुझे बीज की जानकारी चाहिए",
    "stream": False
})

print(response.json()["response"])
```

## ⚙️ **Configuration Options**

### **Model Parameters:**
```json
{
  "temperature": 0.7,    // Creativity (0.1-1.0)
  "top_p": 0.9,         // Diversity (0.1-1.0)  
  "max_tokens": 200,    // Response length
  "stop": ["\n\n"]      // Stop sequences
}
```

### **Performance Tuning:**
```bash
# Set GPU usage (if available)
export OLLAMA_GPU_LAYERS=32

# Set memory limit
export OLLAMA_MAX_LOADED_MODELS=1

# Set number of threads
export OLLAMA_NUM_THREAD=4
```

## 🌾 **Farmer-Specific Optimization**

### **Custom System Prompts:**
```
आप एक अनुभवी कृषि विशेषज्ञ हैं। किसानों को सरल हिंदी में 
व्यावहारिक सलाह दें। जवाब छोटा और तुरंत लागू होने वाला हो।
```

### **Response Guidelines:**
- **Language**: Primary Hindi, secondary English
- **Length**: 3-4 sentences maximum
- **Style**: Practical, actionable advice
- **Tone**: Friendly, respectful (आप, जी)

## 🚨 **Troubleshooting**

### **Problem: "Connection refused"**
**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve
```

### **Problem: "Model not found"**
**Solution:**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3.2:3b
```

### **Problem: "Out of memory"**
**Solutions:**
1. Use smaller model: `ollama pull llama3.2:1b`
2. Close other applications
3. Increase virtual memory
4. Use cloud deployment

### **Problem: "Slow responses"**
**Solutions:**
1. Use faster model: `llama3.2:1b`
2. Reduce max_tokens to 100
3. Use GPU acceleration
4. Increase system RAM

## 📊 **Performance Expectations**

### **Hardware Requirements:**

| Model | RAM | Storage | CPU | Response Time |
|-------|-----|---------|-----|---------------|
| llama3.2:1b | 2GB | 1GB | 2 cores | 1-2 seconds |
| llama3.2:3b | 4GB | 2GB | 4 cores | 2-5 seconds |
| llama3.1:8b | 8GB | 5GB | 8 cores | 5-10 seconds |

### **Expected Quality:**

| Model | Accuracy | Hindi Support | Farming Knowledge |
|-------|----------|---------------|-------------------|
| llama3.2:1b | Good | Basic | Adequate |
| llama3.2:3b | Very Good | Good | Good |
| llama3.1:8b | Excellent | Excellent | Excellent |

## 🔄 **Alternative LLM Options**

### **If Ollama doesn't work:**

1. **OpenAI API** (Paid):
   ```python
   import openai
   openai.api_key = "your-api-key"
   ```

2. **Hugging Face Transformers** (Local):
   ```python
   from transformers import pipeline
   generator = pipeline("text-generation", model="microsoft/DialoGPT-medium")
   ```

3. **Google Gemini API** (Free tier):
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your-api-key")
   ```

## ✅ **Verification Checklist**

Before running the farmer assistant:

- [ ] Ollama installed and running
- [ ] Model downloaded (llama3.2:3b)
- [ ] API responding on localhost:11434
- [ ] Python requests library installed
- [ ] NLP system working
- [ ] Test query successful

## 🎯 **Ready to Use!**

Once setup is complete, run:

```bash
cd llm
python farmer_llm_assistant.py
```

**Your farmer assistant will now provide intelligent, human-like responses powered by LLM!** 🌾🤖✨
