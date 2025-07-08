# 🌾 Farmer Voice Agent - AI कृषि सलाहकार

## 📞 Real-Time Voice Call System for Farmers

A complete AI-powered voice call system that provides real-time farming advice to farmers in Hindi. The system works like a phone call where farmers can speak naturally and get expert agricultural guidance.

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

1. **Clone/Download the project**
   ```bash
   cd "VOSK STT MODEL/website"
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-cors requests gtts
   ```

3. **Set up API keys**
   - Ensure GROQ API key is configured in `../llm/.env`
   - Format: `GROQ_API_KEY=your_api_key_here`

4. **Run the application**
   ```bash
   python FINAL_FARMER_VOICE_AGENT.py
   ```

5. **Open in browser**
   - Go to: http://localhost:5000
   - Allow microphone access when prompted
   - Click the green call button to start

---

## 🧪 Testing

### Run Complete Test Suite
```bash
cd test
python complete_test_suite.py
```

### Manual Testing
1. **Text Input Test**: Use the debug system at http://localhost:5014
2. **Voice Input Test**: Click "🎤 Test Voice" and speak
3. **API Test**: Check individual API endpoints

### Test Coverage
- ✅ API Connectivity
- ✅ Farming Advice Generation
- ✅ Voice Generation
- ✅ System Performance
- ✅ Error Handling

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

### Ending a Call
- Click the red "📵" button
- Or close the browser tab

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
GROQ_API_KEY=your_groq_api_key_here
```

### Server Settings
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **Debug**: False (production)
- **Timeout**: 20 seconds for API calls

### Voice Settings
- **Language**: Hindi (hi-IN)
- **Recognition**: Continuous with auto-restart
- **Confidence Threshold**: 0.3
- **Audio Format**: MP3

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
- Verify GROQ API key is set
- Check internet connectivity
- Try restarting the server

**Audio not playing**
- Check browser audio permissions
- Ensure speakers/headphones are working
- Try refreshing the page

### Debug Mode
Run the test system for debugging:
```bash
python simple_test_voice.py
# Open http://localhost:5014
```

---

## 📁 Project Structure

```
website/
├── FINAL_FARMER_VOICE_AGENT.py    # Main production system
├── README.md                       # This documentation
├── test/
│   ├── complete_test_suite.py     # Complete test suite
│   ├── simple_test_voice.py       # Debug system
│   └── [other test files]         # Additional tests
└── [other files]                  # Development files
```

---

## 🤝 Contributing

### Development Setup
1. Use the debug system for testing
2. Run test suite before committing
3. Follow Hindi language standards
4. Test with real farmers for feedback

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

For technical support or farming advice:
- Check the troubleshooting section
- Run the test suite
- Review server logs
- Test with debug system

---

**🌾 Made with ❤️ for Indian Farmers 🌾**
