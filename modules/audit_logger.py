"""
FAFO Immutable Audit Logger
Logs system-wide administrative, forensic, and user actions to DB and a text audit file.
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st
from config.settings import LOGS_DIR, ENABLE_AUDIT_LOGGING
from modules import incident_manager

# Set up audit log file
AUDIT_LOG_FILE = LOGS_DIR / "audit_trail.log"

def log_action(
    user: Optional[Dict[str, Any]],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Log an event to the database audit table and append to the text-based audit trail log.
    Ensures strict documentation of user access, data edits, and forensic checks.
    """
    if not ENABLE_AUDIT_LOGGING:
        return False
        
    user_id = user.get("id") if user else None
    username = user.get("username", "system_anonymous") if user else "system_anonymous"
    role = user.get("role", "system") if user else "system"
    if isinstance(role, str):
        role_name = role
    elif hasattr(role, "value"):
        role_name = role.value
    else:
        role_name = str(role)
        
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 1. Database log
    try:
        incident_manager.log_audit(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )
    except Exception as e:
        # Fallback to standard logging if DB fails, don't crash
        logging.error(f"Failed to write audit log to database: {str(e)}")
        
    # 2. Text log
    log_line = (
        f"[{timestamp_str}] USER: {username} (ID: {user_id or 'N/A'}, ROLE: {role_name}) | "
        f"ACTION: {action} | "
        f"RESOURCE: {resource_type or 'None'}:{resource_id or 'None'} | "
        f"DETAILS: {details or 'None'} | "
        f"IP: {ip_address or '127.0.0.1'}\n"
    )
    
    try:
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(log_line)
        return True
    except Exception as e:
        logging.error(f"Failed to append to audit trail log: {str(e)}")
        return False

def get_streamlit_ip() -> str:
    """Helper to extract IP address or header elements in Streamlit context."""
    # In some Streamlit versions, headers can be retrieved from session context.
    # Otherwise, default to standard local loopback for local deployments.
    try:
        # Try to resolve remote IP via Streamlit headers (in production standard setups)
        ctx = st.runtime.scriptrunner.script_run_context.get_script_run_context()
        if ctx:
            # Under some environments, this has request details
            headers = st.context.headers
            if "X-Forwarded-For" in headers:
                return headers["X-Forwarded-For"].split(",")[0].strip()
            if "Host" in headers:
                return headers["Host"]
    except Exception:
        pass
    return "127.0.0.1"
