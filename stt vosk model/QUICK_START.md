# 🚀 Quick Start Guide - STT Vosk Model

Complete Speech-to-Text application with enhanced accuracy features.

## 📁 **Project Structure**

```
stt vosk model/
├── 🎤 MAIN APPLICATIONS
│   ├── realtime_stt.py          # Basic STT application
│   ├── improved_stt.py          # Enhanced STT with accuracy improvements
│   └── enhanced_stt.py          # Advanced STT (requires scipy)
│
├── 🔧 UTILITIES
│   ├── download_models.py       # Model downloader
│   ├── test_audio.py           # Audio system tester
│   └── test_stt.py             # Application tester
│
├── 📚 DOCUMENTATION
│   ├── README.md               # Complete documentation
│   ├── ACCURACY_IMPROVEMENT_GUIDE.md  # Accuracy tips
│   └── QUICK_START.md          # This file
│
├── ⚙️ SETUP
│   ├── requirements.txt        # Python dependencies
│   ├── setup_environment.bat   # Windows setup script
│   └── setup_environment.sh    # Linux/Mac setup script
│
├── 🎬 DEMO
│   └── demo.py                 # Application demo
│
└── 🤖 MODELS
    └── models/                 # Vosk language models
        ├── vosk-model-small-en-us-0.15/  # English (working)
        └── vosk-model-hi-0.22/           # Hindi (if downloaded)
```

## ⚡ **Quick Start (3 Steps)**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Test Your System**
```bash
python test_audio.py
```

### **Step 3: Start Transcribing**
```bash
python improved_stt.py
```

## 🎯 **Which Application to Use?**

### **🟢 Recommended: `improved_stt.py`**
- **Best balance** of accuracy and performance
- **Adaptive gain control** (15x automatic adjustment)
- **Real-time feedback** with visual indicators
- **Enhanced post-processing** 
- **Confidence scoring**
- **No heavy dependencies**

### **🟡 Basic: `realtime_stt.py`**
- **Simple and fast**
- **Minimal dependencies**
- **Good for testing**
- **Basic functionality**

### **🔴 Advanced: `enhanced_stt.py`**
- **Maximum accuracy** (requires scipy, noisereduce)
- **Advanced audio filtering**
- **Noise reduction**
- **Heavy processing**

## 🎤 **Usage Examples**

### **Basic Usage:**
```bash
cd "stt vosk model"
python improved_stt.py
# Select: en
# Start speaking!
```

### **Download More Languages:**
```bash
python download_models.py hi    # Hindi
python download_models.py mr    # Marathi  
python download_models.py ta    # Tamil
python download_models.py all   # All languages
```

### **Test Audio System:**
```bash
python test_audio.py
# Check if microphone is working
```

## 📊 **Expected Output**

### **Audio Feedback:**
```
Audio: |███████████████████████████████████| 0.155 🟢 EXCELLENT (Gain: 15.0x)
```

### **Transcription Results:**
```
✅ [1] Hello world.
   Confidence: 🟢 HIGH (0.85) | Avg: 0.85

✅ [2] This is working great.
   Confidence: 🟡 MEDIUM (0.72) | Avg: 0.78
```

### **Session Summary:**
```
📊 Session Stats:
   Transcriptions: 15
   Average Confidence: 0.78
   Final Adaptive Gain: 12.5x
```

## 🎯 **Optimal Settings**

### **Audio Levels:**
- 🟢 **EXCELLENT** (>0.08): Perfect - keep this level
- 🟡 **GOOD** (0.04-0.08): Good - can speak a bit louder
- 🟠 **OK** (0.02-0.04): Acceptable - speak louder
- 🔴 **TOO LOW** (<0.02): Speak much louder or move closer

### **Speaking Tips:**
1. **Distance**: 15-30cm from microphone
2. **Volume**: Speak clearly and moderately loud
3. **Pace**: Moderate speed, not too fast
4. **Environment**: Quiet room, minimal background noise
5. **Pronunciation**: Clear articulation

## 🔧 **Troubleshooting**

### **Problem: "No module named 'vosk'"**
**Solution:**
```bash
pip install vosk sounddevice numpy
```

### **Problem: "Model not found"**
**Solution:**
```bash
python download_models.py en
```

### **Problem: "Audio levels always low"**
**Solutions:**
1. Move closer to microphone
2. Increase system microphone volume
3. Check microphone permissions
4. Try different microphone

### **Problem: "Poor accuracy"**
**Solutions:**
1. Speak more clearly and slowly
2. Reduce background noise
3. Aim for 🟢 EXCELLENT audio levels
4. Use complete sentences
5. Check language model matches spoken language

### **Problem: "Application crashes"**
**Solutions:**
1. Check Python version (3.8+ required)
2. Reinstall dependencies
3. Check microphone permissions
4. Try basic version first: `python realtime_stt.py`

## 📱 **Supported Languages**

| Code | Language | Model Status | Download Command |
|------|----------|--------------|------------------|
| `en` | English  | ✅ Ready     | Already downloaded |
| `hi` | Hindi    | ⬇️ Available | `python download_models.py hi` |
| `mr` | Marathi  | ⬇️ Available | `python download_models.py mr` |
| `ta` | Tamil    | ⬇️ Available | `python download_models.py ta` |

## 🎯 **Performance Expectations**

### **With Good Audio Quality:**
- **Accuracy**: 85-95%
- **Response Time**: <200ms
- **Confidence**: 0.7-0.9 average

### **With Excellent Conditions:**
- **Accuracy**: 95%+
- **Response Time**: <100ms  
- **Confidence**: 0.8+ average

## 🚀 **Next Steps**

1. **Test the system**: `python test_audio.py`
2. **Start with basic**: `python realtime_stt.py`
3. **Upgrade to improved**: `python improved_stt.py`
4. **Download more languages**: `python download_models.py all`
5. **Read full guide**: `README.md`
6. **Optimize accuracy**: `ACCURACY_IMPROVEMENT_GUIDE.md`

## 📞 **Support**

### **Common Commands:**
```bash
# Quick test
python test_audio.py

# Basic STT
python realtime_stt.py

# Best STT (recommended)
python improved_stt.py

# Download Hindi
python download_models.py hi

# Download all languages
python download_models.py all

# Run demo
python demo.py
```

### **File Purposes:**
- **`improved_stt.py`** → **USE THIS** for best results
- **`realtime_stt.py`** → Basic version for testing
- **`download_models.py`** → Get language models
- **`test_audio.py`** → Check if microphone works
- **`requirements.txt`** → Install dependencies

---

## 🎉 **You're Ready!**

Your STT Vosk Model is now organized and ready to use. Start with:

```bash
cd "stt vosk model"
python improved_stt.py
```

**Happy transcribing!** 🎤✨
