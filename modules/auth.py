"""
FAFO Session & Authentication Manager
Handles secure logins, password verification, session timeout triggers, and roles.
"""
from datetime import datetime, timezone, timedelta
from typing import Tuple
import streamlit as st
from config.settings import SESSION_TIMEOUT_MINUTES
from config.roles import Role
from modules import incident_manager
from modules import security
from modules import audit_logger

def authenticate_user(username: str, password: str, selected_role: str) -> Tuple[bool, str]:
    """
    Checks credentials, verifies password hashes using bcrypt,
    validates the selected role area, and updates the active session state if valid.
    """
    user = incident_manager.get_user_by_username(username)
    if not user:
        return False, "Authentication Fault: Invalid username or password."
        
    # Verify is active
    if not user.get("is_active", True):
        return False, "Access Denied: This account is disabled."
        
    # Verify password hash
    if not security.verify_password(password, user["password_hash"]):
        return False, "Authentication Fault: Invalid username or password."

    db_role = user.get("role", "").lower()
    if selected_role.lower() != db_role:
        return False, f"Role mismatch: account is configured as '{db_role}', not '{selected_role}'."

    try:
        role_enum = Role(db_role)
    except Exception:
        return False, "Authentication Fault: Invalid role configuration for this account."
            
    st.session_state["logged_in"] = True
    st.session_state["user"] = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": role_enum
    }
    
    now = datetime.now(timezone.utc)
    st.session_state["login_time"] = now
    st.session_state["last_activity"] = now
    
    # Log to audit trail
    audit_logger.log_action(
        user=st.session_state["user"],
        action="login",
        details=f"User logged in successfully as {role_enum.value}",
        ip_address=audit_logger.get_streamlit_ip()
    )
    return True, "Authorized: Access granted. Handshake successful."

def init_session_state():
    """Initializes standard security session parameters on launch."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = None
    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = None

def check_session_timeout() -> bool:
    """
    Check if the user's session has timed out due to inactivity.
    If timed out, perform automatic logout and prompt for re-auth.
    """
    if not st.session_state.get("logged_in", False):
        return False
        
    last_act = st.session_state.get("last_activity")
    if not last_act:
        return False
        
    now = datetime.now(timezone.utc)
    inactivity_duration = now - last_act
    
    if inactivity_duration > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        # Force logout due to security policy timeout
        user = st.session_state.get("user")
        
        # Log to audit trail before clearing session
        audit_logger.log_action(
            user=user,
            action="session_timeout",
            details=f"Inactivity timeout triggered after {SESSION_TIMEOUT_MINUTES} mins",
            ip_address=audit_logger.get_streamlit_ip()
        )
        
        logout(quiet=True)
        st.warning(f"Session expired due to {SESSION_TIMEOUT_MINUTES} minutes of inactivity. Please log in again.")
        st.rerun()
        return True
        
    # Update last activity timestamp to prevent premature timeout
    st.session_state["last_activity"] = now
    return False

def logout(quiet: bool = False):
    """Securely log out the current user, log the audit record, and clear the session."""
    user = st.session_state.get("user")
    
    if not quiet and user:
        audit_logger.log_action(
            user=user,
            action="logout",
            details="User logged out successfully",
            ip_address=audit_logger.get_streamlit_ip()
        )
        
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["login_time"] = None
    st.session_state["last_activity"] = None

def render_login_panel():
    """Render the high-fidelity cyber-terminal login UI."""
    # Custom HTML header for login panel
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 class='neon-text-cyan' style='font-size: 3rem; margin-bottom: 5px; font-weight: 800;'>F A F O</h1>
            <p style='color: #7289da; letter-spacing: 0.15em; font-family: "JetBrains Mono", monospace; font-size: 0.95rem; text-transform: uppercase;'>
                Facts • Accountability • Forensics • Observation
            </p>
            <div style='border-top: 1px solid #1a3c6e; max-width: 150px; margin: 15px auto;'></div>
            <p style='color: #64748b; font-size: 0.9rem;'>
                Private Secure Digital Forensics & Evidence Preservation Platform
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Grid layout to center login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='terminal-header'>
                <span class='mono-text' style='color: #00e5ff; font-weight: bold;'>🔐 PORTAL LOGIN EXECUTOR</span>
                <span style='color: #e53e3e;'>●</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("fafo_login_form"):
            username = st.text_input("Custodian Username / Case Handle", placeholder="e.g. submitter, reviewer", help="Enter registered FAFO security username")
            password = st.text_input("Security Passphrase key", type="password", placeholder="••••••••••••", help="Enter encrypted FAFO password key")
            selected_role = st.selectbox(
                "Choose Access Role Area:",
                [role.value for role in Role],
                index=0,
                help="Select the role area that matches this user account."
            )
            
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("AUTHORIZE SESSION ACCESS")
            
            if submit_button:
                if not username or not password or not selected_role:
                    st.error("Access Denied: Username, Passphrase, and Role selection are required.")
                else:
                    success, message = authenticate_user(username, password, selected_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display helper note with default passwords for demonstration
     #   with st.expander("🔑 Secure Developer Sandbox Credentials (Demo Only)"):
      #      st.markdown(
       #         """
       #         <div style='background-color: #02070e; border: 1px solid #1a3c6e; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.85rem;'>
        #            <b>Default Accounts:</b><br>
        #            • Submitter: <code style='color:#00e5ff;'>submitter</code> / passphrase: <code style='color:#00e5ff;'>Submitter@123</code><br>
        #            • Reviewer: <code style='color:#ff9f1c;'>reviewer</code> / passphrase: <code style='color:#ff9f1c;'>Reviewer@123</code><br>
        #            • Lawyer: <code style='color:#7289da;'>lawyer</code> / passphrase: <code style='color:#7289da;'>Lawyer@123</code><br>
       #             • Administrator: <code style='color:#ff3860;'>admin</code> / passphrase: <code style='color:#ff3860;'>Admin@123</code>
        #        </div>
         #       """, 
       #         unsafe_allow_html=True
           # )
