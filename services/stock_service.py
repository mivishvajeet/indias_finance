"""Stock Analytics Service: In-depth technical research and quantitative asset profiling."""
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from data_access.duckdb_client import db_client
from src.analytics.risk_engine import FinancialRiskEngine


class StockAnalyticsService:
    """Provides deep-dive quantitative profiling and technical observations for individual securities."""

    @staticmethod
    def get_security_profile(symbol: str) -> Dict[str, Any]:
        """Fetches full historical time-series and profile for a specific symbol."""
        df = db_client.query(f"""
            SELECT 
                p.*,
                s.company_name,
                s.isin,
                s.sector_name,
                s.industry_name,
                s.security_type
            FROM main_marts.fact_daily_prices p
            JOIN main_marts.dim_security s ON p.security_id = s.security_id
            WHERE p.symbol = '{symbol}'
            ORDER BY p.trade_date ASC
        """)

        if df.empty:
            return {}

        latest = df.iloc[-1]
        risk_engine = FinancialRiskEngine(risk_free_rate=0.065)
        risk_profile = risk_engine.profile_asset_series(df, price_col="close_price", date_col="trade_date")

        # Deterministic Technical Observations
        observations = []
        
        # 1. Moving Average Alignment
        if pd.notnull(latest.get("sma_20")) and pd.notnull(latest.get("sma_50")):
            if latest["close_price"] > latest["sma_20"] > latest["sma_50"]:
                observations.append("🟢 **Bullish Alignment**: Price is trading above both 20-Day and 50-Day SMAs with positive moving average slope.")
            elif latest["close_price"] < latest["sma_20"] < latest["sma_50"]:
                observations.append("🔴 **Bearish Alignment**: Price is trading below both 20-Day and 50-Day SMAs with negative moving average slope.")

        # 2. RSI 14 Regime
        rsi = latest.get("rsi_14")
        if pd.notnull(rsi):
            if rsi > 70:
                observations.append(f"⚠️ **RSI Overbought ({rsi:.1f})**: Momentum indicator suggests extended upward price stretch.")
            elif rsi < 30:
                observations.append(f"🟢 **RSI Oversold ({rsi:.1f})**: Momentum indicator suggests deep price discount relative to recent window.")
            else:
                observations.append(f"⚖️ **RSI Neutral ({rsi:.1f})**: Momentum is balanced within standard 30-70 channel.")

        # 3. MACD Momentum
        if pd.notnull(latest.get("macd_line")) and pd.notnull(latest.get("macd_signal_line")):
            if latest["macd_line"] > latest["macd_signal_line"]:
                observations.append("🟢 **MACD Bullish**: Fast MACD line is above the 9-day signal trigger line.")
            else:
                observations.append("🔴 **MACD Bearish**: Fast MACD line is below the 9-day signal trigger line.")

        # 4. Bollinger Band Location
        if pd.notnull(latest.get("bollinger_upper")) and pd.notnull(latest.get("bollinger_lower")):
            if latest["close_price"] >= latest["bollinger_upper"]:
                observations.append("⚡ **Bollinger Upper Band Pierced**: Closing price is testing or exceeding +2σ volatility band.")
            elif latest["close_price"] <= latest["bollinger_lower"]:
                observations.append("⚡ **Bollinger Lower Band Pierced**: Closing price is testing or piercing -2σ volatility band.")

        # 5. Volume Spike
        if latest.get("is_volume_spike"):
            vol_ratio = (latest["volume"] / latest["avg_prior_20_volume"]) if latest["avg_prior_20_volume"] > 0 else 1.0
            observations.append(f"🚨 **Volume Spike**: Traded volume is {vol_ratio:.1f}x higher than the 20-day baseline.")

        return {
            "metadata": {
                "symbol": symbol,
                "company_name": latest["company_name"],
                "sector": latest["sector_name"],
                "industry": latest["industry_name"],
                "isin": latest["isin"],
                "security_type": latest["security_type"],
            },
            "latest_bar": latest.to_dict(),
            "history": df,
            "risk_profile": risk_profile,
            "observations": observations,
        }
