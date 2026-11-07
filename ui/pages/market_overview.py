"""Institutional Indian Stock Market Overview Module."""
import plotly.graph_objects as go
import streamlit as st
from services.market_service import MarketService
from data_access.duckdb_client import db_client
from ui.components.theme import PLOTLY_LAYOUT_TEMPLATE


def render_market_overview():
    """Renders the institutional market overview workspace."""
    st.markdown("## 📊 Indian Capital Markets Overview")
    st.caption("Benchmark Performance · Market Breadth · Sector Rotation · Institutional Insights")

    snapshot = MarketService.get_market_snapshot()
    indices = snapshot["indices"]
    breadth = snapshot["breadth"]

    # 1. Benchmark Snapshot Row
    st.markdown("### 🏛️ Benchmark Indices")
    cols = st.columns(len(indices) if indices else 1)
    for i, (name, d) in enumerate(indices.items()):
        with cols[i]:
            val_col = "#00C087" if d["change_pct"] >= 0 else "#FF5C65"
            sign = "+" if d["change_pct"] >= 0 else ""
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-label">{name}</span>
                    <span class="status-badge badge-neutral">{d['symbol']}</span>
                </div>
                <div class="kpi-value">₹{d['close']:,.2f}</div>
                <div class="kpi-subtext" style="color: {val_col}; font-weight: 600;">
                    {sign}{d['change']:,.2f} ({sign}{d['change_pct']:.2f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Market Breadth & Telemetry
    st.markdown("### ⚖️ Market Breadth & Session Telemetry")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Advancing Securities</div>
            <div class="kpi-value" style="color: #00C087;">{breadth['advancers']}</div>
            <div class="kpi-subtext">Equities in positive territory</div>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Declining Securities</div>
            <div class="kpi-value" style="color: #FF5C65;">{breadth['decliners']}</div>
            <div class="kpi-subtext">Equities in negative territory</div>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Advance / Decline Ratio</div>
            <div class="kpi-value">{breadth['advance_decline_ratio']:.2f}</div>
            <div class="kpi-subtext">Ratio of Gainers to Losers</div>
        </div>
        """, unsafe_allow_html=True)
    with b4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Tracked Securities</div>
            <div class="kpi-value">{breadth['total_tracked']}</div>
            <div class="kpi-subtext">Active universe in Gold Marts</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Interactive Benchmark Chart
    st.markdown("### 📈 Index Performance Trajectory")
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        selected_index = st.selectbox("Select Index", list(indices.keys()), index=0)
    with col_c2:
        timeframe = st.radio("Window", ["1M", "3M", "ALL"], horizontal=True, index=1)

    index_symbol = indices[selected_index]["symbol"]
    idx_df = db_client.query(f"""
        SELECT trade_date, open_price, high_price, low_price, close_price, volume, sma_20, sma_50
        FROM main_marts.fact_daily_prices
        WHERE symbol = '{index_symbol}'
        ORDER BY trade_date ASC
    """)

    if not idx_df.empty:
        if timeframe == "1M":
            idx_df = idx_df.tail(22)
        elif timeframe == "3M":
            idx_df = idx_df.tail(66)

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=idx_df["trade_date"],
            open=idx_df["open_price"],
            high=idx_df["high_price"],
            low=idx_df["low_price"],
            close=idx_df["close_price"],
            name="OHLC Bar",
            increasing_line_color="#00C087",
            decreasing_line_color="#FF5C65",
        ))
        if "sma_20" in idx_df.columns:
            fig.add_trace(go.Scatter(x=idx_df["trade_date"], y=idx_df["sma_20"], name="SMA 20", line=dict(color="#F5B942", width=1.5)))
        if "sma_50" in idx_df.columns:
            fig.add_trace(go.Scatter(x=idx_df["trade_date"], y=idx_df["sma_50"], name="SMA 50", line=dict(color="#45A3FF", width=1.5)))

        layout = dict(PLOTLY_LAYOUT_TEMPLATE)
        layout["height"] = 420
        layout["xaxis"] = dict(layout["xaxis"], rangeslider_visible=False)
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

    # 4. Market Movers & Sector Intelligence
    m_col1, m_col2 = st.columns(2)
    movers = MarketService.get_market_movers(limit=5)
    with m_col1:
        st.markdown("### 🟢 Top Gainers")
        gainers_df = movers["gainers"][["symbol", "company_name", "sector_name", "close_price", "daily_return_pct", "volume"]].copy()
        gainers_df["daily_return_pct"] = gainers_df["daily_return_pct"] * 100
        st.dataframe(
            gainers_df.style.format({
                "close_price": "₹{:.2f}",
                "daily_return_pct": "+{:.2f}%",
                "volume": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with m_col2:
        st.markdown("### 🔴 Top Losers")
        losers_df = movers["losers"][["symbol", "company_name", "sector_name", "close_price", "daily_return_pct", "volume"]].copy()
        losers_df["daily_return_pct"] = losers_df["daily_return_pct"] * 100
        st.dataframe(
            losers_df.style.format({
                "close_price": "₹{:.2f}",
                "daily_return_pct": "{:.2f}%",
                "volume": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # 5. Sector Performance Matrix
    st.markdown("### 🌐 Sector Intelligence")
    sec_df = MarketService.get_sector_performance()
    if not sec_df.empty:
        st.dataframe(
            sec_df.style.format({
                "avg_return_pct": "{:+.2f}%",
                "total_volume": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # 6. Deterministic Market Observations
    st.markdown("### 🧠 Deterministic Technical Observations")
    insights = MarketService.get_market_insights()
    for ins in insights:
        st.markdown(f"- {ins}")

    st.caption("ℹ️ *Notice: Observations are generated deterministically from actual Gold marts data for educational and research purposes. Does not constitute investment advice.*")
