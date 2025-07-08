# 🌾 Farmer Voice Agent - AI कृषि सलाहकार

## 📞 Real-Time Voice Call System for Farmers

A complete AI-powered voice call system that provides real-time farming advice to farmers in Hindi. The system works like a phone call where farmers can speak naturally and get expert agricultural guidance.

![Farmer Voice Agent](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Language](https://img.shields.io/badge/Language-Hindi-orange)
![AI](https://img.shields.io/badge/AI-Groq%20LLM-blue)
![Voice](https://img.shields.io/badge/Voice-Google%20TTS-red)

---

## 🎯 Features

### 🎤 Voice Interaction
- **Real-Time Voice Recognition**: Browser-based speech-to-text
- **Natural Hindi Conversation**: Complete Hindi language support
- **Phone Call Experience**: Just like calling an expert
- **Continuous Listening**: Automatic voice recognition restart

### 🤖 AI-Powered Advice
- **Expert Farming Knowledge**: Specialized agricultural guidance
- **Multiple Topics**: Crops, fertilizers, pest control, irrigation, market prices
- **Practical Solutions**: Actionable advice for farmers
- **Context-Aware**: Understands farming context and intent

### 🔊 Voice Output
- **Hindi Text-to-Speech**: Natural voice responses
- **Real-Time Audio**: Immediate voice feedback
- **Clear Communication**: Professional voice quality

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Chrome or Edge browser (for voice recognition)
- Internet connection
- Microphone access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/hunter9752/farmer-voice-agent.git
   cd farmer-voice-agent
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-cors requests gtts
   ```

3. **Set up API keys**
   ```bash
   # Create llm/.env file with your API keys
   echo "GROQ_API_KEY=your_groq_api_key_here" > llm/.env
   ```

4. **Run the application**
   ```bash
   python website/FINAL_FARMER_VOICE_AGENT.py
   ```

5. **Open in browser**
   - Go to: http://localhost:5000
   - Allow microphone access when prompted
   - Click the green call button to start

---

## 🧪 Testing

### Run Complete Test Suite
```bash
cd website/test
python complete_test_suite.py
```

### Manual Testing
1. **Text Input Test**: Use the debug system at http://localhost:5014
2. **Voice Input Test**: Click "🎤 Test Voice" and speak
3. **API Test**: Check individual API endpoints

---

## 📋 Usage Guide

### Starting a Voice Call
1. Open http://localhost:5000 in Chrome/Edge
2. Click the green "📞" button
3. Allow microphone access
4. Wait for "Call Connected" status
5. Speak your farming question in Hindi

### Example Conversations
```
👨‍🌾 "गेहूं के लिए खाद की सलाह दो"
🤖 "भाई, गेहूं के लिए DAP और यूरिया का मिश्रण उपयोग करें..."

👨‍🌾 "मेरी फसल में कीड़े लग गए हैं"
🤖 "जी भाई, कीड़ों के लिए नीम का तेल स्प्रे करें..."

👨‍🌾 "आज मंडी भाव क्या है"
🤖 "भाई, मंडी भाव के लिए local market check करें..."
```

---

## 🏗️ System Architecture

### Components
1. **Frontend**: HTML/CSS/JavaScript voice interface
2. **Backend**: Flask API server
3. **Voice Recognition**: Browser WebSpeech API
4. **AI Processing**: Groq LLM (Llama3-70B)
5. **Voice Generation**: Google Text-to-Speech
6. **Language**: Hindi (hi-IN)

### API Endpoints
- `GET /` - Main voice interface
- `POST /api/farming-advice` - Get farming advice
- `POST /api/generate-voice` - Generate voice audio
- `GET /api/health` - System health check

### Data Flow
```
Voice Input → STT → AI Processing → TTS → Voice Output
     ↓           ↓         ↓         ↓         ↓
  Browser → JavaScript → Flask → Groq → gTTS → Audio
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here

# Optional API Keys (for additional features)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Server Settings
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **Debug**: False (production)
- **Timeout**: 20 seconds for API calls

---

## 📊 Performance

### Response Times
- **Average**: < 10 seconds
- **Maximum**: < 20 seconds
- **Voice Generation**: < 5 seconds

### System Requirements
- **RAM**: 512MB minimum
- **CPU**: Any modern processor
- **Network**: Stable internet connection
- **Browser**: Chrome 25+ or Edge 79+

---

## 🛠️ Troubleshooting

### Common Issues

**Voice not working**
- Check microphone permissions
- Use Chrome or Edge browser
- Ensure stable internet connection

**No AI response**
- Verify API keys are set in llm/.env
- Check internet connectivity
- Try restarting the server

**Audio not playing**
- Check browser audio permissions
- Ensure speakers/headphones are working
- Try refreshing the page

---

## 📁 Project Structure

```
farmer-voice-agent/
├── website/
│   ├── FINAL_FARMER_VOICE_AGENT.py    # Main production system
│   ├── README.md                       # Documentation
│   ├── test/                          # Test files
│   │   ├── complete_test_suite.py     # Full test suite
│   │   └── simple_test_voice.py       # Debug system
│   └── simple_nlp_detector.py         # NLP system
├── nlp/                               # NLP models and data
├── llm/                               # AI models and config
├── tts model/                         # TTS system
├── .gitignore                         # Git ignore file
└── README.md                          # This file
```

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Adding Features
1. Create new API endpoints in main file
2. Add corresponding tests
3. Update documentation
4. Test thoroughly

---

## 📄 License

This project is developed for farmers and agricultural education.

---

## 🙏 Acknowledgments

- **Groq**: For LLM API services
- **Google**: For Text-to-Speech services
- **Farmers**: For feedback and requirements
- **Open Source Community**: For tools and libraries

---

## 📞 Support

For technical support:
- Check the troubleshooting section
- Run the test suite
- Review server logs
- Test with debug system

---

**🌾 Made with ❤️ for Indian Farmers 🌾**

## 🔗 Links

- **Live Demo**: http://localhost:5000 (when running)
- **Documentation**: [README.md](README.md)
- **Test Suite**: [website/test/](website/test/)
- **API Documentation**: Available in code comments

---

## 🏷️ Tags

`agriculture` `farming` `voice-ai` `hindi` `real-time` `speech-recognition` `text-to-speech` `groq` `flask` `python` `farmers` `india` `ai-assistant` `voice-call`
