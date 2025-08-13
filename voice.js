// Voice Input/Output Handler for Scam Message Detector
class VoiceManager {
    constructor() {
        this.recognition = null;
        this.synthesis = null;
        this.isListening = false;
        this.voiceSettings = {
            rate: 1,
            pitch: 1,
            volume: 1,
            lang: 'en-US'
        };

        // Listen for language toggle changes
        document.addEventListener('DOMContentLoaded', () => {
            const languageSelect = document.getElementById('languageSelect');
            if (languageSelect) {
                languageSelect.addEventListener('change', (event) => {
                    this.voiceSettings.lang = event.target.value;
                    if (this.recognition) {
                        this.recognition.lang = this.voiceSettings.lang;
                    }
                });
            }
        });
        this.init();
    }

    init() {
        // Check browser support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.initSpeechRecognition();
        } else {
            console.warn('Speech recognition not supported');
        }

        if ('speechSynthesis' in window) {
            this.initSpeechSynthesis();
        } else {
            console.warn('Speech synthesis not supported');
        }
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = this.voiceSettings.lang;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceStatus('listening');
            console.log('Voice recognition started');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('Voice input:', transcript);
            this.handleVoiceInput(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.updateVoiceStatus('error', event.error);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateVoiceStatus('idle');
            console.log('Voice recognition ended');
        };
    }

    initSpeechSynthesis() {
        this.synthesis = window.speechSynthesis;
        
        // Load voices when available
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = () => {
                this.loadVoices();
            };
        }
    }

    loadVoices() {
        this.availableVoices = this.synthesis.getVoices();
    }

    startListening() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    speak(text) {
        if (!this.synthesis) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.voiceSettings.rate;
        utterance.pitch = this.voiceSettings.pitch;
        utterance.volume = this.voiceSettings.volume;
        utterance.lang = this.voiceSettings.lang;

        // Select a voice
        if (this.availableVoices && this.availableVoices.length > 0) {
            const preferredVoice = this.availableVoices.find(voice => 
                voice.lang.startsWith(this.voiceSettings.lang)
            ) || this.availableVoices[0];
            utterance.voice = preferredVoice;
        }

        this.synthesis.speak(utterance);
    }

    handleVoiceInput(transcript) {
        // Fill the input field with voice input
        const inputField = document.getElementById('message-input');
        if (inputField) {
            inputField.value = transcript;
            // Auto-analyze after voice input
            setTimeout(() => analyzeMessage(), 500);
        }
    }

    updateVoiceStatus(status, error = null) {
        const statusElement = document.getElementById('voice-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `voice-status ${status}`;
            if (error) {
                statusElement.title = error;
            }
        }
    }

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    // Settings management
    updateSettings(settings) {
        Object.assign(this.voiceSettings, settings);
        if (this.recognition) {
            this.recognition.lang = this.voiceSettings.lang;
        }
    }

    // Hindi voice support
    speakHindi(text) {
        if (!this.synthesis) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        utterance.lang = 'hi-IN'; // Hindi language

        // Find Hindi voice
        const hindiVoicePlan to add Hindi audio support to the output speech:

Information Gathered:
- The current voice.js uses the Web Speech API's SpeechSynthesisUtterance for speech output.
- The language for speech synthesis is set via this.voiceSettings.lang, currently 'en-US'.
- The speak() method selects a voice matching the language setting.
- The speak button triggers voiceManager.speak() with the results text.

Plan:
- Add a UI control (e.g., dropdown or toggle) to select the output speech language (English or Hindi).
- Extend voiceSettings.lang to support 'hi-IN' for Hindi.
- Modify speak() to use the selected language and select a matching Hindi voice if available.
- Update event listeners to handle language selection changes.
- Ensure the results text is spoken in the selected language.

Dependent Files to be edited:
- voice.js (main changes)
- index.html (to add language selection UI)

Followup steps:
- Verify the language selection UI appears and works.
- Test speech output in both English and Hindi.
- Confirm fallback behavior if Hindi voice is unavailable.


    getVoices() {
        return this.availableVoices || [];
    }
}

