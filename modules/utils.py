"""FAFO Helper Utilities and Streamlit Custom CSS Injections"""
from datetime import datetime, timezone
import streamlit as st

def format_timestamp(dt: datetime) -> str:
    """Format datetime as UTC ISO string or human-readable form."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    
    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
        
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def human_readable_size(size_bytes: int) -> str:
    """Format file size in human-readable bytes, KB, MB, GB."""
    if size_bytes is None:
        return "0 Bytes"
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}" if unit != 'Bytes' else f"{int(size_bytes)} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_cyber_css() -> str:
    """Generate high-fidelity cyberpunk/dark cyber-forensics styling for FAFO."""
    return """
    <style>
    /* Custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;600;800&display=swap');

    /* Global styling overrides */
    .stApp {
        background-color: #05080e !important;
        background-image: 
            radial-gradient(at 0% 0%, hsla(215, 80%, 10%, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 0%, hsla(210, 80%, 8%, 0.5) 0px, transparent 50%),
            radial-gradient(at 50% 100%, hsla(180, 80%, 5%, 0.3) 0px, transparent 50%) !important;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #e2e8f0 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        letter-spacing: -0.02em !important;
    }

    /* Coding/Mono Font for hashes & forensics details */
    .mono-text, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }

    /* Terminal Glow */
    .terminal-header {
        background: linear-gradient(90deg, #09172d 0%, #0d264a 100%);
        border: 1px solid #1a3c6e;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .terminal-body {
        background-color: #030a13;
        border-left: 1px solid #1a3c6e;
        border-right: 1px solid #1a3c6e;
        border-bottom: 1px solid #1a3c6e;
        border-radius: 0px 0px 8px 8px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }

    /* Custom Glassmorphic Card */
    .cyber-card {
        background: rgba(10, 18, 30, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(26, 60, 110, 0.4);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    .cyber-card:hover {
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 8px 32px 0 rgba(0, 229, 255, 0.1);
        transform: translateY(-2px);
    }

    /* Form labels and field styling */
    label, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label,
    .stCheckbox label, .stRadio label, .stNumberInput label, .stDateInput label {
        color: #cbd5e1 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    input[type="text"], input[type="password"], input[type="email"], textarea, select {
        background-color: rgba(10, 20, 34, 0.95) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(74, 85, 104, 0.85) !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03) !important;
    }

    input::placeholder, textarea::placeholder {
        color: rgba(226, 232, 240, 0.58) !important;
    }

    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border-color: #00e5ff !important;
        box-shadow: 0 0 0 4px rgba(0, 229, 255, 0.14) !important;
    }

    .stSelectbox > div > div:nth-child(1),
    .stMultiSelect > div > div:nth-child(1) {
        background-color: rgba(10, 20, 34, 0.9) !important;
        border-radius: 10px !important;
    }

    .stRadio > div[role="radiogroup"] label,
    .stCheckbox > div label {
        color: #e2e8f0 !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div > div,
    .stMultiSelect > div > div > div > div {
        color: #e2e8f0 !important;
    }

    /* Neon accents */
    .neon-text-cyan {
        color: #00e5ff !important;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }
    .neon-text-green {
        color: #39ff14 !important;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
    }
    .neon-text-orange {
        color: #ff9f1c !important;
        text-shadow: 0 0 10px rgba(255, 159, 28, 0.5);
    }
    .neon-text-red {
        color: #ff3860 !important;
        text-shadow: 0 0 10px rgba(255, 56, 96, 0.5);
    }

    /* KPI metric style overrides */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(8, 16, 28, 0.8) !important;
        border: 1px solid rgba(26, 60, 110, 0.4) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }

    /* Custom buttons styling */
    .stButton>button {
        background: linear-gradient(135deg, #102a45 0%, #07192b 100%) !important;
        border: 1px solid #1a3c6e !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.82rem 1.6rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #00e5ff 0%, #008ca8 100%) !important;
        border-color: #00e5ff !important;
        color: #05080e !important;
        box-shadow: 0 0 18px rgba(0, 229, 255, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    .stButton>button:active {
        transform: translateY(1px) !important;
    }
    
    /* Submit/Save primary action */
    .stButton.primary-btn>button {
        background: linear-gradient(135deg, #00e5ff 0%, #008ca8 100%) !important;
        border-color: #00e5ff !important;
        color: #05080e !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.3) !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5, 8, 14, 0.98), rgba(10, 18, 30, 0.98)) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(18px) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 24px 18px 20px 18px !important;
    }

    section[data-testid="stSidebar"] .sidebar-section {
        background: rgba(10, 18, 34, 0.95);
        border: 1px solid rgba(74, 85, 104, 0.65);
        border-radius: 18px;
        padding: 16px 16px 20px 16px;
        margin-bottom: 18px;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    section[data-testid="stSidebar"] .stRadio .css-1e5imcs {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stButton>button {
        width: 100% !important;
        padding: 0.9rem 1rem !important;
    }

    section[data-testid="stSidebar"] .stMarkdown>div {
        color: #cbd5e1 !important;
    }

    .sidebar-label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        margin-bottom: 10px !important;
    }
    
    .stButton.primary-btn>button:hover {
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6) !important;
    }

    /* Banner notification overrides */
    .stAlert {
        background: rgba(10, 18, 30, 0.9) !important;
        border: 1px solid #1a3c6e !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    
    /* Custom status pill */
    .status-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-submitted {
        background-color: rgba(32, 129, 226, 0.15);
        color: #00e5ff;
        border: 1px solid rgba(0, 229, 255, 0.4);
    }
    .status-reviewing {
        background-color: rgba(255, 159, 28, 0.15);
        color: #ff9f1c;
        border: 1px solid rgba(255, 159, 28, 0.4);
    }
    .status-approved {
        background-color: rgba(57, 255, 20, 0.15);
        color: #39ff14;
        border: 1px solid rgba(57, 255, 20, 0.4);
    }
    .status-rejected {
        background-color: rgba(255, 56, 96, 0.15);
        color: #ff3860;
        border: 1px solid rgba(255, 56, 96, 0.4);
    }
    
    /* Cryptographic status container */
    .crypto-verify-box {
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
        font-family: 'JetBrains Mono', monospace;
    }
    .crypto-valid {
        background-color: rgba(57, 255, 20, 0.05);
        border: 1px solid rgba(57, 255, 20, 0.3);
        color: #39ff14;
    }
    .crypto-invalid {
        background-color: rgba(255, 56, 96, 0.05);
        border: 1px solid rgba(255, 56, 96, 0.3);
        color: #ff3860;
    }
    </style>
    """

def inject_cyber_css():
    """Inject custom cybersecurity theme CSS into current Streamlit view."""
    st.markdown(get_cyber_css(), unsafe_allow_html=True)
