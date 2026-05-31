"""
FAFO Lawyer Portal & Forensics Verification Panel
Provides a read-only dashboard for legal counsel to download zip packages and verify hashes.
"""
import os
import streamlit as st
from pathlib import Path
from modules import incident_manager
from modules import hashing
from modules import export_manager
from modules import utils
from modules import audit_logger

def render_lawyer_dashboard():
    """Renders the restricted, read-only Lawyer Forensic Panel."""
    st.markdown(
        """
        <div style='display:flex; align-items:center; margin-bottom:20px;'>
            <h1 class='neon-text-cyan' style='margin:0;'>🏛️ LEGAL COUNSEL FORENSIC AUDIT PORTAL</h1>
        </div>
        <p style='color:#a2b0c4;'>
            Authorized Read-Only access to cryptographically validated incident case records for judicial preparation and review.
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    # 1. Load approved cases only
    user = st.session_state["user"]
    approved_cases = incident_manager.get_all_incidents(role_name="lawyer")
    
    if not approved_cases:
        st.markdown(
            """
            <div style='border:1px dashed #1a3c6e; padding:30px; text-align:center; color:#64748b; border-radius:12px;'>
                ⚖️ No authorized forensic cases are currently registered for legal review.<br>
                <span style='font-size:0.85rem;'>Incidents must be marked as 'Approved' by a Reviewer to appear in this panel.</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        return
        
    # Case selector drop-down
    case_options = {f"[{c['incident_key']}] {c['title']}": c for c in approved_cases}
    selected_option = st.selectbox("Select Certified Case File for Review:", list(case_options.keys()))
    
    if not selected_option:
        return
        
    case = case_options[selected_option]
    incident_id = case["id"]
    incident_key = case["incident_key"]
    
    # Reload fresh nested case metadata
    meta = export_manager.build_incident_metadata(incident_id)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Layout with Case Details and Verification Console
    col1, col2 = st.columns([5, 4])
    
    with col1:
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3>📂 Case File: {meta['incident_key']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<b>Title:</b> {meta['title']}", unsafe_allow_html=True)
        st.markdown(f"<b>Preservation Category:</b> <code class='mono-text'>{meta['category']}</code>", unsafe_allow_html=True)
        st.markdown(f"<b>Preserved At:</b> {utils.format_timestamp(meta['created_at'])}", unsafe_allow_html=True)
        st.markdown(f"<b>Custodian Submitter:</b> {meta['submitter']['name']} ({meta['submitter']['email']})", unsafe_allow_html=True)
        
        st.markdown("<h4 style='margin-top:15px; color:#00e5ff;'>📝 Incident Narrative Description:</h4>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background-color:#02070e; border:1px solid #1a3c6e; padding:12px; border-radius:6px; font-size:0.9rem; color:#d2d6dc; line-height:1.5;'>"
            f"{meta['description']}"
            f"</div>", 
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Evidence inventory card
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3>📦 Registered Evidence Inventory ({len(meta['evidence'])} items)</h3>", unsafe_allow_html=True)
        
        for idx, ev in enumerate(meta['evidence'], 1):
            st.markdown(f"<b>Item #{idx}: {ev['original_filename']}</b>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-family:monospace; font-size:0.8rem; color:#94a3b8; padding-left:15px; margin-bottom:12px;'>"
                f"• System Name: {ev['filename']}<br>"
                f"• MIME-Type: {ev['mime_type']}<br>"
                f"• File Size: {utils.human_readable_size(ev['file_size_bytes'])}<br>"
                f"• Uploaded By: {ev['uploaded_by']} at {utils.format_timestamp(ev['uploaded_at'])}<br>"
                f"• <span style='color:#00e5ff;'>SHA-256 Fingerprint: {ev['sha256_hash']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # Embed image if screenshot or media preview
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
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🛡️ CRYPTOGRAPHIC VERIFICATION PANEL</h3>", unsafe_allow_html=True)
        st.markdown(
            "Recalculate cryptographic hash fingerprints of all preserved assets on disk and cross-check against "
            "the original secure evidence manifest to guarantee zero file tampering."
        )
        
        # Trigger verification check
        verify_btn = st.button("RUN DEEP INTEGRITY CHECKSUM")
        
        # By default show a placeholder or results
        if verify_btn:
            # Audit log search action
            audit_logger.log_action(
                user=user,
                action="evidence_verify",
                resource_type="incident",
                resource_id=incident_id,
                details=f"Ran cryptographic integrity checksum verification on incident {incident_key}",
                ip_address=audit_logger.get_streamlit_ip()
            )
            
            with st.spinner("Executing mathematical integrity check on disk..."):
                report = hashing.verify_incident_integrity(incident_key)
                
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            
            if report["is_valid"]:
                st.markdown(
                    f"""
                    <div class='crypto-verify-box crypto-valid'>
                        <h4 style='margin:0 0 5px 0; color:#39ff14;'>✓ VAULT INTEGRITY SECURED</h4>
                        <b>Message:</b> {report['message']}<br>
                        • Registered Assets: {report['registered_count']}<br>
                        • Disk Check Match: {report['current_count']} files verified
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                status_color = "#ff3860" if report["status"] in ["TAMPERED", "CORRUPT_MANIFEST"] else "#ff9f1c"
                st.markdown(
                    f"""
                    <div class='crypto-verify-box crypto-invalid'>
                        <h4 style='margin:0 0 5px 0; color:{status_color};'>🚨 VAULT INTEGRITY COMPROMISED</h4>
                        <b>Status:</b> {report['status']}<br>
                        <b>Warning Message:</b> {report['message']}<br>
                        • Registered Assets: {report['registered_count']}<br>
                        • Current on Disk: {report['current_count']}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                if report["tampered_files"]:
                    st.markdown("<b style='color:#ff3860; font-size:0.85rem;'>Tampered Files List:</b>", unsafe_allow_html=True)
                    for tf in report["tampered_files"]:
                        st.markdown(
                            f"<div style='font-family:monospace; font-size:0.75rem; color:#ff3860; padding-left:10px; margin-bottom:8px; border-left: 2px solid #ff3860;'>"
                            f"File: {tf['file']}<br>"
                            f"Expected: {tf['expected'][:15]}...<br>"
                            f"Actual:   {tf['actual'][:15]}..."
                            f"</div>",
                            unsafe_allow_html=True
                        )
                if report["missing_files"]:
                    st.markdown("<b style='color:#ff9f1c; font-size:0.85rem;'>Missing Files List:</b>", unsafe_allow_html=True)
                    for mf in report["missing_files"]:
                        st.markdown(f"<code style='color:#ff9f1c; font-size:0.75rem;'>• {mf}</code>", unsafe_allow_html=True)
                        
                if report["untracked_files"]:
                    st.markdown("<b style='color:#ff9f1c; font-size:0.85rem;'>Untracked Files List (Added without signature):</b>", unsafe_allow_html=True)
                    for uf in report["untracked_files"]:
                        st.markdown(f"<code style='color:#ff9f1c; font-size:0.75rem;'>• {uf}</code>", unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <div style='background-color:#03080e; border:1px solid #1a3c6e; padding:15px; text-align:center; border-radius:6px; color:#64748b; font-size:0.85rem; margin-top:15px;'>
                    Press button above to calculate mathematical digital signatures and confirm evidence chain-of-custody is completely untampered.
                </div>
                """, 
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Forensic Zip Export Card
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🏛️ FORENSIC VAULT PACKAGING</h3>", unsafe_allow_html=True)
        st.markdown(
            "Compile certified assets, mathematical hashes manifest, case database sheets, "
            "and cryptographic audit logs into a single forensic ZIP container for court filing."
        )
        
        # Generate and pack ZIP
        zip_btn = st.button("GENERATE FORENSIC ARCHIVE (.ZIP)")
        
        if zip_btn:
            with st.spinner("Assembling certified evidence package..."):
                zip_file_path = export_manager.generate_forensic_zip(incident_id)
                
            if zip_file_path and zip_file_path.exists():
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                st.success("✓ Forensic ZIP package successfully sealed and certified!")
                
                # Log export action
                audit_logger.log_action(
                    user=user,
                    action="export_create",
                    resource_type="incident",
                    resource_id=incident_id,
                    details=f"Generated and packaged certified ZIP forensic archive {zip_file_path.name}",
                    ip_address=audit_logger.get_streamlit_ip()
                )
                
                with open(zip_file_path, "rb") as f:
                    zip_data = f.read()
                    
                st.download_button(
                    label="DOWNLOAD FORENSIC PACKAGE (.ZIP)",
                    data=zip_data,
                    file_name=zip_file_path.name,
                    mime="application/zip",
                    help="Click here to download the certified ZIP archive to your local device"
                )
            else:
                st.error("Packaging Failed: Could not compile files or manifest.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show chain of custody list on screen
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📜 Certified Chain of Custody Audit Trail</h3>", unsafe_allow_html=True)
        
        for idx, log in enumerate(meta["audit_logs"], 1):
            st.markdown(
                f"<div style='font-size:0.8rem; margin-bottom:10px; border-bottom:1px solid #1a3c6e; padding-bottom:5px; color:#b2becf;'>"
                f"<b>{idx}. {log['action'].upper()}</b><br>"
                f"<span style='color:#64748b; font-size:0.75rem;'>"
                f"Actor: {log['username']} ({log['role']}) | IP: {log['ip_address']}<br>"
                f"Time: {utils.format_timestamp(log['timestamp'])}<br>"
                f"Details: {log['details']}"
                f"</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
