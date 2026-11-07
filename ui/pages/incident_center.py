"""Institutional Data Incident Management & Lineage Fault Investigation."""
import streamlit as st
import pandas as pd
from data_access.repositories.incident_repository import IncidentRepository
from services.incident_service import IncidentService


def render_incident_center():
    """Renders the data reliability incident workspace with interactive lifecycle controls."""
    st.markdown("## 🚨 Data Incident Center & Reliability Management")
    st.caption("Active Failure Management · Lineage Impact Blast-Radius · Investigation Workflow")

    metrics = IncidentService.get_incident_metrics()
    incidents_df = IncidentRepository.get_all_incidents()

    # 1. Top Incident Telemetry
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Open Incidents</div>
            <div class="kpi-value" style="color: {'#FF5C65' if metrics['open'] > 0 else '#00C087'};">{metrics['open']}</div>
            <div class="kpi-subtext">Requires active triage</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Critical Breaches</div>
            <div class="kpi-value" style="color: {'#FF5C65' if metrics['critical'] > 0 else '#00C087'};">{metrics['critical']}</div>
            <div class="kpi-subtext">Tripped circuit breakers</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Resolved Incidents</div>
            <div class="kpi-value" style="color: #00C087;">{metrics['resolved']}</div>
            <div class="kpi-subtext">Remediated & archived</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Incident History</div>
            <div class="kpi-value">{metrics['total']}</div>
            <div class="kpi-subtext">Total lifecycle records</div>
        </div>
        """, unsafe_allow_html=True)

    if incidents_df.empty:
        st.info("No incidents detected. All pipeline and lakehouse operations are fully healthy.")
        return

    # 2. Incident Selection & Triage
    st.markdown("### 🔍 Active Incident Investigation & Triage")
    inc_options = [f"{row['incident_id']} — {row['title']} [{row['severity']}]" for _, row in incidents_df.iterrows()]
    selected_option = st.selectbox("Select Incident Record", inc_options, index=0)
    selected_id = selected_option.split(" — ")[0].strip()

    inc = incidents_df[incidents_df["incident_id"] == selected_id].iloc[0]

    # Severity & Status Badge
    sev_badge = {
        "CRITICAL": '<span class="status-badge badge-critical">CRITICAL</span>',
        "HIGH": '<span class="status-badge badge-critical">HIGH</span>',
        "MEDIUM": '<span class="status-badge badge-warning">MEDIUM</span>',
        "LOW": '<span class="status-badge badge-neutral">LOW</span>',
        "RESOLVED": '<span class="status-badge badge-verified">RESOLVED</span>',
    }.get(inc["severity"], '<span class="status-badge badge-neutral">INFO</span>')

    status_badge = {
        "DETECTED": '<span class="status-badge badge-critical">DETECTED</span>',
        "ACKNOWLEDGED": '<span class="status-badge badge-warning">ACKNOWLEDGED</span>',
        "INVESTIGATING": '<span class="status-badge badge-warning">INVESTIGATING</span>',
        "RESOLVED": '<span class="status-badge badge-verified">RESOLVED</span>',
    }.get(inc["lifecycle_status"], '<span class="status-badge badge-neutral">UNKNOWN</span>')

    st.markdown(f"""
    <div style="background: #111A26; border: 1px solid #253346; border-radius: 4px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">{inc['title']}</span>
                <span style="margin-left: 10px;">{sev_badge}</span>
                <span style="margin-left: 6px;">{status_badge}</span>
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #91A0B3;">
                Detected: {inc['detection_timestamp']}
            </div>
        </div>
        <div style="font-size: 0.85rem; color: #E6EDF5; margin-bottom: 8px;">
            {inc['failure_description']}
        </div>
        <div style="font-size: 0.8rem; color: #91A0B3;">
            Affected Asset: <code>{inc['affected_table']}</code> · Source: <code>{inc['source_component']}</code> · Test: <code>{inc['related_failed_tests']}</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Lineage Blast-Radius Impact Analysis
    st.markdown("### 💥 Lineage Impact & Upstream Root-Cause Tracing")
    blast = IncidentService.get_blast_radius(inc["affected_table"])
    
    col_root, col_target, col_impact = st.columns(3)
    with col_root:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #F5B942;">
            <div class="kpi-label">Upstream Dependencies</div>
            <div style="font-size: 0.85rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">
                {', '.join([f'<code>{u}</code>' for u in blast['upstream_sources']])}
            </div>
            <div class="kpi-subtext">Potential root cause sources</div>
        </div>
        """, unsafe_allow_html=True)

    with col_target:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #FF5C65;">
            <div class="kpi-label">Failing Target Asset</div>
            <div style="font-size: 0.85rem; color: #FF5C65; font-weight: 700; margin-top: 4px;">
                <code>{inc['affected_table']}</code>
            </div>
            <div class="kpi-subtext">Direct point of assertion failure</div>
        </div>
        """, unsafe_allow_html=True)

    with col_impact:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #45A3FF;">
            <div class="kpi-label">Impacted Downstream Systems</div>
            <div style="font-size: 0.82rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">
                {', '.join([f'<code>{d}</code>' for d in blast['downstream_impact'][:4]])}
            </div>
            <div class="kpi-subtext">Dashboards & feature stores at risk</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Interactive State Transition Actions
    st.markdown("### 🛠️ Incident Remediation & Workflow Actions")
    col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
    
    with col_act1:
        if st.button("👁️ Acknowledge Incident", disabled=(inc["lifecycle_status"] != "DETECTED")):
            IncidentRepository.update_incident_status(selected_id, "ACKNOWLEDGED", "Incident acknowledged by engineer.")
            st.success("Incident moved to ACKNOWLEDGED.")
            st.rerun()

    with col_act2:
        if st.button("🔬 Start Investigating", disabled=(inc["lifecycle_status"] == "INVESTIGATING" or inc["lifecycle_status"] == "RESOLVED")):
            IncidentRepository.update_incident_status(selected_id, "INVESTIGATING", "Active investigation initiated.")
            st.success("Incident moved to INVESTIGATING.")
            st.rerun()

    with col_act3:
        with st.popover("✅ Mark as Resolved"):
            res_notes = st.text_input("Resolution Notes", value="Remediated upstream pipeline and verified tests.")
            if st.button("Confirm Resolution"):
                IncidentRepository.update_incident_status(selected_id, "RESOLVED", res_notes)
                st.success("Incident successfully marked as RESOLVED.")
                st.rerun()

    # 5. Full Incident History Table
    st.markdown("### 📜 Persisted Incident Audit History")
    disp_cols = ["incident_id", "title", "severity", "lifecycle_status", "affected_table", "detection_timestamp", "resolved_at"]
    st.dataframe(incidents_df[disp_cols], use_container_width=True, hide_index=True)
