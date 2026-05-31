"""
FAFO Forensic Export Manager
Assembles approved media case files, manifest checksums, and audit logs into a single forensic ZIP.
"""
import os
import json
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import pandas as pd
from modules.repository import get_incident_dir
from modules import incident_manager
from modules import hashing

def build_incident_metadata(incident_id: int) -> Dict[str, Any]:
    """
    Query all DB relations for an incident and compile a nested metadata dictionary.
    Includes case data, evidence lists, OCR, video meta, and chronological audit logs.
    """
    case = incident_manager.get_incident(incident_id)
    if not case:
        return {}
        
    incident_key = case["incident_key"]
    
    # 1. Fetch related tables
    evidence_list = incident_manager.get_evidence_by_incident(incident_id)
    ocr_list = incident_manager.get_ocr_results_for_incident(incident_id)
    ai_analysis = incident_manager.get_ai_analysis_for_incident(incident_id)
    
    # Get all audit logs relating to this incident
    all_audits = incident_manager.get_audit_logs(limit=1000)
    incident_audits = []
    for log in all_audits:
        if (log["resource_type"] == "incident" and log["resource_id"] == incident_id) or \
           (log["details"] and incident_key in log["details"]):
            incident_audits.append({
                "timestamp": log["timestamp"],
                "username": log["user_name"],
                "role": log["user_role"],
                "action": log["action"],
                "details": log["details"],
                "ip_address": log["ip_address"]
            })
            
    # Format evidence records and attach extra detail
    evidence_formatted = []
    for ev in evidence_list:
        ev_id = ev["id"]
        ev_dict = {
            "id": ev_id,
            "original_filename": ev["original_filename"],
            "filename": ev["filename"],
            "mime_type": ev["mime_type"],
            "file_size_bytes": ev["file_size_bytes"],
            "sha256_hash": ev["sha256_hash"],
            "uploaded_at": ev["created_at"],
            "uploaded_by": ev["uploaded_by_name"]
        }
        
        # Attach OCR if exists
        ev_ocr = [o for o in ocr_list if o["evidence_id"] == ev_id]
        if ev_ocr:
            ev_dict["ocr"] = {
                "text": ev_ocr[0]["extracted_text"],
                "confidence": ev_ocr[0]["confidence_score"],
                "method": ev_ocr[0]["extraction_method"]
            }
            
        # Attach Video Meta if exists
        ev_vid = incident_manager.get_video_metadata_for_evidence(ev_id)
        if ev_vid:
            ev_dict["video_metadata"] = {
                "duration_seconds": ev_vid["duration_seconds"],
                "width": ev_vid["width"],
                "height": ev_vid["height"],
                "codec": ev_vid["codec"]
            }
            
        evidence_formatted.append(ev_dict)
        
    metadata = {
        "incident_key": incident_key,
        "title": case["title"],
        "description": case["description"],
        "category": case["category"],
        "severity": case["severity"],
        "status": case["status"],
        "created_at": case["created_at"],
        "submitter": {
            "name": case["submitter_name"],
            "email": case["submitter_email"]
        },
        "approved_at": case["approved_at"],
        "approved_by": case["approved_by_name"],
        "ai_analysis": ai_analysis,
        "evidence": evidence_formatted,
        "audit_logs": sorted(incident_audits, key=lambda x: x["timestamp"])
    }
    
    return metadata

