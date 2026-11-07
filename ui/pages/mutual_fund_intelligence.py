"""Institutional Mutual Fund Research & Risk Engine Workspace."""
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from services.mutual_fund_service import MutualFundService
from src.analytics.risk_engine import FinancialRiskEngine
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_mutual_fund_intelligence():
    """Renders the comprehensive mutual fund performance and risk analysis workspace."""
    st.markdown("## 💼 Mutual Fund Intelligence & Risk Engine")
    st.caption("Official AMFI NAV Ingestion · Institutional Risk Profiling · Comparative Drawdown Engine")

    summary_df = MutualFundService.get_all_funds_summary()
    if summary_df.empty:
        st.warning("No Mutual Fund NAV data available in warehouse. Run AMFI ingestion to populate.")
        return

    # Benchmark Methodology Card
    st.markdown("""
    <div style="background: #111A26; border: 1px solid #253346; border-radius: 4px; padding: 10px 16px; margin-bottom: 14px; font-size: 0.82rem;">
        <span style="color: #45A3FF; font-weight: 700;">BENCHMARK ASSUMPTIONS:</span>
        Risk-Free Rate: <b style="color: #F5B942;">6.50%</b> (Indian 10-Year Sovereign G-Sec / RBI Repo Benchmark) · 
        Annualization Factor: <b style="color: #E6EDF5;">252 Trading Days</b> · 
        Downside Risk Threshold: <b style="color: #E6EDF5;">0.00%</b> (Sortino Minimum Acceptable Return)
    </div>
    """, unsafe_allow_html=True)

    # Multi-Fund Selection Toolbar
    fund_codes = summary_df["scheme_code"].tolist()
    fund_names = {row["scheme_code"]: f"{row['scheme_name']} ({row['category']})" for _, row in summary_df.iterrows()}
    
    selected_codes = st.multiselect(
        "Select Funds for Comparison",
        options=fund_codes,
        default=fund_codes[:min(4, len(fund_codes))],
        format_func=lambda c: fund_names.get(c, c),
    )

    if not selected_codes:
        st.info("Select at least one mutual fund to display trajectory curves.")
        return

    # 1. Comparative Rebased NAV Chart
    st.markdown("### 📈 Relative NAV Trajectory (Rebased to ₹100.00)")
    fig_comp = go.Figure()

    for code in selected_codes:
        ts = MutualFundService.get_fund_timeseries(code)
        if not ts.empty:
            base_val = ts["nav"].iloc[0]
            rebased_series = (ts["nav"] / base_val) * 100.0
            label = fund_names.get(code, code).split("-")[0].strip()
            fig_comp.add_trace(go.Scatter(x=ts["nav_date"], y=rebased_series, name=label, mode="lines", line=dict(width=2)))

    comp_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
    comp_layout["height"] = 420
    comp_layout["yaxis_title"] = "Normalized NAV (Base = 100)"
    fig_comp.update_layout(comp_layout)
    st.plotly_chart(fig_comp, use_container_width=True)

    # 2. Drawdown Underwater Profile
    st.markdown("### 📉 Peak-to-Trough Drawdown Curves (Underwater View)")
    fig_dd = go.Figure()
    risk_calc = FinancialRiskEngine()

    for code in selected_codes:
        ts = MutualFundService.get_fund_timeseries(code)
        if not ts.empty:
            _, dd_series = risk_calc.calculate_drawdown_series(ts["nav"])
            label = fund_names.get(code, code).split("-")[0].strip()
            fig_dd.add_trace(go.Scatter(
                x=ts["nav_date"],
                y=dd_series * 100.0,
                name=label,
                fill="tozeroy",
                mode="lines",
                line=dict(width=1.5),
            ))

    dd_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
    dd_layout["height"] = 320
    dd_layout["yaxis_title"] = "Drawdown % from Peak"
    fig_dd.update_layout(dd_layout)
    st.plotly_chart(fig_dd, use_container_width=True)

    # 3. Institutional Risk-Adjusted Scorecard Table
    st.markdown("### 🛡️ Institutional Risk-Adjusted Scorecard")
    matched_summary = summary_df[summary_df["scheme_code"].isin(selected_codes)].copy()
    
    cols_display = [
        "scheme_code", "scheme_name", "category", "latest_nav",
        "nav_high_52w", "nav_low_52w", "cagr_pct", "volatility_pct",
        "sharpe_ratio", "sortino_ratio", "max_drawdown_pct", "calmar_ratio"
    ]
    st.dataframe(
        matched_summary[cols_display].style.format({
            "latest_nav": "₹{:.2f}",
            "nav_high_52w": "₹{:.2f}",
            "nav_low_52w": "₹{:.2f}",
            "cagr_pct": "{:+.2f}%",
            "volatility_pct": "{:.2f}%",
            "sharpe_ratio": "{:.2f}",
            "sortino_ratio": "{:.2f}",
            "max_drawdown_pct": "{:.2f}%",
            "calmar_ratio": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
