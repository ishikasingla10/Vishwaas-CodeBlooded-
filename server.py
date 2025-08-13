from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os

app = Flask(__name__)

class ScamDetector:
    def analyze(self, message):
        if not message or not message.strip():
            return {
                'risk': 'No Message',
                'score': 0,
                'summary': 'Please provide a message to analyze.',
                'reasons': ['No message provided']
            }
            
        suspicious_words = ['urgent', 'verify', 'suspended', 'lottery', 'prince', 'wire money', 'click link', 'congratulations', 'winner', 'prize', 'million', 'free', 'limited time', 'act now']
        risk_score = 0
        
        message_lower = message.lower()
        detected_reasons = []
        
        for word in suspicious_words:
            if word in message_lower:
                risk_score += 15
                detected_reasons.append(f"Contains suspicious phrase: '{word}'")
        
        # Additional pattern detection
        if 'http' in message_lower or 'www.' in message_lower:
            risk_score += 20
            detected_reasons.append("Contains suspicious links")
            
        if any(char.isdigit() for char in message) and 'account' in message_lower:
            risk_score += 15
            detected_reasons.append("Requests account information")
            
        if 'money' in message_lower and ('send' in message_lower or 'wire' in message_lower):
            risk_score += 25
            detected_reasons.append("Requests money transfer")
        
        risk_score = min(risk_score, 100)
        
        if risk_score >= 60:
            return {
                'risk': 'High Risk',
                'score': risk_score,
                'summary': 'This message shows multiple red flags typical of scam messages.',
                'reasons': detected_reasons if detected_reasons else ['Multiple suspicious indicators detected']
            }
        elif risk_score >= 30:
            return {
                'risk': 'Medium Risk',
                'score': risk_score,
                'summary': 'This message has some suspicious elements that warrant caution.',
                'reasons': detected_reasons if detected_reasons else ['Contains potentially suspicious content']
            }
        else:
            return {
                'risk': 'Low Risk',
                'score': risk_score,
                'summary': 'This message appears to be legitimate, but always verify with official sources.',
                'reasons': detected_reasons if detected_reasons else ['No obvious scam indicators detected']
            }

detector = ScamDetector()

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html file not found", 404

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/voice.js')
def voice_js():
    return send_from_directory('.', 'voice.js')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        message = data.get('message', '')
        result = detector.analyze(message)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'risk': 'Error',
            'score': 0,
            'summary': f'Analysis error: {str(e)}',
            'reasons': ['Unable to analyze message']
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Vishwas - Voice-enabled scam detector is running'})

if __name__ == '__main__':
    print("🚀 Starting Vishwas - Voice-Enabled Scam Detector...")
    print("📱 Open http://localhost:5000 in your browser")
    print("🎤 Use voice input to speak suspicious messages")
    print("🔊 Click 'Speak Results' to hear the analysis")
    app.run(debug=True, host='0.0.0.0', port=5000)
