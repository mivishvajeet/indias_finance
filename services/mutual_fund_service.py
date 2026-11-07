"""Mutual Fund Service: Performance analysis, risk profiling, and comparative NAV indexing."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client
from src.analytics.risk_engine import FinancialRiskEngine


class MutualFundService:
    """Provides mutual fund intelligence and comparative risk-adjusted performance metrics."""

    @staticmethod
    def get_fund_directory() -> pd.DataFrame:
        """Fetches all tracked funds and AMC families from dim_fund."""
        return db_client.query("""
            SELECT fund_id, scheme_code, scheme_name, fund_family, scheme_category
            FROM main_marts.dim_fund
            ORDER BY fund_family, scheme_name
        """)

    @staticmethod
    def get_all_funds_summary() -> pd.DataFrame:
        """Calculates institutional risk metrics for all active mutual funds in Gold marts."""
        df_nav = db_client.query("""
            SELECT 
                f.scheme_code,
                f.scheme_name,
                d.fund_family,
                d.scheme_category,
                f.nav_date,
                f.nav,
                f.nav_high_52w,
                f.nav_low_52w,
                f.daily_return_pct
            FROM main_marts.fact_mf_nav f
            LEFT JOIN main_marts.dim_fund d ON f.fund_id = d.fund_id
            ORDER BY f.scheme_code, f.nav_date ASC
        """)

        if df_nav.empty:
            return pd.DataFrame()

        engine = FinancialRiskEngine(risk_free_rate=0.065)
        funds = df_nav["scheme_code"].unique()
        rows = []

        for code in funds:
            sub = df_nav[df_nav["scheme_code"] == code].sort_values("nav_date").reset_index(drop=True)
            if len(sub) < 5:
                continue
            stats = engine.profile_asset_series(sub, price_col="nav", date_col="nav_date")
            latest = sub.iloc[-1]
            rows.append({
                "scheme_code": code,
                "scheme_name": latest["scheme_name"],
                "fund_family": latest["fund_family"],
                "category": latest["scheme_category"],
                "latest_nav": latest["nav"],
                "nav_high_52w": latest["nav_high_52w"],
                "nav_low_52w": latest["nav_low_52w"],
                "cagr_pct": stats["cagr_pct"],
                "volatility_pct": stats["volatility_pct"],
                "sharpe_ratio": stats["sharpe_ratio"],
                "sortino_ratio": stats["sortino_ratio"],
                "max_drawdown_pct": stats["max_drawdown_pct"],
                "calmar_ratio": stats["calmar_ratio"],
            })

        return pd.DataFrame(rows)

    @staticmethod
    def get_fund_timeseries(scheme_code: str) -> pd.DataFrame:
        """Fetches historical daily NAVs for a specific scheme code."""
        return db_client.query(f"""
            SELECT nav_date, nav, daily_return_pct, nav_high_52w, nav_low_52w
            FROM main_marts.fact_mf_nav
            WHERE scheme_code = '{scheme_code}'
            ORDER BY nav_date ASC
        """)
