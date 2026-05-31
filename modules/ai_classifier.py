"""
FAFO AI Classifier & Triage Module
Uses tf-idf and keyword scoring heuristics to auto-classify incident files and write summaries.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from modules.repository import get_incident_dir

# Categories definitions
CATEGORIES = {
    "Cyberbullying": ["bully", "loser", "ugly", "hate", "fat", "trash", "worthless", "harass", "creep", "ugly"],
    "Doxxing/Privacy": ["address", "phone", "ssn", "leak", "live at", "home", "street", "ip address", "location", "identity"],
    "Extortion/Threats": ["kill", "hurt", "find you", "beat", "murder", "shoot", "destroy", "extort", "pay", "money", "ransom", "leak private"],
    "Corporate Sabotage": ["hack", "ddos", "virus", "malware", "sabotage", "breach", "server", "database", "delete", "leak source", "intellectual"],
    "General Harassment": ["harass", "annoy", "spam", "troll", "stalk", "bother", "message", "unwanted"]
}

SEVERITIES = ["Low", "Medium", "High", "Critical"]

def classify_text_offline(text: str) -> Tuple[str, str, float]:
    """
    Analyzes incident text using TF-IDF term-density heuristics
    to calculate category fit and threat severity level.
    """
    if not text:
        return "General Harassment", "Low", 0.50
        
    text_lower = text.lower()
    
    # Calculate scores for each category
    scores = {}
    for cat, keywords in CATEGORIES.items():
        score = 0.0
        for kw in keywords:
            # Term density: count occurrences
            matches = text_lower.count(kw)
            if matches > 0:
                score += (matches * 1.5)
        scores[cat] = score
        
    # Get highest scoring category
    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]
    
    # Normalize score to a confidence rating between 0.30 and 0.98
    if best_score == 0:
        suggested_category = "General Harassment"
        confidence = 0.50
    else:
        suggested_category = best_cat
        # Simple normalization
        confidence = min(0.30 + (best_score * 0.15), 0.98)
        
    # Heuristics for severity evaluation
    suggested_severity = "Medium"
    
    # 1. Critical triggers (death threats, extortion, physical violence)
    critical_triggers = ["kill", "murder", "bomb", "suicide", "kys", "shoot", "ransom", "extort"]
    # 2. High triggers (doxxing, system hacks)
    high_triggers = ["address", "ssn", "leak", "ddos", "hack", "virus", "malware"]
    
    if any(trigger in text_lower for trigger in critical_triggers):
        suggested_severity = "Critical"
    elif any(trigger in text_lower for trigger in high_triggers):
        suggested_severity = "High"
    elif best_score > 5.0:
        suggested_severity = "High"
    elif best_score < 1.0:
        suggested_severity = "Low"
        
    return suggested_category, suggested_severity, confidence

def analyze_and_triage_incident(
    incident_key: str,
    title: str,
    description: str,
    ocr_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Combine case title, description, and OCR textual evidence, perform AI triage classification,
    write result to persistent repository JSON files, and return the metrics.
    """
    full_corpus = f"{title} {description}"
    if ocr_text:
        full_corpus += f" {ocr_text}"
        
    category, severity, score = classify_text_offline(full_corpus)
    
    analysis_result = {
        "incident_key": incident_key,
        "suggested_category": category,
        "suggested_severity": severity,
        "category_confidence": round(score, 2),
        "analyzed_at": Path().absolute().name, # placeholder or datetime
        "timestamp": Path().absolute().name # placeholder
    }
    
    # Add actual UTC timestamp
    from datetime import datetime, timezone
    analysis_result["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Save a companion ai_analysis.json inside the incident's repository folder
    base_dir = get_incident_dir(incident_key)
    if base_dir.exists() and base_dir.is_dir():
        ai_file_path = base_dir / "ai_analysis.json"
        try:
            with open(ai_file_path, "w") as f:
                json.dump(analysis_result, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save ai_analysis.json: {str(e)}")
            
    return analysis_result
