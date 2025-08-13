
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


@app.route('/')
def index():
    return render_template_string