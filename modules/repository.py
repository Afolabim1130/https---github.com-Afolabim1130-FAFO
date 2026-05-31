"""
FAFO Repository Manager
Manages incident folder creation, logical sub-folder partitioning, and evidence storage paths.
"""
import os
import shutil
from pathlib import Path
from typing import Dict
from config.settings import EVIDENCE_REPOSITORY

def get_incident_dir(incident_key: str) -> Path:
    """Get absolute path to an incident's directory."""
    return EVIDENCE_REPOSITORY / incident_key

def create_incident_repository(incident_key: str) -> Dict[str, Path]:
    """
    Create a secure, structured physical folder structure for an incident.
    Creates subfolders for: screenshots, videos, audio, documents.
    """
    base_path = get_incident_dir(incident_key)
    
    subfolders = {
        "base": base_path,
        "screenshots": base_path / "screenshots",
        "videos": base_path / "videos",
        "audio": base_path / "audio",
        "documents": base_path / "documents"
    }
    
    for folder_name, folder_path in subfolders.items():
        folder_path.mkdir(parents=True, exist_ok=True)
        # On Unix systems we could restrict permissions here, e.g. 0o700,
        # but on Windows we rely on default folder creation & application-level access controls.
        
    return subfolders

def resolve_evidence_folder(incident_key: str, mime_type: str) -> Path:
    """
    Return the appropriate forensic subfolder path based on file MIME type.
    """
    repos = create_incident_repository(incident_key)
    
    if not mime_type:
        return repos["documents"]
        
    mime_lower = mime_type.lower()
    
    if mime_lower.startswith("image/"):
        return repos["screenshots"]
    elif mime_lower.startswith("video/"):
        return repos["videos"]
    elif mime_lower.startswith("audio/"):
        return repos["audio"]
    else:
        return repos["documents"]

def delete_incident_repository(incident_key: str) -> bool:
    """Delete all files in an incident repository (e.g. for rejected cases or cleanups)."""
    dir_path = get_incident_dir(incident_key)
    if dir_path.exists() and dir_path.is_dir():
        shutil.rmtree(dir_path)
        return True
    return False
