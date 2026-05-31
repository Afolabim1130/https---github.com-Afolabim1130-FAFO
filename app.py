"""
FAFO (Facts, Accountability, Forensics, and Observation)
Secure Multimedia Evidence Logging and Incident Preservation Platform

Main Entrypoint Streamlit GUI.
"""
import os
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import pytesseract

# Configure page settings first
st.set_page_config(
    page_title="FAFO Secure Forensics preservation vault",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core package imports
from config.settings import ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE_BYTES, MAX_UPLOAD_SIZE_MB, FFMPEG_PATH
from config.roles import Role, Permissions, has_permission
from database.init_db import initialize_database
from modules import auth
from modules import utils
from modules import incident_manager
from modules import repository
from modules import security
from modules import hashing
from modules import audit_logger
from modules import ocr_engine
from modules import ai_classifier
from modules import ffmpeg_processor
from modules import notifications
from modules import dashboard
from modules import lawyer_portal
from modules import export_manager

# 1. Initialize DB structure on startup
initialize_database()

# 2. Setup Security Session State
auth.init_session_state()

# 3. Inject CSS visual style rules
utils.inject_cyber_css()

# 4. Check for inactivity timeout
auth.check_session_timeout()

# 5. Handle login screen
if not st.session_state.get("logged_in", False):
    auth.render_login_panel()
else:
    user = st.session_state["user"]
    username = user["username"]
    role = user["role"] # Enum Role
    
    # Render main app header inside the sidebar
    with st.sidebar:
        st.markdown(
            f"""
            <div class='sidebar-section'>
                <div style='text-align: center; padding: 18px 0 10px 0;'>
                    <h2 class='neon-text-cyan' style='font-size: 2.1rem; font-weight: 900; margin: 0;'>🛡️ FAFO</h2>
                    <p style='color: #94a3b8; font-family: monospace; font-size: 0.78rem; letter-spacing: 0.16em; margin: 8px 0 0 0;'>SECURITY VAULT V1.0</p>
                    <div style='border-top: 1px solid rgba(255,255,255,0.12); margin: 14px auto; max-width: 120px;'></div>
                    <p style='color: #cbd5e1; font-size: 0.82rem; margin: 8px 0 0 0;'>Mission Control · Evidence Operations · Role Protection</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display Current Active User Panel
        role_colors = {
            Role.SUBMITTER: "#00e5ff", # Cyan
            Role.REVIEWER: "#ff9f1c",  # Orange
            Role.LAWYER: "#7289da",    # Blue
            Role.ADMIN: "#ff3860"      # Red
        }
        r_color = role_colors.get(role, "#e2e8f0")
        
        st.markdown(
            f"""
            <div class='sidebar-section'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;'>
                    <div>
                        <div class='sidebar-label'>ACTIVE OPERATOR</div>
                        <div style='font-size: 1.05rem; font-weight: 800; color: #ffffff;'>👤 {username}</div>
                    </div>
                    <span style='padding: 6px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; background-color: {r_color}1a; color: {r_color}; border: 1px solid {r_color}4d; text-transform: uppercase;'>
                        {role.value}
                    </span>
                </div>
                <div style='color:#94a3b8; font-size:0.85rem; line-height:1.5;'>Your secure session is active and current interface permissions are enforced by the FAFO role policy engine.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Segment views based on roles
        views = []
        if has_permission(role, Permissions.INCIDENT_CREATE):
            views.append("Submit Case Evidence")
        if has_permission(role, Permissions.INCIDENT_APPROVE):
            views.append("Operations Dashboard")
            views.append("Case Triage & Audits")
        if role == Role.LAWYER:
            views.append("Legal Audit portal")
        if has_permission(role, Permissions.USER_MANAGE):
            # Admin gets to choose anything
            views = ["Operations Dashboard", "Submit Case Evidence", "Case Triage & Audits", "Legal Audit portal", "System Administration"]
            
        st.markdown("<div class='sidebar-label'>SELECT MISSION INTERFACE</div>", unsafe_allow_html=True)
        selected_view = st.radio("", views)
        
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        # Log out button
        if st.button("TERMINATE SESSION"):
            auth.logout()
            st.rerun()
            
    # --- RENDER SELECTED VIEW PANELS ---
    
    # A. SUBMIT CASE EVIDENCE
    if selected_view == "Submit Case Evidence":
        st.markdown("<h1 class='neon-text-cyan'>🛡️ PRESSED EVIDENCE UPLOAD CONSOLE</h1>", unsafe_allow_html=True)
        st.markdown("Preserve digital threats, screenshots, media uploads, and track cases under strict cryptographic integrity hashes.")
        
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📝 Create New Forensic Case File</h3>", unsafe_allow_html=True)
        
        with st.form("create_incident_form", clear_on_submit=True):
            title = st.text_input("Incident Case Title / Headline", placeholder="e.g. Doxxing Threat from Anonymous Account on Twitter", help="Provide a short, distinct identifier of the incident")
            source_url = st.text_input(
                "Evidence Source URL / Social Media Link",
                placeholder="https://twitter.com/...",
                help="Enter the original source URL or social media post associated with this evidence."
            )
            description = st.text_area("Detailed Evidence Context Narrative", placeholder="State what happened, handles involved, and observations without embedding the source URL here.", help="Describe the nature of the incident, participants, timelines, and related context.")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox(
                    "Suggested Category (Auto-Triage Override):",
                    ["Uncategorized", "Cyberbullying", "Doxxing/Privacy", "Extortion/Threats", "Corporate Sabotage", "General Harassment"]
                )
            with col2:
                severity = st.selectbox(
                    "Observed Severity Rating:",
                    ["Low", "Medium", "High", "Critical"]
                )
                
            uploaded_files = st.file_uploader(
                "Upload Forensic Evidence Media files (Screenshots, MP4, PDFs, Audio, text):",
                accept_multiple_files=True,
                help=f"Supported MIME types: Images, Videos, Audio, PDFs, TXT. Max size: {MAX_UPLOAD_SIZE_MB}MB per file."
            )
            
            st.markdown(
                """
                <div style='background-color: rgba(229, 62, 62, 0.05); border: 1px solid rgba(229, 62, 62, 0.2); padding: 10px; border-radius: 6px; font-size: 0.8rem; color: #ff3860; margin: 10px 0;'>
                    ⚠️ <b>FORENSIC INTEGRITY NOTICE:</b> All uploaded files will be computed with sha256 checksums immediately. 
                    Deleting or altering files on the system disk will void the certified chain-of-custody validity.
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            submit_btn = st.form_submit_button("SUBMIT AND SEAL FORENSIC VAULT")
            
            if submit_btn:
                if not title or not description:
                    st.error("Case submission requires a Title and Description Narrative.")
                else:
                    if source_url:
                        description = f"{description}\n\nSource URL: {source_url}"
                    with st.spinner("Generating secure repository vaults and cryptographic records..."):
                        # 1. Generate Case inside database
                        # Temporary repository path
                        temp_key = "TEMP"
                        incident_id = incident_manager.create_incident(
                            title=title,
                            description=description,
                            submitter_id=user["id"],
                            category=category,
                            severity=severity
                        )
                        
                        # Get real key
                        fresh_case = incident_manager.get_incident(incident_id)
                        incident_key = fresh_case["incident_key"]
                        
                        # 2. Lock down dedicated repository folders
                        repos = repository.create_incident_repository(incident_key)
                        repository_path = str(repos["base"])
                        
                        # Update DB case path
                        incident_manager.update_incident_details(incident_id, category, severity)
                        # Actually need to write the repository path to DB
                        with incident_manager.get_db_connection() as conn:
                            conn.execute("UPDATE incidents SET repository_path = ? WHERE id = ?", (repository_path, incident_id))
                            conn.commit()
                            
                        # 3. Process Uploaded Files
                        processed_elements = []
                        for f in uploaded_files:
                            file_bytes = f.read()
                            
                            # Validate MIME
                            mime_type = f.type
                            if not security.validate_mime_type(mime_type):
                                st.warning(f"File '{f.name}' skipped: MIME type '{mime_type}' not permitted by vault configuration policy.")
                                continue
                                
                            if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
                                st.warning(f"File '{f.name}' skipped: Exceeds maximum size boundary of {MAX_UPLOAD_SIZE_MB}MB.")
                                continue
                                
                            # Sanitize filename
                            clean_filename = security.sanitize_filename(f.name)
                            # Resolve target folder based on mime
                            dest_folder = repository.resolve_evidence_folder(incident_key, mime_type)
                            file_disk_path = dest_folder / clean_filename
                            
                            # Write file to disk
                            with open(file_disk_path, "wb") as out_f:
                                out_f.write(file_bytes)
                                
                            # Calculate SHA-256 fingerprint
                            sha256_hash = hashing.calculate_sha256(file_disk_path)
                            
                            # Register inside evidence table
                            evidence_id = incident_manager.add_evidence(
                                incident_id=incident_id,
                                filename=clean_filename,
                                original_filename=f.name,
                                mime_type=mime_type,
                                file_path=str(file_disk_path),
                                file_size_bytes=len(file_bytes),
                                sha256_hash=sha256_hash,
                                uploaded_by_id=user["id"]
                            )
                            
                            # Forensic Subsystems: Process OCR for Screenshots
                            extracted_ocr_text = ""
                            if mime_type.startswith("image/"):
                                ocr_text, ocr_conf, ocr_method = ocr_engine.extract_text_from_image(file_disk_path)
                                incident_manager.add_ocr_result(
                                    evidence_id=evidence_id,
                                    extracted_text=ocr_text,
                                    confidence_score=ocr_conf,
                                    extraction_method=ocr_method
                                )
                                extracted_ocr_text = ocr_text
                                
                            # Forensic Subsystems: Process Video Codecs and Duration
                            if mime_type.startswith("video/"):
                                vid_meta = ffmpeg_processor.extract_video_metadata(file_disk_path)
                                incident_manager.add_video_metadata(
                                    evidence_id=evidence_id,
                                    duration_seconds=vid_meta["duration_seconds"],
                                    width=vid_meta["width"],
                                    height=vid_meta["height"],
                                    codec=vid_meta["codec"]
                                )
                                
                            processed_elements.append(f.name)
                            
                        # 4. Perform AI Triage Analysis on submission corpus
                        ocr_corpus = "\n".join([ocr_engine.extract_text_from_image(repository.resolve_evidence_folder(incident_key, f.type) / security.sanitize_filename(f.name))[0] for f in uploaded_files if f.type.startswith("image/")])
                        ai_triage = ai_classifier.analyze_and_triage_incident(
                            incident_key=incident_key,
                            title=title,
                            description=description,
                            ocr_text=ocr_corpus
                        )
                        
                        # Save AI suggestion to DB analysis table
                        incident_manager.add_ai_analysis(
                            incident_id=incident_id,
                            suggested_category=ai_triage["suggested_category"],
                            suggested_severity=ai_triage["suggested_severity"],
                            category_score=ai_triage["category_confidence"]
                        )
                        
                        # 5. Lock forensic folder: compile hashing manifest hashes.json
                        hashing.generate_hashes_json(incident_key)
                        
                        # 6. Audit logging
                        audit_logger.log_action(
                            user=user,
                            action="incident_create",
                            resource_type="incident",
                            resource_id=incident_id,
                            details=f"Created case {incident_key} and uploaded {len(processed_elements)} evidence file(s)",
                            ip_address=audit_logger.get_streamlit_ip()
                        )
                        
                        # 7. Alert notification email & text log trigger
                        notifications.send_submission_alert(
                            incident_key=incident_key,
                            title=title,
                            severity=severity,
                            submitter_name=username,
                            submitter_email=user["email"]
                        )
                        
                    st.success(f"✓ Case {incident_key} has been successfully locked, fingerprinted and sealed!")
                    st.markdown(
                        f"""
                        <div style='background-color:#02070e; border:1px solid #00e5ff; padding:15px; border-radius:6px; margin-bottom:15px;'>
                            <b>🔒 CASE METADATA SEALED:</b><br>
                            • Case Number: <code style='color:#00e5ff;'>{incident_key}</code><br>
                            • Category Triage: <code style='color:#ff9f1c;'>{ai_triage['suggested_category']}</code> (Confidence: {int(ai_triage['category_confidence']*100)}%)<br>
                            • Cryptographic Hash Manifest Generated: <code>hashes.json</code> created.<br>
                            • Review status: <b>Pending Reviewer Authentication</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show Submitter Case History Grid
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        my_cases = incident_manager.get_all_incidents(role_name="submitter", user_id=user["id"])
        dashboard.render_recent_incidents_grid(my_cases)
        
    # B. OPERATIONS DASHBOARD
    elif selected_view == "Operations Dashboard":
        st.markdown("<h1 class='neon-text-cyan'>🛡️ SECURITY OPERATIONS CENTER (SOC)</h1>", unsafe_allow_html=True)
        st.markdown("Real-time telemetry, classification models metrics, threat vectors, and case distribution grids.")
        
        # Load all incidents for analytics
        all_incidents = incident_manager.get_all_incidents()
        
        dashboard.render_kpi_metrics(all_incidents)
        dashboard.render_visualizations(all_incidents)
        
    # C. CASE TRIAGE & AUDITS
    elif selected_view == "Case Triage & Audits":
        st.markdown("<h1 class='neon-text-cyan'>🔍 FORENSIC CASE TRIAGE & AUDIT WORKSPACE</h1>", unsafe_allow_html=True)
        st.markdown("Review submitted evidence narrative records, audit files integrity, check AI analysis, and authorize releases.")
        
        # Load all active cases in system
        all_incidents = incident_manager.get_all_incidents()
        
        if not all_incidents:
            st.info("No cases logged in system. Upload an incident from the Submitter interface to initiate triage.")
        else:
            case_options = {f"[{c['incident_key']}] {c['title']}": c for c in all_incidents}
            selected_case = st.selectbox("Select Active Case File to Triage:", list(case_options.keys()))
            
            if selected_case:
                case = case_options[selected_case]
                incident_id = case["id"]
                incident_key = case["incident_key"]
                
                # Fetch fresh metadata details
                meta = export_manager.build_incident_metadata(incident_id)
                
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                col1, col2 = st.columns([5, 4])
                
                with col1:
                    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
                    st.markdown(f"<h3>📂 Incident Dossier: {meta['incident_key']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<b>Title:</b> {meta['title']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Preservation Category:</b> <code class='mono-text'>{meta['category']}</code>", unsafe_allow_html=True)
                    st.markdown(f"<b>Threat Severity:</b> <code class='mono-text'>{meta['severity']}</code>", unsafe_allow_html=True)
                    st.markdown(f"<b>Current Vault Status:</b> <span class='status-pill status-{meta['status'].lower()}'>{meta['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<b>Preservation Custodian:</b> {meta['submitter']['name']} ({meta['submitter']['email']})", unsafe_allow_html=True)
                    
                    st.markdown("<h4 style='margin-top:15px; color:#00e5ff;'>📝 Context Narrative Details:</h4>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div style='background-color:#02070e; border:1px solid #1a3c6e; padding:12px; border-radius:6px; font-size:0.9rem; color:#d2d6dc; line-height:1.5;'>"
                        f"{meta['description']}"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Case Release and release authorization controls
                    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
                    st.markdown("<h3>🎯 Case Classification & Release Authorization</h3>", unsafe_allow_html=True)
                    
                    with st.form("triage_update_form"):
                        new_category = st.selectbox(
                            "Update Forensic Classification:",
                            ["Cyberbullying", "Doxxing/Privacy", "Extortion/Threats", "Corporate Sabotage", "General Harassment"],
                            index=["Cyberbullying", "Doxxing/Privacy", "Extortion/Threats", "Corporate Sabotage", "General Harassment"].index(meta["category"]) if meta["category"] in ["Cyberbullying", "Doxxing/Privacy", "Extortion/Threats", "Corporate Sabotage", "General Harassment"] else 0
                        )
                        new_severity = st.selectbox(
                            "Override Severity Rating:",
                            ["Low", "Medium", "High", "Critical"],
                            index=["Low", "Medium", "High", "Critical"].index(meta["severity"]) if meta["severity"] in ["Low", "Medium", "High", "Critical"] else 1
                        )
                        new_status = st.selectbox(
                            "Authorize Release Status:",
                            ["Submitted", "Reviewing", "Approved", "Rejected"],
                            index=["Submitted", "Reviewing", "Approved", "Rejected"].index(meta["status"])
                        )
                        
                        submit_triage = st.form_submit_button("LOCK AND APPLY TRIAGE CLASSIFICATIONS")
                        
                        if submit_triage:
                            # Save classifications
                            incident_manager.update_incident_details(incident_id, new_category, new_severity)
                            incident_manager.update_incident_status(incident_id, new_status, user["id"])
                            
                            # Log audit action
                            audit_logger.log_action(
                                user=user,
                                action="incident_update",
                                resource_type="incident",
                                resource_id=incident_id,
                                details=f"Triaged case {incident_key}: Category={new_category}, Severity={new_severity}, Status={new_status}",
                                ip_address=audit_logger.get_streamlit_ip()
                            )
                            
                            st.success("✓ Forensic database records updated successfully!")
                            st.rerun()
                            
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with col2:
                    # AI suggestions & predictions telemetry
                    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
                    st.markdown("<h3>🤖 FAFO Offline AI Triage Telemetry</h3>", unsafe_allow_html=True)
                    
                    if meta["ai_analysis"]:
                        ai = meta["ai_analysis"]
                        st.markdown(
                            f"""
                            <div style='background-color:#02070e; border:1px solid #1a3c6e; padding:15px; border-radius:6px;'>
                                • Suggested Category: <b style='color:#00e5ff;'>{ai['suggested_category']}</b><br>
                                • Category Weight/Score: <b style='color:#39ff14;'>{int(ai['category_score']*100)}% Match</b><br>
                                • Suggested Severity: <b style='color:#ff9f1c;'>{ai['suggested_severity']}</b><br>
                                • Engine Model Type: <code>Offline Lexicon / TF-IDF density</code><br>
                                • Triage Timestamp: <span style='font-size:0.8rem; color:#64748b;'>{utils.format_timestamp(ai['analysis_timestamp'])}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("No AI triage records logged for this case.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display Cryptographic manifest validation check
                    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
                    st.markdown("<h3>🛡️ Cryptographic Integrity Check</h3>", unsafe_allow_html=True)
                    
                    run_integrity = st.button("RUN DEEP VAULT INTEGRITY CHECKSUM")
                    if run_integrity:
                        # Log verify action
                        audit_logger.log_action(
                            user=user,
                            action="evidence_verify",
                            resource_type="incident",
                            resource_id=incident_id,
                            details=f"Ran cryptographic integrity verification on incident {incident_key}",
                            ip_address=audit_logger.get_streamlit_ip()
                        )
                        
                        report = hashing.verify_incident_integrity(incident_key)
                        if report["is_valid"]:
                            st.success(f"✓ ALL FILES VALID: {report['message']}")
                        else:
                            st.error(f"🚨 INTEGRITY ALARM: {report['message']}")
                            if report["tampered_files"]:
                                st.markdown("<b>Tampered Files:</b>", unsafe_allow_html=True)
                                for tf in report["tampered_files"]:
                                    st.markdown(f"<code style='color:#ff3860;'>{tf['file']} (Expected: {tf['expected'][:10]}... Actual: {tf['actual'][:10]}...)</code>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='font-size:0.85rem; color:#64748b;'>Launch checksum scanner to recalculate files hashes against hashes.json manifest.</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                # Full Case Evidence List showing file contents, video details and OCR
                st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3>📦 Certified Evidence Items Inventory ({len(meta['evidence'])} items)</h3>", unsafe_allow_html=True)
                
                for idx, ev in enumerate(meta['evidence'], 1):
                    st.markdown(f"<b>Item #{idx}: {ev['original_filename']}</b>", unsafe_allow_html=True)
                    
                    col_det, col_media = st.columns([1, 1])
                    with col_det:
                        st.markdown(
                            f"<div style='font-family:monospace; font-size:0.8rem; color:#94a3b8; padding-left:10px; margin-bottom:15px; border-left: 2px solid #1a3c6e;'>"
                            f"• filename: {ev['filename']}<br>"
                            f"• MIME type: {ev['mime_type']}<br>"
                            f"• File size: {utils.human_readable_size(ev['file_size_bytes'])}<br>"
                            f"• Uploaded: {utils.format_timestamp(ev['uploaded_at'])} by {ev['uploaded_by']}<br>"
                            f"• Hash: {ev['sha256_hash']}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        
                        if "ocr" in ev:
                            st.markdown("<b style='color:#00e5ff;'>🔍 Extracted OCR screenshot transcript text:</b>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div style='background-color:#02070e; border:1px solid #1a3c6e; padding:10px; border-radius:6px; font-family:monospace; font-size:0.8rem; color:#a2b0c4; max-height:200px; overflow-y:auto; line-height:1.4; white-space:pre-wrap; margin-bottom:15px;'>"
                                f"{ev['ocr']['text']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        if "video_metadata" in ev:
                            v = ev["video_metadata"]
                            st.markdown("<b style='color:#ff9f1c;'>🎥 Video Forensic Header specs:</b>", unsafe_allow_html=True)
                            st.markdown(
                                f"<div style='font-family:monospace; font-size:0.8rem; color:#ff9f1c; padding-left:10px; margin-bottom:15px;'>"
                                f"• duration: {v['duration_seconds']} seconds<br>"
                                f"• resolution: {v['width']} x {v['height']} pixels<br>"
                                f"• Codec atom: {v['codec']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                    with col_media:
                        if ev["mime_type"].startswith("image/"):
                            file_disk_path = Path(case["repository_path"]) / "screenshots" / ev["filename"]
                            if file_disk_path.exists():
                                st.image(str(file_disk_path), caption=f"Screenshot Evidence #{idx}", use_container_width=True)
                        elif ev["mime_type"].startswith("video/"):
                            file_disk_path = Path(case["repository_path"]) / "videos" / ev["filename"]
                            if file_disk_path.exists():
                                st.video(str(file_disk_path), format=ev["mime_type"])
                        elif ev["mime_type"].startswith("audio/"):
                            file_disk_path = Path(case["repository_path"]) / "audio" / ev["filename"]
                            if file_disk_path.exists():
                                st.audio(str(file_disk_path), format=ev["mime_type"])
                                
                    st.markdown("<hr style='border-color:#1a3c6e; opacity:0.3; margin:15px 0;'>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
    # D. LEGAL AUDIT PORTAL
    elif selected_view == "Legal Audit portal":
        lawyer_portal.render_lawyer_dashboard()
        
    # E. SYSTEM ADMINISTRATION
    elif selected_view == "System Administration":
        st.markdown("<h1 class='neon-text-red'>🛡️ FAFO SYSTEM SECURITY ADMINISTRATION</h1>", unsafe_allow_html=True)
        st.markdown("Database management, access controls configurations, fallback diagnostic alerts, and immutable audit logs.")
        
        tab1, tab2, tab3 = st.tabs(["👥 Custodian Role access", "📜 Immutable System Audit logs", "🔧 Diagnostics & Fallback Checks"])
        
        with tab1:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("<h3>👥 Create New System Custodian User</h3>", unsafe_allow_html=True)
            
            with st.form("create_user_form", clear_on_submit=True):
                new_username = st.text_input("New Operator Username Handle", placeholder="e.g. detective_smith", help="Enter username alphanumeric handle")
                new_email = st.text_input("Custodian Secure Email Address", placeholder="e.g. smith@fafo.local", help="Operator security mail contact")
                new_password = st.text_input("New Security Passphrase key", type="password", placeholder="••••••••••••", help="Passphrase must satisfy local vault policies")
                new_role = st.selectbox("Assign Vault Access Role Permissions:", ["submitter", "reviewer", "lawyer", "admin"])
                
                submit_user = st.form_submit_button("REGISTER AND HASH OPERATOR KEY")
                
                if submit_user:
                    if not new_username or not new_email or not new_password:
                        st.error("User creation requires Username, Email and Passphrase Key.")
                    else:
                        try:
                            # Hashing password using standard bcrypt rounds
                            hashed_pw = security.hash_password(new_password)
                            user_id = incident_manager.create_user(
                                username=new_username,
                                email=new_email,
                                password_hash=hashed_pw,
                                role=new_role
                            )
                            
                            # Log audit action
                            audit_logger.log_action(
                                user=user,
                                action="user_create",
                                resource_type="user",
                                resource_id=user_id,
                                details=f"Registered new user operator handle '{new_username}' with role '{new_role}'",
                                ip_address=audit_logger.get_streamlit_ip()
                            )
                            
                            st.success(f"✓ Custodian Operator '{new_username}' registered with role '{new_role}' successfully!")
                            
                        except Exception as e:
                            st.error(f"Integrity Violation: Username or Email already exists in records database. ({str(e)})")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display active user table
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📊 Active System Custodians Vault Accounts</h3>", unsafe_allow_html=True)
            
            user_list = incident_manager.get_all_users()
            st.dataframe(pd.DataFrame(user_list).set_index("id"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📜 System Chronological Security Audit Logs</h3>", unsafe_allow_html=True)
            st.markdown("This view provides a chronologically ordered list of administrative actions pulled directly from SQLite DB.")
            
            logs = incident_manager.get_audit_logs(limit=100)
            if logs:
                st.dataframe(pd.DataFrame(logs).set_index("id"), use_container_width=True)
            else:
                st.info("Audit log is empty.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Text based audit log file viewer
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📁 Immutable Text-Based Log Trail: logs/audit_trail.log</h3>", unsafe_allow_html=True)
            
            audit_trail_path = Path("logs/audit_trail.log")
            if audit_trail_path.exists():
                try:
                    with open(audit_trail_path, "r") as f:
                        log_lines = f.readlines()
                    # Show last 50 lines
                    st.text_area(
                        label="Forensic text file tail (Last 50 actions):",
                        value="".join(log_lines[-50:]),
                        height=350,
                        help="Text logs are directly appended to the physical drive in logs/audit_trail.log"
                    )
                except Exception as e:
                    st.error(f"Failed to read logs: {str(e)}")
            else:
                st.info("No physical audit_trail.log text file detected yet.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab3:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("<h3>🔧 Binary Dependencies Diagnostics & Fallback Flags</h3>", unsafe_allow_html=True)
            st.markdown("Audit the current availability of binary decoders and external system commands.")
            
            # Checking pytesseract binary
            try:
                pytesseract.get_tesseract_version()
                tess_status = "🟢 AVAILABLE (Version loaded)"
                tess_color = "green"
            except Exception:
                tess_status = "🟡 UNAVAILABLE (Active Heuristics Fallback Triggered)"
                tess_color = "orange"
                
            # Checking ffprobe / ffmpeg binary
            try:
                import subprocess
                import shutil
                ffmpeg_executable = shutil.which(FFMPEG_PATH) or shutil.which("ffmpeg")
                if not ffmpeg_executable:
                    raise FileNotFoundError("FFmpeg binary not found")
                proc = subprocess.run([ffmpeg_executable, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
                ffmpeg_status = "🟢 AVAILABLE"
                ffmpeg_color = "green"
            except Exception:
                ffmpeg_status = "🟡 UNAVAILABLE (Active Binary Container Parser Triggered)"
                ffmpeg_color = "orange"
                
            st.markdown(
                f"""
                <div style='background-color:#02070e; border:1px solid #1a3c6e; padding:15px; border-radius:6px;'>
                    <b>1. Tesseract OCR binary:</b> <span class='neon-text-{tess_color}'>{tess_status}</span><br>
                    • Subsystem: Screenshot text translation decoder<br>
                    • Heuristic status: Regex ASCII heuristics active.<br><br>
                    <b>2. FFmpeg / FFprobe bin:</b> <span class='neon-text-{ffmpeg_color}'>{ffmpeg_status}</span><br>
                    • Subsystem: Video codec extraction and frame properties<br>
                    • Heuristic status: Custom MP4 binary box header parser active.<br><br>
                    <b>3. Machine Learning Classification:</b> <span class='neon-text-green'>🟢 ACTIVE</span><br>
                    • Subsystem: Term density category and severity evaluator<br>
                    • Model type: scikit-learn TF-IDF / Custom Regex weight dictionary
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
