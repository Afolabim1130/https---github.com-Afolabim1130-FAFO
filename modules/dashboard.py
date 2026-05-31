"""
FAFO Operations Dashboard Module
Renders advanced visual charts, incident KPI statistics, status metrics, and threat grids.
"""
import pandas as pd
import streamlit as st
from typing import List, Dict, Any
from modules import incident_manager
from modules import utils

def render_kpi_metrics(incidents: List[Dict[str, Any]]):
    """Draw a secure operations grid of glassmorphic KPI status widgets."""
    total_count = len(incidents)
    
    # Counter status variables
    submitted = sum(1 for i in incidents if i["status"] == "Submitted")
    reviewing = sum(1 for i in incidents if i["status"] == "Reviewing")
    approved = sum(1 for i in incidents if i["status"] == "Approved")
    
    # Calculate total evidence files size and file count
    total_files = 0
    total_bytes = 0
    
    # Try fetching evidence stats
    for inc in incidents:
        try:
            evs = incident_manager.get_evidence_by_incident(inc["id"])
            total_files += len(evs)
            total_bytes += sum(e["file_size_bytes"] or 0 for e in evs)
        except Exception:
            pass
            
    st.markdown("<h3 class='neon-text-cyan' style='margin-bottom: 15px;'>🛡️ INCIDENT RESPONSE & FORENSIC METRICS</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="Total Logged Cases", value=total_count, delta=None)
    with col2:
        st.metric(label="Pending Audits", value=submitted, delta=None, delta_color="inverse")
    with col3:
        st.metric(label="Under Active Review", value=reviewing, delta=None)
    with col4:
        st.metric(label="Authorized Evidence", value=approved, delta=None)
    with col5:
        st.metric(label="Preserved Artifacts", value=f"{total_files} files", delta=utils.human_readable_size(total_bytes))
        
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

def render_visualizations(incidents: List[Dict[str, Any]]):
    """Generates gorgeous data visualization widgets for categories and threat vectors."""
    if not incidents:
        st.info("No cases logged in system. Charts will populate once submissions are registered.")
        return
        
    df = pd.DataFrame(incidents)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h4>📊 Threat Severity Distribution</h4>", unsafe_allow_html=True)
        
        # Ensure all standard severities are present in order for consistent charting colors
        severity_order = ["Critical", "High", "Medium", "Low"]
        sev_counts = df["severity"].value_counts()
        
        # Sort counts by standard order
        sorted_counts = []
        sorted_labels = []
        for s in severity_order:
            if s in sev_counts:
                sorted_counts.append(sev_counts[s])
                sorted_labels.append(s)
                
        plot_df = pd.DataFrame({
            "Severity Level": sorted_labels,
            "Active Cases": sorted_counts
        })
        
        # Display as a horizontal bar chart
        st.bar_chart(plot_df.set_index("Severity Level"), color="#ff3860")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("<h4>📂 Forensic Category Incident Breakdown</h4>", unsafe_allow_html=True)
        
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Forensic Category", "Case Volume"]
        
        # Display as a vertical bar chart
        st.bar_chart(cat_counts.set_index("Forensic Category"), color="#00e5ff")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Chronological submission activity (Timeline plot)
    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
    st.markdown("<h4>📈 Chronological Evidence Submission Activity Log</h4>", unsafe_allow_html=True)
    
    # Format date to YYYY-MM-DD
    df["created_date"] = pd.to_datetime(df["created_at"]).dt.date
    timeline = df.groupby("created_date").size().reset_index(name="Daily Incidents")
    timeline.columns = ["Submission Date", "Case Submissions Count"]
    
    st.area_chart(timeline.set_index("Submission Date"), color="#7289da")
    st.markdown("</div>", unsafe_allow_html=True)

def render_recent_incidents_grid(incidents: List[Dict[str, Any]]):
    """Draw a highly readable cybersecurity layout showing incident case cards."""
    st.markdown("<h3 class='neon-text-orange'>📂 ACTIVE DIGITAL FORENSIC VAULT REPOSITORY</h3>", unsafe_allow_html=True)
    
    if not incidents:
        st.markdown(
            "<div style='border:1px dashed #1a3c6e; padding:20px; text-align:center; color:#64748b; border-radius:8px;'>"
            "Secure vault is empty. Submitter files will appear here chronologically."
            "</div>",
            unsafe_allow_html=True
        )
        return
        
    for inc in incidents:
        status = inc["status"]
        severity = inc["severity"]
        
        # Map class and glow color based on status/severity
        status_class = f"status-{status.lower()}"
        
        severity_color = "#39ff14" # Low
        if severity == "Critical":
            severity_color = "#ff3860"
        elif severity == "High":
            severity_color = "#ff9f1c"
        elif severity == "Medium":
            severity_color = "#2081E2"
            
        st.markdown(
            f"""
            <div class='cyber-card' style='margin-bottom:15px; padding:15px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                    <span class='mono-text neon-text-cyan' style='font-size:1.05rem; font-weight:bold;'>📂 {inc['incident_key']}</span>
                    <div>
                        <span class='status-pill {status_class}'>{status}</span>
                        <span style='margin-left: 8px; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; background-color:{severity_color}1a; color:{severity_color}; border:1px solid {severity_color}4d;'>{severity}</span>
                    </div>
                </div>
                <h4 style='margin:0 0 8px 0; color:#ffffff;'>{inc['title']}</h4>
                <p style='font-size:0.88rem; color:#94a3b8; margin:0 0 10px 0;'>{inc['description'][:180] + '...' if len(inc['description']) > 180 else inc['description']}</p>
                <div style='display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:#64748b;'>
                    <span>Custodian Actor: <b>{inc['submitter_name']}</b></span>
                    <span>Preserved: {utils.format_timestamp(inc['created_at'])}</span>
                    <span>Files: <b>{inc['file_count']} preserved</b></span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