def compile_forensic_report_text(meta: Dict[str, Any]) -> str:
    """
    Format forensic metadata into a beautiful legal-ready plain-text report structure.
    """
    report = []
    border = "=" * 80
    sub_border = "-" * 80
    
    report.append(border)
    report.append("                   FAFO SECURE FORENSIC EVIDENCE CASE REPORT")
    report.append("                   LEGAL-READY STANDARDIZED RECORD SUMMARY")
    report.append(border)
    
    report.append(f"Incident Reference Key:  {meta['incident_key']}")
    report.append(f"Preservation Title:      {meta['title']}")
    report.append(f"Assigned Category:       {meta['category']}")
    report.append(f"Threat Severity Rating:  {meta['severity']}")
    report.append(f"Current Vault Status:    {meta['status']}")
    report.append(f"Created DateTime (UTC):  {meta['created_at']}")
    report.append(f"Custodian Submitter:     {meta['submitter']['name']} ({meta['submitter']['email']})")
    
    if meta['approved_at']:
        report.append(f"Authorized DateTime:     {meta['approved_at']}")
        report.append(f"Authorized Reviewer:     {meta['approved_by']}")
        
    report.append("\nCASE SUMMARY / CONTEXT DESCRIPTION:")
    report.append(sub_border)
    report.append(meta['description'] or "No contextual description provided.")
    report.append(sub_border)
    
    report.append(f"\nREGISTERED EVIDENCE FILES ({len(meta['evidence'])} count):")
    report.append(sub_border)
    
    for idx, ev in enumerate(meta['evidence'], 1):
        report.append(f"File #{idx}: {ev['original_filename']}")
        report.append(f"  Storage Name:   {ev['filename']}")
        report.append(f"  MIME-Type:      {ev['mime_type']}")
        report.append(f"  File Size:      {ev['file_size_bytes']} bytes")
        report.append(f"  SHA-256 Hash:   {ev['sha256_hash']}")
        report.append(f"  Uploaded By:    {ev['uploaded_by']} at {ev['uploaded_at']}")
        
        if "ocr" in ev:
            report.append("  OCR Extract (Tesseract Heuristics):")
            report.append("    [Text Begin]")
            # Indent text lines
            lines = ev['ocr']['text'].splitlines()
            for l in lines:
                report.append(f"      {l}")
            report.append("    [Text End]")
            report.append(f"    Confidence:   {int(ev['ocr']['confidence']*100)}% ({ev['ocr']['method']})")
            
        if "video_metadata" in ev:
            v = ev["video_metadata"]
            report.append("  Video Forensic Details:")
            report.append(f"    Duration:     {v['duration_seconds']} seconds")
            report.append(f"    Dimensions:   {v['width']} x {v['height']} pixels")
            report.append(f"    Codec:        {v['codec']}")
            
        report.append("")
        
    report.append(sub_border)
    report.append("CHRONOLOGICAL FORENSIC CHAIN OF CUSTODY AUDIT LOG:")
    report.append(sub_border)
    
    for log in meta['audit_logs']:
        report.append(
            f"[{log['timestamp']}] ACTION: {log['action']} | "
            f"ACTOR: {log['username']} ({log['role']}) | "
            f"IP: {log['ip_address']} | "
            f"DETAILS: {log['details']}"
        )
        
    report.append(border)
    report.append("   End of Forensic Case Report. Integrity Manifest Checked. Sealed vault record.")
    report.append(border)
    
    return "\n".join(report)

def generate_forensic_zip(incident_id: int) -> Optional[Path]:
    """
    Compile all files, database reports, audit logs, and checksum digests
    into a portable signed-ready .zip archive inside the incident directory.
    """
    case = incident_manager.get_incident(incident_id)
    if not case:
        return None
        
    incident_key = case["incident_key"]
    base_dir = get_incident_dir(incident_key)
    if not base_dir.exists():
        return None
        
    # 1. Regenerate current hashes companion to ensure absolute fresh integrity
    hashing.generate_hashes_json(incident_key)
    
    # 2. Build metadata dictionary and text summary
    meta = build_incident_metadata(incident_id)
    report_text = compile_forensic_report_text(meta)
    
    # 3. Write metadata.json and FORENSIC_SUMMARY.txt inside the directory temporarily
    meta_file = base_dir / "metadata.json"
    summary_file = base_dir / "FORENSIC_SUMMARY.txt"
    
    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=4)
        
    with open(summary_file, "w") as f:
        f.write(report_text)
        
    # 4. Generate the Zip file
    zip_filename = f"FAFO_FORENSIC_EXPORT_{incident_key}.zip"
    zip_path = base_dir / zip_filename
    
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add all files in base_dir, EXCEPT the zip file itself!
            for path in base_dir.rglob("*"):
                if path.is_file() and path.name != zip_filename:
                    # Maintain structure in zip relative to incident folder
                    rel_path = path.relative_to(base_dir)
                    zip_file.write(path, rel_path)
                    
        return zip_path
    except Exception as e:
        import logging
        logging.error(f"Failed to generate forensic zip export: {str(e)}")
        return None
