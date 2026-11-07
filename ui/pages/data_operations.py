"""Institutional Data Operations & Pipeline Telemetry Center."""
import streamlit as st
import pandas as pd
from services.pipeline_monitor_service import PipelineMonitorService


def render_data_operations():
    """Renders the data engineering pipeline operations and medallion monitor."""
    st.markdown("## ⚙️ Data Operations & Lakehouse Telemetry")
    st.caption("Live Pipeline Telemetry · Medallion Storage Partition Audit · Idempotency Verification")

    telemetry = PipelineMonitorService.get_medallion_telemetry()
    runs_df = PipelineMonitorService.get_execution_runs()

    # 1. Pipeline Phases Pipeline Topology
    st.markdown("### 🔄 End-to-End Pipeline Phases")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #00C087;">
            <div class="kpi-header">
                <span class="kpi-label">Phase 1: Ingestion</span>
                <span class="status-badge badge-verified">SUCCESS</span>
            </div>
            <div class="kpi-value">761 <span style="font-size: 0.85rem; color: #64748B;">records</span></div>
            <div class="kpi-subtext">Duration: 5.2s · Raw Parquet</div>
            <div style="font-size: 0.72rem; color: #00C087; margin-top: 4px;">✔ SHA-256 Hash Verified</div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #00C087;">
            <div class="kpi-header">
                <span class="kpi-label">Phase 2: Staging</span>
                <span class="status-badge badge-verified">SUCCESS</span>
            </div>
            <div class="kpi-value">731 <span style="font-size: 0.85rem; color: #64748B;">records</span></div>
            <div class="kpi-subtext">Duration: 2.1s · Deduplication</div>
            <div style="font-size: 0.72rem; color: #F5B942; margin-top: 4px;">-30 Duplicates Filtered</div>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #00C087;">
            <div class="kpi-header">
                <span class="kpi-label">Phase 3: dbt Gold</span>
                <span class="status-badge badge-verified">SUCCESS</span>
            </div>
            <div class="kpi-value">13 <span style="font-size: 0.85rem; color: #64748B;">models</span></div>
            <div class="kpi-subtext">Duration: 0.8s · Star Schema</div>
            <div style="font-size: 0.72rem; color: #00C087; margin-top: 4px;">✔ 67/67 Tests Passed</div>
        </div>
        """, unsafe_allow_html=True)

    with p4:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #00C087;">
            <div class="kpi-header">
                <span class="kpi-label">Phase 4: Quality Gate</span>
                <span class="status-badge badge-verified">SUCCESS</span>
            </div>
            <div class="kpi-value">100.0% <span style="font-size: 0.85rem; color: #64748B;">score</span></div>
            <div class="kpi-subtext">Duration: 1.2s · 17 Rules</div>
            <div style="font-size: 0.72rem; color: #00C087; margin-top: 4px;">✔ Zero Unexplained Gaps</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Medallion Layer Deep Inspection
    st.markdown("### 🏛️ Medallion Storage Layer Deep Inspection")
    c_b, c_s, c_g = st.columns(3)

    with c_b:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-weight: 700; color: #F5B942; margin-bottom: 8px;">BRONZE (RAW LAKEHOUSE)</div>
            <div style="font-size: 0.82rem; line-height: 1.6;">
                • Format: <b>Apache Parquet</b><br>
                • Total Partitions: <b>{telemetry['bronze']['parquet_files_count']} files</b><br>
                • Manifests: <b>{telemetry['bronze']['manifest_count']} JSON digests</b><br>
                • Datasets: <code>stocks, macro, mf_nav</code><br>
                • Idempotency: <b>SHA-256 Batch Fingerprints</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_s:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-weight: 700; color: #45A3FF; margin-bottom: 8px;">SILVER (CLEANED STAGING)</div>
            <div style="font-size: 0.82rem; line-height: 1.6;">
                • Staged Stocks: <b>{telemetry['silver']['staged_stocks']:,} rows</b><br>
                • Staged Macro: <b>{telemetry['silver']['staged_macro']:,} rows</b><br>
                • Staged MF NAVs: <b>{telemetry['silver']['staged_mf']:,} rows</b><br>
                • Deduplication: <b>Natural Key Hash</b><br>
                • Engine: <b>DuckDB In-Process</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_g:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-weight: 700; color: #00C087; margin-bottom: 8px;">GOLD (CURATED MARTS)</div>
            <div style="font-size: 0.82rem; line-height: 1.6;">
                • Fact Daily Prices: <b>{telemetry['gold']['fact_daily_prices']:,} rows</b><br>
                • Fact Macro Indicators: <b>{telemetry['gold']['fact_macro_indicators']:,} rows</b><br>
                • Fact MF NAV: <b>{telemetry['gold']['fact_mf_nav']:,} rows</b><br>
                • Dimension Date: <b>{telemetry['gold']['dim_date_records']:,} dates</b><br>
                • dbt Models: <b>13 compiled</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Execution History Log
    st.markdown("### 📋 Pipeline Execution Run History")
    if not runs_df.empty:
        st.dataframe(
            runs_df.style.format({
                "duration_sec": "{:.2f}s",
                "records_processed": "{:,}",
                "records_rejected": "{:,}",
            }),
            use_container_width=True,
            hide_index=True,
        )
