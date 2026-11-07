"""Visual Data Lineage Explorer & dbt Dependency DAG."""
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from services.lineage_service import DataLineageService
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_data_lineage():
    """Renders the interactive end-to-end data lineage DAG."""
    st.markdown("## 🕸️ Data Lineage Explorer & Dependency DAG")
    st.caption("Visual End-to-End Asset Provenance: Bronze Raw ➔ Silver Staging ➔ Gold Marts ➔ Dashboards")

    lineage = DataLineageService.get_lineage_graph()
    nodes = lineage["nodes"]
    coords = lineage["coords"]
    edges = lineage["edges"]

    # Layer Color Legend Ribbon
    st.markdown("""
    <div style="display: flex; gap: 14px; margin-bottom: 14px; font-size: 0.8rem; font-weight: 600;">
        <span style="color: #F5B942;">● BRONZE (RAW LAKEHOUSE)</span>
        <span style="color: #45A3FF;">● SILVER (STAGING VIEWS)</span>
        <span style="color: #A78BFA;">● INTERMEDIATE (SQL TECHNICALS)</span>
        <span style="color: #00C087;">● GOLD (STAR SCHEMA MARTS)</span>
        <span style="color: #E6EDF5;">● SERVING (ANALYTICS ENGINES)</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Interactive Plotly Lineage DAG Graph
    fig = go.Figure()

    # Draw Directed Edge Lines
    for src, tgt in edges:
        if src in coords and tgt in coords:
            x0, y0 = coords[src]
            x1, y1 = coords[tgt]
            fig.add_trace(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(color="#253346", width=1.5),
                hoverinfo="none",
                showlegend=False,
            ))

    # Draw Nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_hover = []

    for name, (x, y) in coords.items():
        node_x.append(x)
        node_y.append(y)
        node_text.append(name)
        n_info = nodes.get(name, {})
        node_color.append(n_info.get("color", "#45A3FF"))
        node_hover.append(f"<b>{name}</b><br>Layer: {n_info.get('layer')}<br>Records: {n_info.get('records')}<br>Materialization: {n_info.get('materialization')}")

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(size=28, color=node_color, line=dict(color="#080C12", width=2)),
        text=[f"  {t}" for t in node_text],
        textposition="middle right",
        textfont=dict(family="JetBrains Mono", size=10, color="#E6EDF5"),
        hovertext=node_hover,
        hoverinfo="text",
        showlegend=False,
    ))

    layout = dict(PLOTLY_LAYOUT_TEMPLATE)
    layout["height"] = 520
    layout["xaxis"] = dict(
        showgrid=False, zeroline=False, showticklabels=True,
        tickvals=[0, 1, 2, 3, 4],
        ticktext=["1. BRONZE", "2. SILVER", "3. INTERMEDIATE", "4. GOLD MARTS", "5. SERVING"],
        tickfont=dict(color="#91A0B3", size=11, family="Inter"),
    )
    layout["yaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False)
    layout["margin"] = dict(l=20, r=140, t=20, b=20)
    fig.update_layout(layout)
    st.plotly_chart(fig, use_container_width=True)

    # 2. Interactive Node Metadata Inspector
    st.markdown("### 🔍 Node Inspector & Schema Governance")
    selected_node = st.selectbox("Inspect Asset Details", list(nodes.keys()), index=list(nodes.keys()).index("fact_daily_prices"))
    
    n_data = nodes[selected_node]
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)

    with col_i1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Asset Layer</div>
            <div class="kpi-value" style="color: {n_data['color']};">{n_data['layer']}</div>
            <div class="kpi-subtext">Schema: <code>{n_data['schema']}</code></div>
        </div>
        """, unsafe_allow_html=True)

    with col_i2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Materialization</div>
            <div class="kpi-value">{n_data['materialization']}</div>
            <div class="kpi-subtext">Engine: DuckDB / Parquet</div>
        </div>
        """, unsafe_allow_html=True)

    with col_i3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Curated Record Count</div>
            <div class="kpi-value">{n_data['records'] if isinstance(n_data['records'], str) else f"{n_data['records']:,}"}</div>
            <div class="kpi-subtext">Dynamic warehouse count</div>
        </div>
        """, unsafe_allow_html=True)

    with col_i4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Dependencies</div>
            <div class="kpi-value">{len(n_data['upstreams'])} in / {len(n_data['downstreams'])} out</div>
            <div class="kpi-subtext">Direct DAG edges</div>
        </div>
        """, unsafe_allow_html=True)

    col_up, col_down = st.columns(2)
    with col_up:
        st.markdown("#### ⬅️ Upstream Provenance Sources")
        if n_data["upstreams"]:
            for u in n_data["upstreams"]:
                st.markdown(f"- <code>{u}</code> *(Layer: {nodes[u]['layer']})*")
        else:
            st.info("Primary ingestion root (Zero upstream dependencies).")

    with col_down:
        st.markdown("#### ➡️ Downstream Consumers")
        if n_data["downstreams"]:
            for d in n_data["downstreams"]:
                st.markdown(f"- <code>{d}</code> *(Layer: {nodes[d]['layer']})*")
        else:
            st.info("Terminal serving endpoint (Zero downstream dependencies).")
