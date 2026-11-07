"""Institutional Risk Analytics & Cross-Asset Frontier Workspace."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from services.risk_service import RiskAnalyticsService
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_risk_analytics():
    """Renders the institutional risk-return and asset correlation workspace."""
    st.markdown("## ⚖️ Financial Risk & Quantitative Performance Engine")
    st.caption("Sharpe & Sortino Ratios · Maximum Drawdown · Cross-Asset Correlation Matrix · Risk Frontiers")

    profiles_df = RiskAnalyticsService.get_cross_asset_risk_profiles()
    if profiles_df.empty:
        st.warning("Insufficient pricing history in warehouse to construct risk profiles.")
        return

    # 1. Risk-Return Scatter Plot
    st.markdown("### 🎯 Cross-Asset Risk vs. Return Frontier")
    fig_scatter = px.scatter(
        profiles_df,
        x="volatility_pct",
        y="cagr_pct",
        color="asset_type",
        size=profiles_df["sharpe_ratio"].clip(lower=0.5, upper=5.0),
        hover_name="asset_name",
        text="symbol",
        labels={
            "volatility_pct": "Annualized Volatility (%) [Risk]",
            "cagr_pct": "CAGR (%) [Return]",
            "asset_type": "Asset Class",
        },
        color_discrete_map={
            "Index": "#A78BFA",
            "Equity": "#45A3FF",
            "Mutual Fund": "#00C087",
        },
    )
    scat_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
    scat_layout["height"] = 460
    fig_scatter.update_layout(scat_layout)
    fig_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 2. Correlation Matrix
    st.markdown("### 🔗 Multi-Asset Return Correlation Heatmap")
    all_syms = sorted(profiles_df[profiles_df["asset_type"] != "Mutual Fund"]["symbol"].tolist())
    default_syms = all_syms[:min(6, len(all_syms))]

    corr_syms = st.multiselect("Select Assets for Correlation", options=all_syms, default=default_syms)
    if len(corr_syms) >= 2:
        corr_matrix = RiskAnalyticsService.get_correlation_matrix(corr_syms)
        if not corr_matrix.empty:
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale="Blues",
                zmin=-1.0, zmax=1.0,
                text=corr_matrix.values,
                texttemplate="%{text:.2f}",
                showscale=True,
            ))
            c_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
            c_layout["height"] = 380
            fig_corr.update_layout(c_layout)
            st.plotly_chart(fig_corr, use_container_width=True)

    # 3. Comprehensive Risk Scorecard
    st.markdown("### 📋 Institutional Risk Profile Table")
    st.dataframe(
        profiles_df.style.format({
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
