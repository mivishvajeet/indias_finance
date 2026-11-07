"""Institutional Stock Research & Technical Analytics Workspace."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
from services.stock_service import StockAnalyticsService
from data_access.duckdb_client import db_client
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_stock_analytics():
    """Renders the in-depth stock research and quantitative analysis module."""
    st.markdown("## 📈 Equity Analytics & Technical Terminal")
    st.caption("Deep Quantitative Research · Multi-Timeframe Candlestick Overlays · Risk Profiles")

    # Fetch available symbols
    symbols_df = db_client.query("SELECT symbol, company_name FROM main_marts.dim_security ORDER BY symbol ASC")
    if symbols_df.empty:
        st.warning("No security metadata available in warehouse.")
        return

    symbol_options = [f"{row['symbol']} — {row['company_name']}" for _, row in symbols_df.iterrows()]
    
    col_sel, col_toggles = st.columns([2, 2])
    with col_sel:
        selected_option = st.selectbox("Select Security for Analysis", symbol_options, index=0)
        selected_symbol = selected_option.split(" — ")[0].strip()

    with col_toggles:
        c1, c2 = st.columns(2)
        with c1:
            overlay_ma = st.multiselect("Moving Averages", ["SMA 20", "SMA 50", "SMA 200"], default=["SMA 20", "SMA 50"])
        with c2:
            show_bb = st.checkbox("Bollinger Bands (20, 2σ)", value=True)

    profile = StockAnalyticsService.get_security_profile(selected_symbol)
    if not profile:
        st.warning(f"No pricing history available for {selected_symbol}")
        return

    meta = profile["metadata"]
    latest = profile["latest_bar"]
    history = profile["history"]
    risk = profile["risk_profile"]

    # Company Header Banner
    st.markdown(f"""
    <div style="background: #111A26; border: 1px solid #253346; border-radius: 4px; padding: 12px 18px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">{meta['company_name']}</span>
                <span style="font-family: 'JetBrains Mono'; font-weight: 700; color: #45A3FF; margin-left: 10px;">{meta['symbol']}</span>
                <div style="font-size: 0.78rem; color: #91A0B3; margin-top: 2px;">
                    Sector: <b>{meta['sector']}</b> · Industry: <b>{meta['industry']}</b> · ISIN: <b>{meta['isin']}</b>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.6rem; font-weight: 700; font-family: 'JetBrains Mono'; color: #FFFFFF;">
                    ₹{latest['close_price']:,.2f}
                </div>
                <div style="font-size: 0.85rem; font-weight: 600; font-family: 'JetBrains Mono'; color: {'#00C087' if (latest['daily_return_pct'] or 0) >= 0 else '#FF5C65'};">
                    {'+' if (latest['daily_return_pct'] or 0) >= 0 else ''}{(latest['daily_return_pct'] or 0)*100:.2f}% ({(latest['close_price'] - (latest['prev_close_price'] or latest['close_price'])):+,.2f})
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quantitative KPI Row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">52W High</div>
            <div class="kpi-value">₹{latest['high_52w']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">52W Low</div>
            <div class="kpi-value">₹{latest['low_52w']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Ann. Volatility</div>
            <div class="kpi-value">{risk['volatility_pct']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Max Drawdown</div>
            <div class="kpi-value" style="color: #FF5C65;">{risk['max_drawdown_pct']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        rsi_val = latest.get("rsi_14") or 50.0
        rsi_col = "#FF5C65" if rsi_val > 70 else ("#00C087" if rsi_val < 30 else "#45A3FF")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">RSI (14-Day)</div>
            <div class="kpi-value" style="color: {rsi_col};">{rsi_val:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    with k6:
        vol_ratio = (latest['volume'] / latest['avg_prior_20_volume']) if latest.get('avg_prior_20_volume', 0) > 0 else 1.0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Vol vs 20D Avg</div>
            <div class="kpi-value">{vol_ratio:.2f}x</div>
        </div>
        """, unsafe_allow_html=True)

    # 3-Tier Technical Plotly Subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{meta['symbol']} Price Action & Moving Averages", "RSI (14-Day Momentum)", "MACD (12, 26, 9)")
    )

    # 1. Candlestick
    fig.add_trace(
        go.Candlestick(
            x=history["trade_date"],
            open=history["open_price"],
            high=history["high_price"],
            low=history["low_price"],
            close=history["close_price"],
            name="OHLC",
            increasing_line_color="#00C087",
            decreasing_line_color="#FF5C65",
        ),
        row=1, col=1
    )

    if "SMA 20" in overlay_ma and "sma_20" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["sma_20"], name="SMA 20", line=dict(color="#F5B942", width=1.5)), row=1, col=1)
    if "SMA 50" in overlay_ma and "sma_50" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["sma_50"], name="SMA 50", line=dict(color="#45A3FF", width=1.5)), row=1, col=1)
    if "SMA 200" in overlay_ma and "sma_200" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["sma_200"], name="SMA 200", line=dict(color="#A78BFA", width=2)), row=1, col=1)

    if show_bb and "bollinger_upper" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["bollinger_upper"], name="BB Upper", line=dict(color="rgba(148, 163, 184, 0.4)", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["bollinger_lower"], name="BB Lower", fill="tonexty", fillcolor="rgba(148, 163, 184, 0.05)", line=dict(color="rgba(148, 163, 184, 0.4)", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["bollinger_middle"], name="BB Middle", line=dict(color="rgba(245, 185, 66, 0.6)", dash="dash", width=1)), row=1, col=1)

    # 2. RSI Subplot
    if "rsi_14" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["rsi_14"], name="RSI", line=dict(color="#45A3FF", width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#FF5C65", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#00C087", row=2, col=1)

    # 3. MACD Subplot
    if "macd_line" in history.columns and "macd_signal_line" in history.columns:
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["macd_line"], name="MACD", line=dict(color="#00C087", width=1.5)), row=3, col=1)
        fig.add_trace(go.Scatter(x=history["trade_date"], y=history["macd_signal_line"], name="Signal", line=dict(color="#F5B942", width=1.5)), row=3, col=1)
        hist_colors = ["#00C087" if v >= 0 else "#FF5C65" for v in history["macd_histogram"].fillna(0)]
        fig.add_trace(go.Bar(x=history["trade_date"], y=history["macd_histogram"], name="Hist", marker_color=hist_colors), row=3, col=1)

    layout = dict(PLOTLY_LAYOUT_TEMPLATE)
    layout["height"] = 780
    layout["xaxis"] = dict(layout["xaxis"], rangeslider_visible=False)
    fig.update_layout(layout)
    st.plotly_chart(fig, use_container_width=True)

    # Quantitative Return Distribution & Observations
    c_hist, c_obs = st.columns([1, 1])
    with c_hist:
        st.markdown("### 📊 Daily Returns Distribution")
        clean_rets = history["daily_return_pct"].dropna() * 100
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=clean_rets,
            nbinsx=30,
            marker_color="#45A3FF",
            opacity=0.8,
            name="Return Freq"
        ))
        dist_layout = dict(PLOTLY_LAYOUT_TEMPLATE)
        dist_layout["height"] = 300
        dist_layout["xaxis_title"] = "Daily Return %"
        dist_layout["yaxis_title"] = "Session Count"
        fig_dist.update_layout(dist_layout)
        st.plotly_chart(fig_dist, use_container_width=True)

    with c_obs:
        st.markdown("### 🧠 Technical Intelligence Observations")
        for obs in profile["observations"]:
            st.markdown(f"- {obs}")
        if not profile["observations"]:
            st.info("Technical indicators are within standard baseline thresholds.")
        st.caption("ℹ️ *Notice: Generated from deterministic Gold marts window functions for portfolio demonstration. Not financial advice.*")
