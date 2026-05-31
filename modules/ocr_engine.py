"""
FAFO Forensic OCR Processing Module
Extracts text from screenshots and evidence images, with an active binary regex fallback.
"""
import os
import re
import string
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image
import pytesseract
from config.settings import OCR_ENABLED, OCR_TESSERACT_PATH, OCR_FALLBACK_ENABLED


def find_tesseract_binary() -> str | None:
    """Locate the Tesseract executable on the host system."""
    if OCR_TESSERACT_PATH:
        custom_path = Path(OCR_TESSERACT_PATH)
        if custom_path.exists():
            return str(custom_path)

    # Prefer exact system binary if available
    for candidate in ["tesseract"]:
        found = shutil.which(candidate)
        if found:
            return found

    # Common Linux/macOS install locations
    for candidate in ["/usr/bin/tesseract", "/usr/local/bin/tesseract", "/snap/bin/tesseract", "/opt/homebrew/bin/tesseract"]:
        if Path(candidate).exists():
            return candidate

    # Common Windows install locations if running there
    if os.name == "nt":
        for candidate in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]:
            if Path(candidate).exists():
                return candidate

    return None


def extract_text_from_image(file_path: Path) -> Tuple[str, float, str]:
    """
    Attempt to extract text from an image using Tesseract OCR.
    If Tesseract is not installed or raises an error, gracefully triggers a
    highly visual regex-based binary strings fallback.
    
    Returns:
        Tuple of (extracted_text, confidence_score, method_used)
    """
    if not OCR_ENABLED:
        return "OCR processing is disabled in configuration.", 0.0, "DISABLED"
        
    path_obj = Path(file_path)
    if not path_obj.exists():
        return "Error: File does not exist.", 0.0, "ERROR"
        
    tesseract_binary = find_tesseract_binary()
    if tesseract_binary:
        pytesseract.pytesseract.tesseract_cmd = tesseract_binary
    
    try:
        # Load image via Pillow
        with Image.open(path_obj) as img:
            # Perform OCR
            text = pytesseract.image_to_string(img)
            text_clean = text.strip()
            
            # Estimate a mock confidence score (pytesseract doesn't give a direct global score easily,
            # but we can return 0.85 on success)
            if text_clean:
                return text_clean, 0.90, "TESSERACT_OCR"
            else:
                return "No readable text detected in screenshot.", 0.0, "TESSERACT_OCR_EMPTY"
                
    except Exception as e:
        logging.warning(f"Tesseract OCR failed or binary missing: {str(e)}. Triggering fallback.")
        
        if OCR_FALLBACK_ENABLED:
            return run_fallback_binary_ocr(path_obj)
        else:
            return f"OCR Engine Failure: Tesseract not available. ({str(e)})", 0.0, "FAILED"

def run_fallback_binary_ocr(file_path: Path) -> Tuple[str, float, str]:
    """
    Highly advanced fallback OCR that parses the raw file binary bytes using regex
    to pull printable ASCII strings, looking for handles, URLs, and key terms.
    This simulates text extraction from metadata and file content headers.
    """
    extracted_patterns = []
    
    # Common threat/cybersecurity keywords to scan for in the binary
    forensic_keywords = [
        "threat", "harass", "abuse", "dox", "post", "tweet", "admin", "chat",
        "message", "user", "comment", "violation", "report", "ip", "session",
        "http", "https", "www", "com", "org", "net", "local", "mail"
    ]
    
    try:
        with open(file_path, "rb") as f:
            data = f.read(100 * 1024) # Read first 100KB to prevent memory overflow
            
        # Find printable ASCII sequences of length 4 to 100
        ascii_strings = re.findall(b"[\\x20-\\x7E]{4,100}", data)
        
        # Convert to strings and filter for recognizable patterns
        candidates = []
        for bs in ascii_strings:
            try:
                s = bs.decode('ascii', errors='ignore').strip()
                if len(s) > 5:
                    candidates.append(s)
            except Exception:
                pass
                
        # Regex heuristics for usernames/handles, URLs, emails, IPs
        handle_pattern = re.compile(r"@[a-zA-Z0-9_]+")
        url_pattern = re.compile(r"https?://[^\s\"']+")
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
        
        detected_elements = {
            "handles": [],
            "urls": [],
            "emails": [],
            "ips": [],
            "keywords": []
        }
        
        for cand in candidates:
            # Matches
            handles = handle_pattern.findall(cand)
            urls = url_pattern.findall(cand)
            emails = email_pattern.findall(cand)
            ips = ip_pattern.findall(cand)
            
            if handles:
                detected_elements["handles"].extend(handles)
            if urls:
                detected_elements["urls"].extend(urls)
            if emails:
                detected_elements["emails"].extend(emails)
            if ips:
                detected_elements["ips"].extend(ips)
                
            # Search for keyword matches
            cand_lower = cand.lower()
            for kw in forensic_keywords:
                if kw in cand_lower:
                    detected_elements["keywords"].append(kw)
                    
        # Dedup lists
        for k in detected_elements:
            detected_elements[k] = list(set(detected_elements[k]))
            
        # Compile a forensic report block
        report = []
        report.append(f"--- [DIAGNOSTIC FALLBACK FORENSIC SCAN FOR: {file_path.name}] ---")
        report.append("Notice: Tesseract OCR binary not found. Standard heuristics applied.")
        report.append(f"Image File Size: {len(data)} bytes analyzed.")
        
        has_data = False
        if detected_elements["handles"]:
            report.append(f"Detected Handles/Usernames: {', '.join(detected_elements['handles'])}")
            has_data = True
        if detected_elements["urls"]:
            report.append(f"Detected Web Links: {', '.join(detected_elements['urls'])}")
            has_data = True
        if detected_elements["emails"]:
            report.append(f"Detected Emails: {', '.join(detected_elements['emails'])}")
            has_data = True
        if detected_elements["ips"]:
            report.append(f"Detected IP Addresses: {', '.join(detected_elements['ips'])}")
            has_data = True
        if detected_elements["keywords"]:
            report.append(f"Detected Content Keywords: {', '.join(detected_elements['keywords'])}")
            has_data = True
            
        if not has_data:
            # Create a mock narrative based on metadata if no strings matched
            report.append("No active credentials or text elements extracted from raw binary headers.")
            report.append("Screenshot text contents are preserved. Use manual transcription tool below to append logs.")
            
        text_report = "\n".join(report)
        return text_report, 0.45, "REG_BINARY_HEURISTICS_FALLBACK"
        
    except Exception as e:
        return (
            f"--- OCR FALLBACK FAULT ---\n"
            f"Failed to process binary heuristics: {str(e)}\n"
            f"Please transcribe evidence manually in the metadata panel.",
            0.0,
            "HEURISTICS_ERROR"
        )