// Initialize voice manager
let voiceManager;

document.addEventListener('DOMContentLoaded', () => {
    voiceManager = new VoiceManager();
    
    // Add event listeners for voice controls
    const micButton = document.getElementById('mic-button');
    const speakButton = document.getElementById('speak-button');
    
    if (micButton) {
        micButton.addEventListener('click', () => voiceManager.toggleListening());
    }
    
    if (speakButton) {
        speakButton.addEventListener('click', () => {
            const resultsText = document.getElementById('results-text')?.textContent;
            if (resultsText) {
                voiceManager.speak(resultsText);
            }
        });
    }
});

// Enhanced analyze function with voice feedback
function analyzeMessage() {
    const message = document.getElementById('message-input').value;
    if (!message.trim()) {
        voiceManager.speak("Please enter a message to analyze");
        return;
    }

    // Show loading state
    document.getElementById('results').classList.add('show');
    document.getElementById('risk-circle').textContent = '⏳';
    document.getElementById('risk-level').textContent = 'Analyzing...';
    document.getElementById('risk-text').textContent = 'Please wait...';

    // Simulate API call (replace with actual API call)
    setTimeout(() => {
        const result = simulateAnalysis(message);
        displayResults(result);
        
        // Provide voice feedback
        const summary = `Analysis complete. Risk level: ${result.risk}. ${result.summary}`;
        voiceManager.speak(summary);
    }, 1500);
}

// Simulate scam detection (replace with actual API)
function simulateAnalysis(message) {
    const suspiciousWords = ['urgent', 'verify', 'suspended', 'lottery', 'prince', 'wire money', 'click link'];
    const riskScore = suspiciousWords.reduce((score, word) => 
        message.toLowerCase().includes(word) ? score + 20 : score, 0
    );
    
    let risk, summary, reasons;
    
    if (riskScore >= 60) {
        risk = 'High Risk';
        summary = 'This message shows multiple red flags typical of scam messages.';
        reasons = ['Uses urgency tactics', 'Requests personal information', 'Promises unrealistic rewards'];
    } else if (riskScore >= 30) {
        risk = 'Medium Risk';
        summary = 'This message has some suspicious elements that warrant caution.';
        reasons = ['Contains unusual requests', 'May be attempting to create urgency'];
    } else {
        risk = 'Low Risk';
        summary = 'This message appears to be legitimate, but always verify with official sources.';
        reasons = ['No obvious scam indicators detected'];
    }
    
    return { risk, score: Math.min(riskScore, 100), summary, reasons };
}

function displayResults(result) {
    const riskCircle = document.getElementById('risk-circle');
    const riskLevel = document.getElementById('risk-level');
    const riskText = document.getElementById('risk-text');
    const reasonsList = document.getElementById('reasons-list');
    
    // Update risk indicator
    riskCircle.textContent = result.score;
    riskLevel.textContent = result.risk;
    riskText.textContent = result.summary;
    
    // Set color based on risk
    riskCircle.className = `risk-circle risk-${result.risk.toLowerCase().replace(' ', '')}`;
    
    // Update reasons
    reasonsList.innerHTML = '';
    result.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.textContent = reason;
        reasonsList.appendChild(li);
    });
    
    // Update results text for voice output
    const resultsText = `${result.risk} detected. ${result.summary}. ${result.reasons.join('. ')}`;
    if (!document.getElementById('results-text')) {
        const div = document.createElement('div');
        div.id = 'results-text';
        div.style.display = 'none';
        div.textContent = resultsText;
        document.body.appendChild(div);
    } else {
        document.getElementById('results-text').textContent = resultsText;
    }
}

// Load example messages
function loadExample(element) {
    document.getElementById('message-input').value = element.textContent.trim();
    analyzeMessage();
}
