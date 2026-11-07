"""Macroeconomic Intelligence Workspace: RBI Monetary Policy & FX."""
import plotly.graph_objects as go
import streamlit as st
from services.macro_service import MacroIntelligenceService
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_macro_intelligence():
    """Renders the macroeconomic observatory module."""
    st.markdown("## 🏛️ Macroeconomic Intelligence & Monetary Policy")
    st.caption("Official RBI Monetary Indicators · MOSPI Price Indices · USD / INR Exchange Trajectory")

    indicators = MacroIntelligenceService.get_macro_summary()
    if not indicators:
        st.warning("No macroeconomic indicator series available in warehouse.")
        return

    # 1. Macro Summary Cards
    st.markdown("### 📊 Key Macroeconomic Observations")
    cols = st.columns(len(indicators))
    for i, ind in enumerate(indicators):
        with cols[i]:
            val_col = "#00C087" if ind["change"] >= 0 else "#FF5C65"
            sign = "+" if ind["change"] >= 0 else ""
            unit_suffix = "%" if ind["unit"] == "percentage" else (" ₹/USD" if "USD" in ind["code"] else "")
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-label">{ind['code']}</span>
                    <span class="status-badge badge-neutral">{ind['source']}</span>
                </div>
                <div class="kpi-value">{ind['latest_value']:.2f}{unit_suffix}</div>
                <div class="kpi-subtext" style="color: {val_col}; font-weight: 600;">
                    {sign}{ind['change']:.2f} vs prior ({ind['frequency']})
                </div>
                <div style="font-size: 0.72rem; color: #64748B; margin-top: 4px;">
                    Date: {ind['observation_date']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Historical Charts
    st.markdown("### 📈 Indicator Historical Trajectories")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### USD / INR Daily Currency Exchange Rate")
        usd_df = MacroIntelligenceService.get_indicator_history("USD_INR")
        if not usd_df.empty:
            fig_usd = go.Figure()
            fig_usd.add_trace(go.Scatter(
                x=usd_df["observation_date"],
                y=usd_df["indicator_value"],
                name="USD/INR",
                line=dict(color="#00C087", width=2),
            ))
            u_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
            u_layout["height"] = 350
            u_layout["yaxis_title"] = "INR per USD"
            fig_usd.update_layout(u_layout)
            st.plotly_chart(fig_usd, use_container_width=True)

    with c2:
        st.markdown("#### RBI Monetary Policy Repo Rate (%)")
        repo_df = MacroIntelligenceService.get_indicator_history("REPO_RATE")
        if not repo_df.empty:
            fig_repo = go.Figure()
            fig_repo.add_trace(go.Scatter(
                x=repo_df["observation_date"],
                y=repo_df["indicator_value"],
                name="Repo Rate",
                line=dict(color="#F5B942", width=2),
            ))
            r_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
            r_layout["height"] = 350
            r_layout["yaxis_title"] = "Repo Rate %"
            fig_repo.update_layout(r_layout)
            st.plotly_chart(fig_repo, use_container_width=True)
