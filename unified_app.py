from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
import re
from typing import Dict, List, Any

app = Flask(__name__)

class UnifiedScamDetector:
    def __init__(self):
        # Comprehensive scam keywords with weights
        self.scam_keywords = {
            'urgent': 3.0, 'immediate': 2.5, 'act now': 3.5, 'limited time': 2.8,
            'winner': 3.2, 'congratulations': 2.7, 'lottery': 3.5, 'inheritance': 3.0,
            'prince': 2.8, 'million': 2.5, 'verify account': 3.0, 'suspended': 2.8,
            'click link': 3.2, 'wire transfer': 3.0, 'gift card': 2.8, 'bitcoin': 2.5,
            'cryptocurrency': 2.3, 'confidential': 2.5, 'secret': 2.3, 'do not tell': 3.0,
            'western union': 3.5, 'moneygram': 3.5, 'account verification': 3.2,
            'security alert': 3.0, 'unauthorized access': 2.8, 'confirm identity': 3.0
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\\b\\d{3}-\\d{2}-\\d{4}\\b',  # SSN
            r'\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b',  # Credit card
            r'\\b[A-Z]{2,}\\b',  # ALL CAPS
            r'[!]{2,}',  # Multiple exclamations
            r'\\$\\d+(?:,\\d{3})*(?:\\.\\d{2})?',  # Dollar amounts
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+',  # URLs
        ]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for scam indicators"""
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
        
        # Check scam keywords
        for keyword, weight in self.scam_keywords.items():
            if keyword in text_lower:
                score += weight
                reasons.append(f"Suspicious phrase: '{keyword}'")
        
        # Check patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += len(matches) * 2.0
                reasons.append(f"Matches suspicious pattern")
        
        # Text characteristics
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += exclamation_count * 0.5
            reasons.append(f"Excessive exclamation marks ({exclamation_count})")
        
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            score += caps_ratio * 5
            reasons.append(f"High percentage of capital letters")
        
        # Normalize score
        normalized_score = min((score / 50.0) * 100, 100)
        
        # Determine risk level
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
        text = data.get('text', '')
        result = detector.analyze_text(text)
        print("Analysis Result:", result)  # Added logging for verification
        return jsonify(result)
    except Exception as e:
        print("Error during analysis:", e)  # Added error logging
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
