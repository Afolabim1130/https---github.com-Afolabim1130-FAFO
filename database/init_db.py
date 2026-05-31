"""
FAFO Database Schema Initializer
Automatically executes schema SQL declarations and seeds default roles.
"""
import sqlite3
from pathlib import Path
from config.settings import DATABASE_PATH, APP_ROOT
from config.roles import DEFAULT_PASSWORDS
from modules import security

def initialize_database(force: bool = False) -> bool:
    """
    Check if database exists and is initialized.
    If not, executes database/schema.sql and seeds default users.
    """
    db_path = Path(DATABASE_PATH)
    schema_path = APP_ROOT / "database" / "schema.sql"
    
    if db_path.exists() and db_path.stat().st_size > 0 and not force:
        # DB already exists and contains data, skip
        return False
        
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Establish connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema
    try:
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        conn.commit()
    except Exception as e:
        import logging
        logging.error(f"Failed to execute schema SQL: {str(e)}")
        conn.close()
        return False
        
    # Seed default users
    for username, password in DEFAULT_PASSWORDS.items():
        email = f"{username}@fafo.local"
        pw_hash = security.hash_password(password)
        role = username.lower()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, pw_hash, role)
            )
        except sqlite3.IntegrityError:
            # Already seeded
            pass
            
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    success = initialize_database(force=True)
    if success:
        print("✓ Database successfully initialized and seeded with default users.")
    else:
        print("✗ Database initialization skipped or encountered error.")
