from flask import Flask, request, jsonify, render_template_string
import os
import re

app = Flask(__name__)

class UnifiedScamDetector:
    def __init__(self):
        self.scam_keywords = {
            'urgent': 3.0, 'immediate': 2.5, 'act now': 3.5, 'limited time': 2.8,
            'winner': 3.2, 'congratulations': 2.7, 'lottery': 3.5, 'inheritance': 3.0,
            'prince': 2.8, 'million': 2.5, 'verify account': 3.0, 'suspended': 2.8,
            'click link': 3.2, 'wire transfer': 3.0, 'gift card': 2.8, 'bitcoin': 2.5,
            'cryptocurrency': 2.3, 'confidential': 2.5, 'secret': 2.3, 'do not tell': 3.0,
            'western union': 3.5, 'moneygram': 3.5, 'account verification': 3.2,
            'security alert': 3.0, 'unauthorized access': 2.8, 'confirm identity': 3.0
        }
        
        self.suspicious_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            r'\b[A-Z]{2,}\b',
            r'[!]{2,}',
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\b\d+\s*(?:million|billion|thousand)\b',
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+',
            r'\b(?:urgent|immediate|asap)\b.*?\b(?:respond|reply|click)\b',
            r'\b(?:click|visit).*\b(?:link|url)\b',
            r'\b(?:wire|send|transfer).*\b(?:money|funds)\b',
        ]
    
    def analyze_text(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "score": 0,
                "risk_level": "NO TEXT",
                "color": "gray",
                "reasons": ["No text provided"],
                "is_scam": False,
                "summary": "Please provide a message to analyze."
            }
        
        text_lower = text.lower()
        score = 0.0
        reasons = []
        
        for keyword, weight in self.scam_keywords.items():
            if keyword in text_lower:
                score += weight
                reasons.append(f"Suspicious phrase: '{keyword}'")
        
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += len(matches) * 2.0
                reasons.append(f"Matches suspicious pattern")
        
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += exclamation_count * 0.5
            reasons.append(f"Excessive exclamation marks ({exclamation_count})")
        
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            score += caps_ratio * 5
            reasons.append(f"High percentage of capital letters")
        
        normalized_score = min((score / 50.0) * 100, 100)
        
        if normalized_score >= 70:
            risk_level = "HIGH RISK"
            color = "red"
            summary = "Multiple red flags detected - likely a scam"
        elif normalized_score >= 40:
            risk_level = "MEDIUM RISK"
            color = "orange"
            summary = "Suspicious elements present - proceed with caution"
        elif normalized_score >= 20:
            risk_level = "LOW RISK"
            color = "yellow"
            summary = "Some concerns but appears mostly legitimate"
        else:
            risk_level = "SAFE"
            color = "green"
            summary = "No obvious scam indicators detected"
        
        return {
            "score": round(normalized_score, 1),
            "risk_level": risk_level,
            "color": color,
            "reasons": reasons[:5],
            "is_scam": normalized_score >= 40,
            "summary": summary
        }

