"""Risk Analytics Service: Cross-asset risk-return frontier and correlation matrix."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client
from src.analytics.risk_engine import FinancialRiskEngine


class RiskAnalyticsService:
    """Computes cross-asset risk profiles, correlation matrices, and drawdown series."""

    @staticmethod
    def get_cross_asset_risk_profiles() -> pd.DataFrame:
        """Profiles all equities, indices, and mutual funds for risk vs return mapping."""
        engine = FinancialRiskEngine(risk_free_rate=0.065)

        # 1. Equities and Indices
        df_stocks = db_client.query("""
            SELECT p.symbol, s.company_name, s.security_type, p.trade_date, p.close_price
            FROM main_marts.fact_daily_prices p
            JOIN main_marts.dim_security s ON p.security_id = s.security_id
            ORDER BY p.symbol, p.trade_date ASC
        """)

        # 2. Mutual Funds
        df_funds = db_client.query("""
            SELECT f.scheme_code as symbol, f.scheme_name as company_name, 'Mutual Fund' as security_type, f.nav_date as trade_date, f.nav as close_price
            FROM main_marts.fact_mf_nav f
            ORDER BY f.scheme_code, f.nav_date ASC
        """)

        combined = pd.concat([df_stocks, df_funds], ignore_index=True)
        rows = []

        for sym in combined["symbol"].unique():
            sub = combined[combined["symbol"] == sym].sort_values("trade_date").reset_index(drop=True)
            if len(sub) < 5:
                continue
            meta = sub.iloc[-1]
            stats = engine.profile_asset_series(sub, price_col="close_price", date_col="trade_date")
            rows.append({
                "symbol": sym,
                "asset_name": meta["company_name"],
                "asset_type": meta["security_type"],
                "cagr_pct": stats["cagr_pct"],
                "volatility_pct": stats["volatility_pct"],
                "sharpe_ratio": stats["sharpe_ratio"],
                "sortino_ratio": stats["sortino_ratio"],
                "max_drawdown_pct": stats["max_drawdown_pct"],
                "calmar_ratio": stats["calmar_ratio"],
            })

        return pd.DataFrame(rows)

    @staticmethod
    def get_correlation_matrix(symbols: List[str]) -> pd.DataFrame:
        """Computes daily returns correlation matrix across selected securities."""
        if not symbols:
            return pd.DataFrame()

        # Query daily returns
        sym_list_str = "', '".join(symbols)
        df_rets = db_client.query(f"""
            SELECT symbol, trade_date, daily_return_pct
            FROM main_marts.fact_daily_prices
            WHERE symbol IN ('{sym_list_str}')
            ORDER BY trade_date ASC
        """)

        if df_rets.empty:
            return pd.DataFrame()

        pivot = df_rets.pivot(index="trade_date", columns="symbol", values="daily_return_pct")
        return pivot.corr().round(2)
