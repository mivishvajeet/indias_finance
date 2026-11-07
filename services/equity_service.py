"""Equity Screener Service: Multi-factor screening and technical filtering on Gold marts."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client


class EquityScreenerService:
    """Executes multi-factor filtering over latest trading session metrics in fact_daily_prices."""

    @staticmethod
    def get_screenable_universe() -> pd.DataFrame:
        """Fetches the latest trading session snapshot for all tracked securities."""
        df = db_client.query("""
            WITH ranked AS (
                SELECT 
                    p.symbol,
                    s.company_name,
                    s.security_type,
                    s.sector_name,
                    p.trade_date,
                    p.close_price,
                    p.daily_return_pct,
                    p.rsi_14,
                    p.sma_20,
                    p.sma_50,
                    p.sma_200,
                    p.ema_12,
                    p.ema_26,
                    p.macd_line,
                    p.macd_signal_line,
                    p.macd_histogram,
                    p.high_52w,
                    p.low_52w,
                    p.bollinger_upper,
                    p.bollinger_lower,
                    p.volume,
                    p.avg_prior_20_volume,
                    ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
            )
            SELECT * EXCLUDE (rn)
            FROM ranked
            WHERE rn = 1
            ORDER BY symbol ASC
        """)
        return df

    @classmethod
    def apply_filters(
        cls,
        df: pd.DataFrame,
        symbol_query: str = "",
        sector: str = "ALL",
        min_price: float = 0.0,
        max_price: float = 1_000_000.0,
        rsi_min: float = 0.0,
        rsi_max: float = 100.0,
        above_sma20: Optional[bool] = None,
        above_sma50: Optional[bool] = None,
        macd_bullish: Optional[bool] = None,
        within_52w_high_pct: Optional[float] = None,
    ) -> pd.DataFrame:
        """Applies financial & technical filters deterministically."""
        filtered = df.copy()

        # Symbol / Company Search
        if symbol_query:
            q = symbol_query.upper().strip()
            filtered = filtered[
                filtered["symbol"].str.contains(q, case=False, na=False) |
                filtered["company_name"].str.contains(q, case=False, na=False)
            ]

        # Sector Filter
        if sector and sector != "ALL":
            filtered = filtered[filtered["sector_name"] == sector]

        # Price Range
        filtered = filtered[(filtered["close_price"] >= min_price) & (filtered["close_price"] <= max_price)]

        # RSI Range
        if "rsi_14" in filtered.columns:
            filtered = filtered[(filtered["rsi_14"].fillna(50.0) >= rsi_min) & (filtered["rsi_14"].fillna(50.0) <= rsi_max)]

        # SMA Crossovers
        if above_sma20 is True:
            filtered = filtered[filtered["close_price"] > filtered["sma_20"]]
        elif above_sma20 is False:
            filtered = filtered[filtered["close_price"] < filtered["sma_20"]]

        if above_sma50 is True:
            filtered = filtered[filtered["close_price"] > filtered["sma_50"]]
        elif above_sma50 is False:
            filtered = filtered[filtered["close_price"] < filtered["sma_50"]]

        # MACD Signal
        if macd_bullish is True:
            filtered = filtered[filtered["macd_line"] > filtered["macd_signal_line"]]
        elif macd_bullish is False:
            filtered = filtered[filtered["macd_line"] < filtered["macd_signal_line"]]

        # 52-Week High Proximity
        if within_52w_high_pct is not None and within_52w_high_pct > 0:
            threshold = 1.0 - (within_52w_high_pct / 100.0)
            filtered = filtered[(filtered["close_price"] >= filtered["high_52w"] * threshold) & (filtered["high_52w"] > 0)]

        return filtered
