/**
 * Advanced Real-Time Voice Call System
 * Features: Continuous listening, voice interruption, real-time responses
 */

class RealTimeVoiceCall {
    constructor() {
        this.isCallActive = false;
        this.isListening = false;
        this.isSpeaking = false;
        this.isMuted = false;
        this.recognition = null;
        this.currentAudio = null;
        this.conversationHistory = [];
        this.listeningTimeout = null;
        this.silenceTimeout = null;
        this.interruptionCount = 0;
        this.responseQueue = [];
        this.currentResponseId = null;
        
        // Voice settings
        this.settings = {
            volume: 0.8,
            autoInterrupt: true,
            continuousListen: true,
            silenceThreshold: 3000, // 3 seconds
            interruptionDelay: 500   // 0.5 seconds
        };
        
        this.initializeSystem();
    }
    
    initializeSystem() {
        console.log('🎤 Initializing Real-Time Voice Call System...');
        
        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window) {
            this.setupSpeechRecognition();
            console.log('✅ Speech recognition initialized');
        } else {
            console.error('❌ Speech recognition not supported');
            this.showError('Voice recognition not supported in this browser');
            return false;
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize UI
        this.updateUI();
        
        console.log('✅ Real-Time Voice Call System ready');
        return true;
    }
    
    setupSpeechRecognition() {
        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'hi-IN';
        this.recognition.maxAlternatives = 1;
        
        // Recognition event handlers
        this.recognition.onstart = () => {
            console.log('🎤 Voice recognition started');
            this.isListening = true;
            this.updateCallStatus('सुन रहा हूं... बोलिए', 'listening');
            this.updateVisualizer('listening');
        };
        
        this.recognition.onresult = (event) => {
            this.handleSpeechResult(event);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.handleRecognitionError(event.error);
        };
        
        this.recognition.onend = () => {
            console.log('🎤 Voice recognition ended');
            this.isListening = false;
            
            // Auto-restart if call is active and not muted
            if (this.isCallActive && !this.isMuted && this.settings.continuousListen) {
                setTimeout(() => {
                    this.startListening();
                }, 100);
            }
        };
    }
    
    handleSpeechResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            const confidence = event.results[i][0].confidence;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
                console.log(`🎤 Final transcript: "${transcript}" (confidence: ${confidence})`);
            } else {
                interimTranscript += transcript;
                console.log(`🎤 Interim transcript: "${transcript}"`);
            }
        }
        
        // Handle final transcript
        if (finalTranscript.trim()) {
            this.handleVoiceInput(finalTranscript.trim());
        }
        
        // Show interim results
        if (interimTranscript.trim()) {
            this.showInterimTranscript(interimTranscript.trim());
        }
    }
    
    handleVoiceInput(transcript) {
        console.log(`🎤 Processing voice input: "${transcript}"`);
        
        // Check for interruption
        if (this.isSpeaking && this.settings.autoInterrupt) {
            this.handleInterruption();
        }
        
        // Add user message to conversation
        this.addConversationItem('user', transcript);
        
        // Stop listening temporarily
        this.stopListening();
        
        // Process the query
        this.processVoiceQuery(transcript);
    }
    
    handleInterruption() {
        console.log('🛑 Voice interruption detected');
        
        // Stop current audio
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
        
        // Cancel current response
        if (this.currentResponseId) {
            this.cancelResponse(this.currentResponseId);
        }
        
        // Update state
        this.isSpeaking = false;
        this.interruptionCount++;
        
        // Show interruption indicator
        this.showInterruptionIndicator();
        
        // Clear response queue
        this.responseQueue = [];
        
        console.log(`🛑 Interruption handled (count: ${this.interruptionCount})`);
    }
    
    async processVoiceQuery(query) {
        const responseId = this.generateResponseId();
        this.currentResponseId = responseId;
        
        console.log(`🤖 Processing query: "${query}" (ID: ${responseId})`);
        
        this.updateCallStatus('सोच रहा हूं...', 'processing');
        this.updateVisualizer('processing');
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    responseId: responseId
                })
            });
            
            // Check if response was cancelled
            if (this.currentResponseId !== responseId) {
                console.log(`🛑 Response cancelled: ${responseId}`);
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                const aiResponse = result.llm_result.response;
                console.log(`🤖 AI response: "${aiResponse}" (ID: ${responseId})`);
                
                // Add AI response to conversation
                this.addConversationItem('ai', aiResponse);
                
                // Generate and play TTS
                await this.generateAndPlayTTS(aiResponse, responseId);
            } else {
                const errorMsg = 'माफ करें, कुछ गलती हुई है। कृपया दोबारा कोशिश करें।';
                this.addConversationItem('ai', errorMsg);
                await this.generateAndPlayTTS(errorMsg, responseId);
            }
            
        } catch (error) {
            console.error('Query processing error:', error);
            
            // Check if response was cancelled
            if (this.currentResponseId !== responseId) {
                return;
            }
            
            const errorMsg = 'नेटवर्क की समस्या है। कृपया दोबारा कोशिश करें।';
            this.addConversationItem('ai', errorMsg);
            await this.generateAndPlayTTS(errorMsg, responseId);
        }
    }
    
    async generateAndPlayTTS(text, responseId) {
        // Check if response was cancelled
        if (this.currentResponseId !== responseId) {
            console.log(`🛑 TTS cancelled: ${responseId}`);
            return;
        }
        
        console.log(`🔊 Generating TTS: "${text}" (ID: ${responseId})`);
        
        this.updateCallStatus('जवाब दे रहा हूं...', 'speaking');
        this.updateVisualizer('speaking');
        this.isSpeaking = true;
        
        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    responseId: responseId
                })
            });
            
            // Check if response was cancelled
            if (this.currentResponseId !== responseId) {
                console.log(`🛑 TTS response cancelled: ${responseId}`);
                return;
            }
            
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                this.currentAudio = new Audio(audioUrl);
                
                // Set volume
                this.currentAudio.volume = this.settings.volume;
                
                // Audio event handlers
                this.currentAudio.onended = () => {
                    console.log(`🔊 Audio playback ended: ${responseId}`);
                    this.handleAudioEnd(responseId);
                };
                
                this.currentAudio.onerror = (error) => {
                    console.error('Audio playback error:', error);
                    this.handleAudioError(responseId);
                };
                
                this.currentAudio.onpause = () => {
                    console.log(`🔊 Audio paused: ${responseId}`);
                };
                
                // Play audio
                await this.currentAudio.play();
                console.log(`🔊 Audio playback started: ${responseId}`);
                
            } else {
                throw new Error('TTS generation failed');
            }
            
        } catch (error) {
            console.error('TTS error:', error);
            this.handleAudioError(responseId);
        }
    }
    
    handleAudioEnd(responseId) {
        // Check if this is the current response
        if (this.currentResponseId === responseId) {
            this.isSpeaking = false;
            this.currentAudio = null;
            this.currentResponseId = null;
            
            // Resume listening if call is still active
            if (this.isCallActive && !this.isMuted) {
                setTimeout(() => {
                    this.startListening();
                }, this.settings.interruptionDelay);
            }
        }
    }
    
    handleAudioError(responseId) {
        if (this.currentResponseId === responseId) {
            this.isSpeaking = false;
            this.currentAudio = null;
            this.currentResponseId = null;
            
            if (this.isCallActive && !this.isMuted) {
                this.startListening();
            }
        }
    }
    
    startCall() {
        if (!this.initializeSystem()) return;
        
        console.log('📞 Starting real-time voice call');
        
        this.isCallActive = true;
        this.interruptionCount = 0;
        this.conversationHistory = [];
        
        this.updateCallStatus('कॉल शुरू हो गई - बोलना शुरू करें', 'listening');
        this.updateVisualizer('listening');
        
        // Update UI
        this.showCallControls();
        this.showConversationLog();
        
        // Start continuous listening
        this.startListening();
        
        // Add welcome message
        this.addConversationItem('ai', 'नमस्कार! मैं आपका AI कृषि सलाहकार हूं। आप मुझसे खेती के बारे में कोई भी सवाल पूछ सकते हैं।');
        
        console.log('✅ Real-time voice call started');
    }
    
    endCall() {
        console.log('📞 Ending real-time voice call');
        
        this.isCallActive = false;
        this.isListening = false;
        this.isSpeaking = false;
        
        // Stop recognition
        if (this.recognition) {
            this.recognition.stop();
        }
        
        // Stop current audio
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        
        // Cancel current response
        if (this.currentResponseId) {
            this.cancelResponse(this.currentResponseId);
        }
        
        // Clear timeouts
        if (this.listeningTimeout) clearTimeout(this.listeningTimeout);
        if (this.silenceTimeout) clearTimeout(this.silenceTimeout);
        
        // Update UI
        this.updateCallStatus('कॉल समाप्त', 'idle');
        this.updateVisualizer('idle');
        this.hideCallControls();
        
        console.log('✅ Real-time voice call ended');
        console.log(`📊 Call statistics: ${this.conversationHistory.length} messages, ${this.interruptionCount} interruptions`);
    }
    
    // Utility methods
    generateResponseId() {
        return `resp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    cancelResponse(responseId) {
        console.log(`🛑 Cancelling response: ${responseId}`);
        if (this.currentResponseId === responseId) {
            this.currentResponseId = null;
        }
    }
    
    startListening() {
        if (!this.isCallActive || this.isMuted || this.isListening) return;
        
        console.log('🎤 Starting voice listening');
        
        if (this.recognition) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Failed to start recognition:', error);
                // Retry after delay
                setTimeout(() => {
                    if (this.isCallActive && !this.isMuted) {
                        this.startListening();
                    }
                }, 1000);
            }
        }
    }
    
    stopListening() {
        console.log('🎤 Stopping voice listening');
        this.isListening = false;
        if (this.recognition) {
            this.recognition.stop();
        }
    }
    
    // UI update methods (to be implemented based on your HTML structure)
    updateCallStatus(status, type) {
        // Implementation depends on your HTML structure
        console.log(`📱 Call status: ${status} (${type})`);
    }
    
    updateVisualizer(state) {
        // Implementation depends on your HTML structure
        console.log(`🎨 Visualizer state: ${state}`);
    }
    
    addConversationItem(speaker, text) {
        const timestamp = new Date().toLocaleTimeString('hi-IN');
        const item = {
            speaker: speaker,
            text: text,
            timestamp: timestamp
        };
        
        this.conversationHistory.push(item);
        console.log(`💬 Conversation: ${speaker === 'user' ? '👨‍🌾' : '🤖'} ${text}`);
        
        // Update UI (implementation depends on your HTML structure)
    }
    
    showInterruptionIndicator() {
        console.log('🛑 Showing interruption indicator');
        // Implementation depends on your HTML structure
    }
    
    showError(message) {
        console.error(`❌ Error: ${message}`);
        alert(message);
    }
    
    // Additional utility methods
    updateUI() {
        // Update UI based on current state
    }
    
    showCallControls() {
        // Show call control buttons
    }
    
    hideCallControls() {
        // Hide call control buttons
    }
    
    showConversationLog() {
        // Show conversation log
    }
    
    showInterimTranscript(transcript) {
        console.log(`🎤 Interim: "${transcript}"`);
    }
    
    handleRecognitionError(error) {
        console.error(`🎤 Recognition error: ${error}`);
        
        // Handle different error types
        switch(error) {
            case 'network':
                this.showError('Network error. Please check your internet connection.');
                break;
            case 'not-allowed':
                this.showError('Microphone access denied. Please allow microphone access.');
                break;
            case 'no-speech':
                // Ignore no-speech errors in continuous mode
                break;
            default:
                console.warn(`Unhandled recognition error: ${error}`);
        }
        
        // Auto-restart recognition if call is active
        if (this.isCallActive && !this.isMuted) {
            setTimeout(() => {
                this.startListening();
            }, 1000);
        }
    }
    
    // Settings management
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        console.log('⚙️ Settings updated:', this.settings);
    }
    
    getCallStatistics() {
        return {
            conversationCount: this.conversationHistory.length,
            interruptionCount: this.interruptionCount,
            isActive: this.isCallActive,
            currentState: this.isSpeaking ? 'speaking' : this.isListening ? 'listening' : 'idle'
        };
    }
}

// Export for use in HTML
window.RealTimeVoiceCall = RealTimeVoiceCall;
