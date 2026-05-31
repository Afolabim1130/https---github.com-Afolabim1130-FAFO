"""
FAFO Forensics Integrity & Cryptographic Hashing Layer
Maintains mathematical chain of custody by hashing files and checking disk alterations.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
from modules.repository import get_incident_dir

def calculate_sha256(target) -> str:
    """
    Calculate SHA-256 hash of a file path or a bytes stream.
    """
    sha256_hash = hashlib.sha256()
    
    if isinstance(target, (str, Path)):
        with open(target, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
    elif isinstance(target, bytes):
        sha256_hash.update(target)
    elif hasattr(target, "read"): # stream or UploadedFile
        # Save current position if seekable
        pos = 0
        if hasattr(target, "seek"):
            try:
                pos = target.tell()
                target.seek(0)
            except Exception:
                pass
                
        for byte_block in iter(lambda: target.read(65536), b""):
            sha256_hash.update(byte_block)
            
        # Restore position
        if hasattr(target, "seek"):
            try:
                target.seek(pos)
            except Exception:
                pass
    else:
        raise TypeError("Unsupported target type for hashing.")
        
    return sha256_hash.hexdigest()

def generate_hashes_json(incident_key: str) -> Path:
    """
    Scans the incident's physical repository, computes SHA-256 hashes of all files,
    and updates/writes a companion `hashes.json` inside the base incident folder.
    """
    base_dir = get_incident_dir(incident_key)
    hash_map = {}
    
    # Recursively traverse all subfolders, ignoring the hashes.json file itself
    for path in base_dir.rglob("*"):
        if path.is_file() and path.name != "hashes.json" and path.name != "metadata.json":
            # Store relative path for portability across environments
            rel_path = path.relative_to(base_dir).as_posix()
            hash_map[rel_path] = calculate_sha256(path)
            
    hash_file_path = base_dir / "hashes.json"
    with open(hash_file_path, "w") as f:
        json.dump(hash_map, f, indent=4)
        
    return hash_file_path

def verify_incident_integrity(incident_key: str) -> Dict[str, Any]:
    """
    Recalculates the SHA-256 of all files currently on disk and compares them
    against the values saved in the companion `hashes.json`.
    Detects tampering, deletions, additions, or missing hashes.json.
    """
    base_dir = get_incident_dir(incident_key)
    hash_file_path = base_dir / "hashes.json"
    
    result = {
        "status": "VALID",
        "message": "All evidence files matches their registered forensic hashes.",
        "incident_key": incident_key,
        "is_valid": True,
        "tampered_files": [],
        "missing_files": [],
        "untracked_files": [],
        "registered_count": 0,
        "current_count": 0
    }
    
    if not hash_file_path.exists():
        result["status"] = "MISSING_MANIFEST"
        result["message"] = "Forensic manifest hashes.json was not found."
        result["is_valid"] = False
        return result
        
    # Read saved hashes
    try:
        with open(hash_file_path, "r") as f:
            registered_hashes = json.load(f)
    except Exception as e:
        result["status"] = "CORRUPT_MANIFEST"
        result["message"] = f"Failed to parse hashes.json: {str(e)}"
        result["is_valid"] = False
        return result
        
    result["registered_count"] = len(registered_hashes)
    
    # Scan files on disk
    current_files = {}
    for path in base_dir.rglob("*"):
        if path.is_file() and path.name != "hashes.json" and path.name != "metadata.json":
            rel_path = path.relative_to(base_dir).as_posix()
            current_files[rel_path] = path
            
    result["current_count"] = len(current_files)
    
    # 1. Check for missing or tampered files
    for rel_path, expected_hash in registered_hashes.items():
        if rel_path not in current_files:
            result["missing_files"].append(rel_path)
            result["is_valid"] = False
        else:
            file_path = current_files[rel_path]
            actual_hash = calculate_sha256(file_path)
            if actual_hash != expected_hash:
                result["tampered_files"].append({
                    "file": rel_path,
                    "expected": expected_hash,
                    "actual": actual_hash
                })
                result["is_valid"] = False
                
    # 2. Check for untracked files (added later without log)
    for rel_path in current_files:
        if rel_path not in registered_hashes:
            result["untracked_files"].append(rel_path)
            result["is_valid"] = False
            
    # Set final statuses
    if result["tampered_files"]:
        result["status"] = "TAMPERED"
        result["message"] = f"Warning: {len(result['tampered_files'])} file(s) have been modified after registration!"
    elif result["missing_files"]:
        result["status"] = "INCOMPLETE"
        result["message"] = f"Warning: {len(result['missing_files'])} registered file(s) are missing from the folder!"
    elif result["untracked_files"]:
        result["status"] = "UNTRACKED_FILES_PRESENT"
        result["message"] = f"Warning: {len(result['untracked_files'])} untracked file(s) are present in the folder!"
        
    return result