detector = UnifiedScamDetector()

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Scam Detector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.2em; }
        .content { padding: 40px; }
        .input-section { margin-bottom: 30px; }
        .input-section label { display: block; margin-bottom: 10px; font-weight: 600; color: #333; }
        .text-input { width: 100%; min-height: 120px; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; resize: vertical; transition: border-color 0.3s; }
        .text-input:focus { outline: none; border-color: #667eea; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .results { margin-top: 30px; padding: 30px; border-radius: 15px; background: #f8f9fa; display: none; }
        .results.show { display: block; animation: fadeIn 0.5s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .risk-indicator { text-align: center; margin-bottom: 20px; }
        .risk-circle { display: inline-block; width: 80px; height: 80px; border-radius: 50%; line-height: 80px; font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px; }
        .risk-red { background: #e74c3c; } .risk-orange { background: #f39c12; } .risk-yellow { background: #f1c40f; } .risk-green { background: #27ae60; }
        .risk-level { font-size: 1.5em; font-weight: bold; margin-bottom: 10px; }
        .risk-text { font-size: 1.1em; color: #555; margin-bottom: 20px; }
        .reasons { background: white; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .reasons ul { list-style: none; }
        .reasons li { padding: 8px 0; border-bottom: 1px solid #eee; color: #555; }
        .voice-controls { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px; }
        .voice-status { padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center; font-weight: bold; }
        .voice-status.listening { background: #d4edda; color: #155724; }
        .voice-status.error { background: #f8d7da; color: #721c24; }
        .voice-status.idle { background: #e2e3e5; color: #383d41; }
        .voice-status.unsupported { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Unified Scam Detector</h1>
            <p>Advanced AI-powered scam detection with voice capabilities</p>
        </div>
        
        <div class="content">
            <div class="input-section">
                <label for="message-input">Paste your suspicious message here:</label>
                <textarea id="message-input" class="text-input" placeholder="Enter suspicious email, text message, or social media post..."></textarea>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="analyzeMessage()">🔍 Analyze Message</button>
                <button class="btn" onclick="startVoiceInput()" id="mic-btn">🎤 Voice Input</button>
                <button class="btn" onclick="speakResults()" id="speak-btn" disabled>🔊 Speak Results</button>
            </div>
            
            <div class="voice-controls">
                <div id="voice-status" class="voice-status idle">Ready for voice input</div>
            </div>
            
            <div id="results" class="results">
                <div class="risk-indicator">
                    <div id="risk-circle" class="risk-circle risk-green">0</div>
                    <div id="risk-level" class="risk-level">SAFE</div>
                    <div id="risk-text" class="risk-text">No analysis performed yet</div>
                </div>
                
                <div class="reasons">
                    <h4>🚨 Key Findings:</h4>
                    <ul id="reasons-list"></ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let recognition = null;
        let isListening = false;

        // Initialize voice recognition
        function initVoiceRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                recognition.onstart = () => {
                    isListening = true;
                    document.getElementById('voice-status').textContent = 'Listening...';
                    document.getElementById('voice-status').className = 'voice-status listening';
                    document.getElementById('mic-btn').textContent = '⏹️ Stop';
                };
                
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('message-input').value = transcript;
                    analyzeMessage();
                };
                
                recognition.onerror = (event) => {
                    document.getElementById('voice-status').textContent = 'Error: ' + event.error;
                    document.getElementById('voice-status').className = 'voice-status error';
                    console.error('Voice recognition error:', event.error);
                };
                
                recognition.onend = () => {
                    isListening = false;
                    document.getElementById('voice-status').textContent = 'Ready';
                    document.getElementById('voice-status').className = 'voice-status idle';
                    document.getElementById('mic-btn').textContent = '🎤 Voice Input';
                };
            } else {
                document.getElementById('voice-status').textContent = 'Voice recognition not supported in this browser';
                document.getElementById('voice-status').className = 'voice-status unsupported';
                document.getElementById('mic-btn').disabled = true;
            }
        }

        function startVoiceInput() {
            if (!recognition) {
                initVoiceRecognition();
            }
            
            if (recognition) {
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            }
        }

        async function analyzeMessage() {
            const message = document.getElementById('message-input').value;
            
            if (!message.trim()) {
                alert('Please enter a message to analyze');
                return;
            }
            
            // Show loading state
            document.getElementById('results').classList.add('show');
            document.getElementById('risk-circle').textContent = '⏳';
            document.getElementById('risk-level').textContent = 'Analyzing...';
            document.getElementById('risk-text').textContent = 'Please wait...';
            document.getElementById('reasons-list').innerHTML = '';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: message })
                });
                
                const result = await response.json();
                
                // Update UI with results
                document.getElementById('risk-circle').textContent = result.score;
                document.getElementById('risk-circle').className = `risk-circle risk-${result.color}`;
                document.getElementById('risk-level').textContent = result.risk_level;
                document.getElementById('risk-text').textContent = result.summary;
                
                // Update reasons
                const reasonsList = document.getElementById('reasons-list');
                reasonsList.innerHTML = '';
                result.reasons.forEach(reason => {
                    const li = document.createElement('li');
                    li.textContent = reason;
                    reasonsList.appendChild(li);
                });
                
                // Enable speak button
                document.getElementById('speak-btn').disabled = false;
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error analyzing message. Please try again.');
            }
        }

        function speakResults() {
            const riskLevel = document.getElementById('risk-level').textContent;
            const riskText = document.getElementById('risk-text').textContent;
            const reasons = Array.from(document.getElementById('reasons-list').children)
                .map(li => li.textContent).join('. ');
            
            const textToSpeak = `Analysis complete. Risk level: ${riskLevel}. ${riskText}. ${reasons}`;
            
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                window.speechSynthesis.speak(utterance);
            } else {
                alert('Speech synthesis not supported in your browser');
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initVoiceRecognition();
        });
    </script>
</body>
</html>
    ''')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text', '')
        result = detector.analyze_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'unified-scam-detector',
        'features': ['advanced-analysis', 'voice-input', 'voice-output', 'real-time-detection']
    })

if __name__ == '__main__':
    print("🚀 Starting Unified Scam Detector...")
    print("📱 Open http://localhost:5000 in your browser")
    print("🎤 Use voice input with the microphone button")
    print("🔊 Click 'Speak Results' to hear the analysis")
    print("🔍 Paste suspicious messages for instant analysis")
    app.run(debug=True, host='0.0.0.0', port=5000)
