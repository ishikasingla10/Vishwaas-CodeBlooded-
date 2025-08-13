import re
import string
from typing import Dict, List, Tuple
import math

class ScamDetector:
    def __init__(self):
        # Common scam keywords and patterns
        self.scam_keywords = {
            'urgent': 3.0,
            'immediate': 2.5,
            'act now': 3.5,
            'limited time': 2.8,
            'winner': 3.2,
            'congratulations': 2.7,
            'lottery': 3.5,
            'inheritance': 3.0,
            'prince': 2.8,
            'million': 2.5,
            'urgent response': 3.5,
            'verify account': 3.0,
            'suspended': 2.8,
            'click link': 3.2,
            'wire transfer': 3.0,
            'gift card': 2.8,
            'bitcoin': 2.5,
            'cryptocurrency': 2.3,
            'urgent wire': 3.8,
            'confidential': 2.5,
            'secret': 2.3,
            'do not tell': 3.0,
            'western union': 3.5,
            'moneygram': 3.5,
            'paypal': 2.0,
            'account verification': 3.2,
            'security alert': 3.0,
            'suspended account': 3.3,
            'unauthorized access': 2.8,
            'confirm identity': 3.0,
            'validate account': 3.0
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b[A-Z]{2,}\b',  # ALL CAPS words
            r'[!]{2,}',  # Multiple exclamation marks
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Dollar amounts
            r'\b\d+\s*(?:million|billion|thousand)\b',  # Large amounts
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
            r'\b(?:urgent|immediate|asap)\b.*?\b(?:respond|reply|click)\b',  # Urgent action
            r'\b(?:click|visit).*\b(?:link|url)\b',  # Click requests
            r'\b(?:wire|send|transfer).*\b(?:money|funds)\b',  # Money requests
        ]
        
        # Legitimate patterns (reduce scam score)
        self.legitimate_patterns = [
            r'\bthank you\b',
            r'\bregards\b',
            r'\bbest regards\b',
            r'\bsincerely\b',
            r'\bhello\b',
            r'\bhi\b',
            r'\bhow are you\b',
            r'\bgood morning\b',
            r'\bgood afternoon\b',
            r'\bgood evening\b',
        ]
    
    def calculate_scam_score(self, text: str) -> Dict[str, any]:
        """Calculate scam probability score for given text"""
        text_lower = text.lower()
        score = 0.0
        reasons = []
        
        # Check for scam keywords
        for keyword, weight in self.scam_keywords.items():
            if keyword in text_lower:
                score += weight
                reasons.append(f"Contains suspicious keyword: '{keyword}'")
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += len(matches) * 2.0
                reasons.append(f"Matches suspicious pattern: {pattern}")
        
        # Reduce score for legitimate patterns
        for pattern in self.legitimate_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                score -= len(matches) * 0.5
        
        # Check text characteristics
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += exclamation_count * 0.5
            reasons.append(f"Excessive exclamation marks ({exclamation_count})")
        
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            score += caps_ratio * 5
            reasons.append(f"High percentage of capital letters ({caps_ratio:.1%})")
        
        # Check for urgency indicators
        urgency_words = ['urgent', 'immediate', 'asap', 'hurry', 'quick']
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        if urgency_count > 0:
            score += urgency_count * 1.5
            reasons.append(f"Contains {urgency_count} urgency indicators")
        
        # Normalize score to 0-100
        max_possible_score = 50.0
        normalized_score = min((score / max_possible_score) * 100, 100)
        
        # Determine risk level
        if normalized_score >= 70:
            risk_level = "HIGH RISK"
            color = "red"
        elif normalized_score >= 40:
            risk_level = "MEDIUM RISK"
            color = "orange"
        elif normalized_score >= 20:
            risk_level = "LOW RISK"
            color = "yellow"
        else:
            risk_level = "SAFE"
            color = "green"
        
        return {
            "score": round(normalized_score, 1),
            "risk_level": risk_level,
            "color": color,
            "reasons": reasons[:5],  # Top 5 reasons
            "is_scam": normalized_score >= 40
        }

    def analyze_text(self, text: str) -> Dict[str, any]:
        """Main method to analyze text for scam detection"""
        if not text.strip():
            return {
                "score": 0,
                "risk_level": "NO TEXT",
                "color": "gray",
                "reasons": ["No text provided"],
                "is_scam": False
            }
        
        return self.calculate_scam_score(text)
