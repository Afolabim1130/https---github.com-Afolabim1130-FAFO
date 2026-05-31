"""
FAFO Configuration Management
Loads settings from environment variables with fallback defaults.
"""
import os
import logging
from pathlib import Path

# Application Root
APP_ROOT = Path(__file__).parent.parent

# Environment mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", APP_ROOT / "fafo_database.db"))
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Evidence Repository
EVIDENCE_REPOSITORY = Path(os.getenv("EVIDENCE_REPOSITORY", APP_ROOT / "evidence_repository"))
EVIDENCE_REPOSITORY.mkdir(parents=True, exist_ok=True)

# Logs Directory
LOGS_DIR = Path(os.getenv("LOGS_DIR", APP_ROOT / "logs"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# OCR Configuration
OCR_ENABLED = os.getenv("OCR_ENABLED", "True").lower() == "true"
OCR_TESSERACT_PATH = os.getenv("OCR_TESSERACT_PATH", None)
OCR_FALLBACK_ENABLED = os.getenv("OCR_FALLBACK_ENABLED", "True").lower() == "true"

# FFmpeg Configuration
FFMPEG_ENABLED = os.getenv("FFMPEG_ENABLED", "True").lower() == "true"
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFMPEG_FALLBACK_ENABLED = os.getenv("FFMPEG_FALLBACK_ENABLED", "True").lower() == "true"

# AI Classification Configuration
AI_CLASSIFIER_TYPE = os.getenv("AI_CLASSIFIER_TYPE", "tfidf")
AI_FALLBACK_ENABLED = os.getenv("AI_FALLBACK_ENABLED", "True").lower() == "true"

# Email/SMTP Configuration
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "False").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "fafo-notifications@example.com")
NOTIFICATION_LOG_FILE = LOGS_DIR / "notifications.log"

# Streamlit Configuration
STREAMLIT_THEME = "dark"
SIDEBAR_WIDTH = 250
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Session Management
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

# Security
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"

# Supported MIME types
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp",
    "video/mp4", "video/mpeg", "video/quicktime", "video/webm",
    "audio/mpeg", "audio/wav", "audio/ogg", "audio/m4a",
    "application/pdf", "text/plain", "application/json"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
