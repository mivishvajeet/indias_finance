"""NSE Equity Screener Workspace."""
import streamlit as st
import pandas as pd
from services.equity_service import EquityScreenerService


def render_equity_screener():
    """Renders the interactive NSE equity screener workspace."""
    st.markdown("## 🔍 NSE Equity Screener Workspace")
    st.caption("Multi-Factor Technical & Quantitative Screening · Real Gold Marts Data")

    universe_df = EquityScreenerService.get_screenable_universe()
    if universe_df.empty:
        st.warning("No equity data available in warehouse.")
        return

    # Filter Toolbar
    with st.expander("⚙️ Screening Parameters & Factor Filters", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            sym_search = st.text_input("Search Symbol / Name", placeholder="e.g. RELIANCE, TCS")
        with c2:
            sectors = ["ALL"] + sorted([s for s in universe_df["sector_name"].dropna().unique()])
            sel_sector = st.selectbox("Sector Classification", sectors, index=0)
        with c3:
            rsi_filter = st.selectbox("RSI (14-Day) Condition", ["Any", "Oversold (< 35)", "Neutral (35 - 65)", "Overbought (> 65)"])
        with c4:
            sma_trend = st.selectbox("Trend (Moving Averages)", ["Any", "Above 20-Day SMA", "Below 20-Day SMA", "Above 50-Day SMA"])

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            macd_choice = st.selectbox("MACD Signal", ["Any", "Bullish (MACD > Signal)", "Bearish (MACD < Signal)"])
        with c6:
            high_52w_prox = st.selectbox("52-Week High Proximity", ["Any", "Within 3% of 52W High", "Within 5% of 52W High", "Within 10% of 52W High"])
        with c7:
            min_p, max_p = float(universe_df["close_price"].min()), float(universe_df["close_price"].max())
            price_range = st.slider("Closing Price Range (₹)", min_value=0.0, max_value=max(10000.0, max_p), value=(min_p, max_p))
        with c8:
            sec_type = st.selectbox("Asset Class", ["All", "Equities Only", "Indices Only"])

    # Parse filter choices
    rsi_min, rsi_max = 0.0, 100.0
    if rsi_filter == "Oversold (< 35)":
        rsi_max = 35.0
    elif rsi_filter == "Neutral (35 - 65)":
        rsi_min, rsi_max = 35.0, 65.0
    elif rsi_filter == "Overbought (> 65)":
        rsi_min = 65.0

    above_sma20 = True if sma_trend == "Above 20-Day SMA" else (False if sma_trend == "Below 20-Day SMA" else None)
    above_sma50 = True if sma_trend == "Above 50-Day SMA" else None
    macd_bullish = True if macd_choice == "Bullish (MACD > Signal)" else (False if macd_choice == "Bearish (MACD < Signal)" else None)

    prox_pct = None
    if high_52w_prox == "Within 3% of 52W High":
        prox_pct = 3.0
    elif high_52w_prox == "Within 5% of 52W High":
        prox_pct = 5.0
    elif high_52w_prox == "Within 10% of 52W High":
        prox_pct = 10.0

    # Apply Filters
    filtered_df = EquityScreenerService.apply_filters(
        universe_df,
        symbol_query=sym_search,
        sector=sel_sector,
        min_price=price_range[0],
        max_price=price_range[1],
        rsi_min=rsi_min,
        rsi_max=rsi_max,
        above_sma20=above_sma20,
        above_sma50=above_sma50,
        macd_bullish=macd_bullish,
        within_52w_high_pct=prox_pct,
    )

    if sec_type == "Equities Only":
        filtered_df = filtered_df[filtered_df["security_type"] != "Index"]
    elif sec_type == "Indices Only":
        filtered_df = filtered_df[filtered_df["security_type"] == "Index"]

    # Results Header & Metrics
    st.markdown(f"### 📋 Screener Matches: **{len(filtered_df)}** of {len(universe_df)} tracked securities")

    # Display Table
    cols_to_show = [
        "symbol", "company_name", "sector_name", "close_price",
        "daily_return_pct", "rsi_14", "sma_20", "sma_50", "macd_line",
        "high_52w", "low_52w", "volume"
    ]
    disp_df = filtered_df[cols_to_show].copy()
    disp_df["daily_return_pct"] = disp_df["daily_return_pct"] * 100

    st.dataframe(
        disp_df.style.format({
            "close_price": "₹{:.2f}",
            "daily_return_pct": "{:+.2f}%",
            "rsi_14": "{:.1f}",
            "sma_20": "₹{:.2f}",
            "sma_50": "₹{:.2f}",
            "macd_line": "{:.2f}",
            "high_52w": "₹{:.2f}",
            "low_52w": "₹{:.2f}",
            "volume": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Actions: Export & Selection
    col_e1, col_e2 = st.columns([1, 4])
    with col_e1:
        csv_data = disp_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Matches to CSV",
            data=csv_data,
            file_name="nse_screener_results.csv",
            mime="text/csv",
        )
    with col_e2:
        st.caption("💡 *Tip: Switch to the 'Stock Analytics' tab in the left sidebar to perform a deep-dive research inspection on any matched security.*")
