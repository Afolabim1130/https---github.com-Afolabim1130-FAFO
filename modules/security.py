"""
FAFO Security Layer
Provides password hashing, filename sanitization, mime-type checking, and path traversal protections.
"""
import os
import re
import bcrypt
from pathlib import Path
from typing import Optional
from config.settings import BCRYPT_ROUNDS, ALLOWED_MIME_TYPES

def hash_password(password: str) -> str:
    """Generate a secure bcrypt hash of a password."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and injection attacks.
    Keeps only alphanumeric, dot, dash, and underscore.
    """
    if not filename:
        return "unnamed_file"
    
    # Strip paths if any
    base_name = os.path.basename(filename)
    
    # Remove leading dots or spaces
    base_name = base_name.lstrip('. ')
    
    # Split filename and extension
    name, ext = os.path.splitext(base_name)
    
    # Sanitize name
    name_clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    # Ensure extension is simple alpha
    ext_clean = re.sub(r'[^a-zA-Z0-9]', '', ext.lower())
    
    if not name_clean:
        name_clean = "evidence"
        
    return f"{name_clean}.{ext_clean}" if ext_clean else name_clean

def validate_mime_type(mime_type: str) -> bool:
    """Verify that the uploaded file MIME type is explicitly permitted."""
    if not mime_type:
        return False
    return mime_type.lower() in ALLOWED_MIME_TYPES

def prevent_path_traversal(base_path: Path, target_path: Path) -> bool:
    """
    Ensure target_path resolves strictly under base_path.
    Prevents path traversal vulnerabilities.
    """
    try:
        resolved_base = Path(base_path).resolve()
        resolved_target = Path(target_path).resolve()
        return resolved_base in resolved_target.parents or resolved_base == resolved_target
    except Exception:
        return False

def is_safe_url(url: str) -> bool:
    """Validate that input URLs use standard secure protocols (HTTP/HTTPS) only."""
    if not url:
        return False
    # Regex to check standard HTTP/HTTPS schemes
    pattern = re.compile(
        r'^https?://'  # scheme
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(pattern.match(url))
