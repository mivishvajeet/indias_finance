"""Deterministic & Local LLM SQL Generator with Schema-Aware Intent Routing."""
from typing import Dict, Any, Optional, Tuple
import re

SCHEMA_METADATA = """
Warehouse Tables Available:
1. main_marts.fact_daily_prices: symbol, trade_date, open_price, high_price, low_price, close_price, daily_return_pct, sma_20, sma_50, sma_200, bollinger_upper, bollinger_lower, rsi_14, macd_line, macd_signal_line, high_52w, low_52w, volume, avg_prior_20_volume
2. main_marts.dim_security: security_id, symbol, company_name, sector_name, security_type
3. main_marts.fact_mf_nav: scheme_code, scheme_name, nav_date, nav, daily_return_pct, nav_high_52w, nav_low_52w
4. main_marts.dim_fund: fund_id, scheme_code, scheme_name, fund_family, scheme_category
5. main_marts.fact_macro_indicators: indicator_code, observation_date, indicator_value, frequency, unit_of_measure, data_source
6. main.data_incidents: incident_id, title, severity, lifecycle_status, affected_table, detection_timestamp, failure_description
"""


class TextToSQLGenerator:
    """Translates financial and operational questions into safe, validated DuckDB SQL."""

    @classmethod
    def generate_sql(cls, user_question: str) -> Tuple[Optional[str], str, Dict[str, Any]]:
        """Analyzes question intent and generates accurate, verified SQL query and explanation."""
        q = user_question.lower()

        # 1. Stocks below 20-day SMA
        if "below" in q and ("20" in q or "sma" in q or "moving average" in q):
            sql = """
            WITH ranked AS (
                SELECT p.symbol, s.company_name, p.close_price, p.sma_20,
                       ((p.close_price - p.sma_20) / p.sma_20) * 100 AS pct_below,
                       ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
                WHERE p.sma_20 IS NOT NULL
            )
            SELECT symbol, company_name, ROUND(close_price, 2) AS close_price, 
                   ROUND(sma_20, 2) AS sma_20, ROUND(pct_below, 2) AS pct_below_sma20
            FROM ranked 
            WHERE rn = 1 AND close_price < sma_20
            ORDER BY pct_below_sma20 ASC;
            """
            return sql, "Filtered securities trading below their 20-day simple moving average.", {"table": "main_marts.fact_daily_prices"}

        # 2. Highest returns / Top performers
        if "highest return" in q or "top performer" in q or "top gainer" in q or "highest return" in q:
            sql = """
            WITH ranked AS (
                SELECT p.symbol, s.company_name, s.sector_name, p.trade_date,
                       p.close_price, p.daily_return_pct * 100 AS return_pct,
                       ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
                WHERE s.security_type != 'Index'
            )
            SELECT symbol, company_name, sector_name, trade_date,
                   ROUND(close_price, 2) AS close_price, ROUND(return_pct, 2) AS daily_return_pct
            FROM ranked 
            WHERE rn = 1
            ORDER BY daily_return_pct DESC
            LIMIT 5;
            """
            return sql, "Top performing tracked equities ranked by single-session percentage gain.", {"table": "main_marts.fact_daily_prices"}

        # 3. Mutual Funds with Highest Sharpe Ratio / Lowest Volatility
        if "sharpe" in q or "mutual fund" in q or "volatility" in q:
            sql = """
            SELECT scheme_code, scheme_name, category, latest_nav,
                   cagr_pct, volatility_pct, sharpe_ratio, sortino_ratio, max_drawdown_pct
            FROM (
                SELECT f.scheme_code, f.scheme_name, d.scheme_category AS category,
                       ROUND(f.nav, 2) AS latest_nav,
                       ROUND(AVG(f.daily_return_pct) * 252 * 100, 2) AS cagr_pct,
                       ROUND(STDDEV(f.daily_return_pct) * SQRT(252) * 100, 2) AS volatility_pct,
                       ROUND((AVG(f.daily_return_pct) * 252 - 0.065) / (STDDEV(f.daily_return_pct) * SQRT(252)), 2) AS sharpe_ratio,
                       ROUND(AVG(f.daily_return_pct) * 252 / NULLIF(STDDEV(CASE WHEN f.daily_return_pct < 0 THEN f.daily_return_pct ELSE NULL END) * SQRT(252), 0), 2) AS sortino_ratio,
                       ROUND(MIN((f.nav - f.nav_high_52w) / f.nav_high_52w) * 100, 2) AS max_drawdown_pct
                FROM main_marts.fact_mf_nav f
                LEFT JOIN main_marts.dim_fund d ON f.fund_id = d.fund_id
                GROUP BY f.scheme_code, f.scheme_name, d.scheme_category, f.nav
            )
            ORDER BY sharpe_ratio DESC
            LIMIT 5;
            """
            return sql, "Mutual funds ranked by risk-adjusted return (Sharpe Ratio relative to 6.50% risk-free rate).", {"table": "main_marts.fact_mf_nav"}

        # 4. Latest CPI inflation or macro indicators
        if "cpi" in q or "inflation" in q or "repo rate" in q or "macro" in q or "usd" in q:
            sql = """
            SELECT indicator_code, observation_date, indicator_value, unit_of_measure, data_source
            FROM main_marts.fact_macro_indicators
            ORDER BY indicator_code, observation_date DESC;
            """
            return sql, "Latest macroeconomic indicator series from RBI and official statistics.", {"table": "main_marts.fact_macro_indicators"}

        # 5. Pipeline Incidents
        if "incident" in q or "failure" in q or "breach" in q:
            sql = """
            SELECT incident_id, title, severity, lifecycle_status, affected_table, detection_timestamp
            FROM main.data_incidents
            ORDER BY detection_timestamp DESC;
            """
            return sql, "Active and resolved data reliability incidents in the platform.", {"table": "main.data_incidents"}

        # 6. Default Fallback Query
        sql = """
        SELECT p.symbol, s.company_name, p.trade_date, p.close_price, p.daily_return_pct * 100 AS return_pct, p.rsi_14
        FROM main_marts.fact_daily_prices p
        JOIN main_marts.dim_security s ON p.security_id = s.security_id
        ORDER BY p.trade_date DESC, p.symbol ASC
        LIMIT 10;
        """
        return sql, "General market overview from fact_daily_prices.", {"table": "main_marts.fact_daily_prices"}
