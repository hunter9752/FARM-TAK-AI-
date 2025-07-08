# Real-time Speech-to-Text Application

A Python application for real-time speech-to-text transcription using the Vosk library. Supports Hindi, Marathi, Tamil, and English languages with offline processing.

## Features

- 🎤 Real-time microphone audio capture
- 🌍 Multi-language support (English, Hindi, Marathi, Tamil)
- 🔄 Live transcription with partial and final results
- 🔒 Completely offline - no cloud APIs required
- 🎯 Clear visual feedback for transcription status

## Requirements

- Python 3.7+
- Microphone access
- Vosk language models (downloaded separately)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Vosk Models:**
   
   Create a `models` directory and download the required language models:
   
   ```bash
   mkdir models
   cd models
   ```
   
   **English Model:**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
   unzip vosk-model-en-us-0.22.zip
   ```
   
   **Hindi Model:**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip
   unzip vosk-model-hi-0.22.zip
   ```
   
   **Marathi Model:**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-mr-0.22.zip
   unzip vosk-model-mr-0.22.zip
   ```
   
   **Tamil Model:**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-ta-0.22.zip
   unzip vosk-model-ta-0.22.zip
   ```

## Directory Structure

After setup, your directory should look like:
```
VOSK STT MODEL/
├── realtime_stt.py
├── requirements.txt
├── README.md
└── models/
    ├── vosk-model-en-us-0.22/
    ├── vosk-model-hi-0.22/
    ├── vosk-model-mr-0.22/
    └── vosk-model-ta-0.22/
```

## Usage

1. **Run the application:**
   ```bash
   python realtime_stt.py
   ```

2. **Select a language:**
   - Choose from: `en` (English), `hi` (Hindi), `mr` (Marathi), `ta` (Tamil)

3. **Start speaking:**
   - The application will show partial results as you speak
   - Final results are displayed when you pause
   - Press `Ctrl+C` to stop

## Example Output

```
============================================================
🎤 Real-time Speech-to-Text Application
============================================================
Supported Languages:
  EN: English
  HI: Hindi
  MR: Marathi
  TA: Tamil
============================================================

Enter language code (en/hi/mr/ta): en
✅ Selected: English

🔄 Loading English model...
✅ Model loaded successfully!

🎯 Starting transcription...
💡 Speak into your microphone (Ctrl+C to stop)
------------------------------------------------------------
🎤 Listening... (Sample rate: 16000 Hz)
... hello how are you
✅ Final: hello how are you today
... this is a test
✅ Final: this is a test of the speech recognition system
```

## Troubleshooting

### Model Not Found Error
If you see "Model not found" error:
1. Ensure models are downloaded to the correct `models/` directory
2. Check that model directories contain required files (am, final.mdl, etc.)
3. Verify model names match the expected format

### Audio Issues
If microphone is not working:
1. Check microphone permissions
2. Ensure microphone is not being used by other applications
3. Try running with administrator privileges (Windows)

### Performance Issues
For better performance:
1. Use a good quality microphone
2. Minimize background noise
3. Speak clearly and at moderate pace
4. Ensure sufficient system resources

## Model Information

| Language | Model Size | Accuracy | Use Case |
|----------|------------|----------|----------|
| English  | ~50MB      | High     | General purpose |
| Hindi    | ~45MB      | Good     | Indian English + Hindi |
| Marathi  | ~40MB      | Good     | Regional Indian language |
| Tamil    | ~42MB      | Good     | South Indian language |

## License

This project uses the Vosk library which is licensed under Apache 2.0.
Individual language models may have their own licensing terms.
