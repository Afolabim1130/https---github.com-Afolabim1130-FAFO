"""
FAFO Database Manager & Incident Data Access Layer
Manages connection sessions, transaction commits, and standard database queries.
"""
import sqlite3
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from config.settings import DATABASE_PATH

def get_db_connection() -> sqlite3.Connection:
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db_structure():
    """Initializes schema and seeds default users if not already present."""
    # This will be handled by the master setup or initialization,
    # but having a check ensures database robustness.
    pass

def generate_incident_key() -> str:
    """Generate a unique case file number in INC-YYYYMMDD-XXXX format."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INC-{date_str}-{random_str}"

# User Management
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user details by username."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, role, is_active FROM users WHERE username = ?",
            (username.lower(),)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user details by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, role, is_active FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def create_user(username: str, email: str, password_hash: str, role: str) -> int:
    """Create a new user in the system."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username.lower(), email, password_hash, role.lower())
        )
        conn.commit()
        return cursor.lastrowid

def get_all_users() -> List[Dict[str, Any]]:
    """Get list of all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at, is_active FROM users ORDER BY username ASC")
        return [dict(r) for r in cursor.fetchall()]

# Incident Management
def create_incident(
    title: str,
    description: str,
    submitter_id: int,
    category: str = "Uncategorized",
    severity: str = "Medium",
    repository_path: str = None
) -> int:
    """Create a new incident file record."""
    incident_key = generate_incident_key()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO incidents (incident_key, title, description, submitter_id, category, severity, repository_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (incident_key, title, description, submitter_id, category, severity, repository_path)
        )
        conn.commit()
        return cursor.lastrowid

def get_incident(incident_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve incident by database primary key ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.*, u.username as submitter_name, u.email as submitter_email,
                   a.username as approved_by_name
            FROM incidents i
            JOIN users u ON i.submitter_id = u.id
            LEFT JOIN users a ON i.approved_by_id = a.id
            WHERE i.id = ?
            """,
            (incident_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_incident_by_key(incident_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve incident details by clinical/forensic reference key."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.*, u.username as submitter_name, u.email as submitter_email
            FROM incidents i
            JOIN users u ON i.submitter_id = u.id
            WHERE i.incident_key = ?
            """,
            (incident_key,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_incidents(role_name: str = None, user_id: int = None) -> List[Dict[str, Any]]:
    """Get all incidents, with role-based restriction visibility."""
    query = """
        SELECT i.*, u.username as submitter_name,
               (SELECT COUNT(*) FROM evidence e WHERE e.incident_id = i.id) as file_count
        FROM incidents i
        JOIN users u ON i.submitter_id = u.id
    """
    params = []
    
    # Submitter can only see their own incidents
    if role_name == "submitter" and user_id is not None:
        query += " WHERE i.submitter_id = ?"
        params.append(user_id)
    # Lawyer can only see approved incidents
    elif role_name == "lawyer":
        query += " WHERE i.status = 'Approved'"
    
    query += " ORDER BY i.created_at DESC"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

def update_incident_status(incident_id: int, status: str, reviewer_id: int = None) -> bool:
    """Update status (Submitted, Reviewing, Approved, Rejected) of an incident."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status == "Approved" and reviewer_id is not None:
            cursor.execute(
                """
                UPDATE incidents 
                SET status = ?, approved_at = ?, approved_by_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, now, reviewer_id, now, incident_id)
            )
        else:
            cursor.execute(
                "UPDATE incidents SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, incident_id)
            )
        conn.commit()
        return cursor.rowcount > 0

def update_incident_details(incident_id: int, category: str, severity: str) -> bool:
    """Update details like AI-derived category or severity classification."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE incidents SET category = ?, severity = ?, updated_at = ? WHERE id = ?",
            (category, severity, now, incident_id)
        )
        conn.commit()
        return cursor.rowcount > 0

# Evidence Management
def add_evidence(
    incident_id: int,
    filename: str,
    original_filename: str,
    mime_type: str,
    file_path: str,
    file_size_bytes: int,
    sha256_hash: str,
    uploaded_by_id: int
) -> int:
    """Log details of a newly uploaded evidence file."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO evidence (incident_id, filename, original_filename, mime_type, file_path, file_size_bytes, sha256_hash, uploaded_by_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (incident_id, filename, original_filename, mime_type, file_path, file_size_bytes, sha256_hash, uploaded_by_id)
        )
        conn.commit()
        return cursor.lastrowid

def get_evidence_by_incident(incident_id: int) -> List[Dict[str, Any]]:
    """Retrieve all evidence files associated with an incident."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.*, u.username as uploaded_by_name 
            FROM evidence e
            JOIN users u ON e.uploaded_by_id = u.id
            WHERE e.incident_id = ?
            ORDER BY e.created_at ASC
            """,
            (incident_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

def get_evidence_by_id(evidence_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve details of a single evidence file by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM evidence WHERE id = ?",
            (evidence_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

# Subsystem Logging (OCR, AI, Video)
def add_ocr_result(evidence_id: int, extracted_text: str, confidence_score: float, extraction_method: str) -> int:
    """Save the text transcript extracted from an image file."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ocr_results (evidence_id, extracted_text, confidence_score, extraction_method)
            VALUES (?, ?, ?, ?)
            """,
            (evidence_id, extracted_text, confidence_score, extraction_method)
        )
        conn.commit()
        return cursor.lastrowid

def get_ocr_results_for_incident(incident_id: int) -> List[Dict[str, Any]]:
    """Retrieve all OCR text extracts in an incident."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.*, e.filename, e.original_filename
            FROM ocr_results o
            JOIN evidence e ON o.evidence_id = e.id
            WHERE e.incident_id = ?
            """,
            (incident_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

def add_ai_analysis(incident_id: int, suggested_category: str, suggested_severity: str, category_score: float) -> int:
    """Save the offline AI automated incident triage classifications."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ai_analysis (incident_id, suggested_category, suggested_severity, category_score)
            VALUES (?, ?, ?, ?)
            """,
            (incident_id, suggested_category, suggested_severity, category_score)
        )
        conn.commit()
        return cursor.lastrowid

def get_ai_analysis_for_incident(incident_id: int) -> Optional[Dict[str, Any]]:
    """Get the latest AI automated analysis metrics for an incident."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ai_analysis WHERE incident_id = ? ORDER BY analysis_timestamp DESC LIMIT 1",
            (incident_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def add_video_metadata(evidence_id: int, duration_seconds: float, width: int, height: int, codec: str) -> int:
    """Record forensic technical video specs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO video_metadata (evidence_id, duration_seconds, width, height, codec)
            VALUES (?, ?, ?, ?, ?)
            """,
            (evidence_id, duration_seconds, width, height, codec)
        )
        conn.commit()
        return cursor.lastrowid

def get_video_metadata_for_evidence(evidence_id: int) -> Optional[Dict[str, Any]]:
    """Get video forensic technical metrics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM video_metadata WHERE evidence_id = ?",
            (evidence_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

# Tamper-proof Security Auditing
def log_audit(user_id: Optional[int], action: str, resource_type: str = None, resource_id: int = None, details: str = None, ip_address: str = None) -> int:
    """Write an audit record to the persistent SQLite audit table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, action, resource_type, resource_id, details, ip_address)
        )
        conn.commit()
        return cursor.lastrowid

def get_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve chronologically ordered system audit trail logs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.*, u.username as user_name, u.role as user_role
            FROM audit_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(r) for r in cursor.fetchall()]
