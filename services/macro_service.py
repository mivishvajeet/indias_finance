"""Macroeconomic Intelligence Service: RBI, MOSPI, and FX analytics."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client


class MacroIntelligenceService:
    """Provides macroeconomic indicator analysis and cross-asset correlation from Gold marts."""

    @staticmethod
    def get_macro_summary() -> List[Dict[str, Any]]:
        """Fetches the latest and prior observation for each active macro indicator."""
        df = db_client.query("""
            WITH ranked AS (
                SELECT 
                    indicator_code,
                    observation_date,
                    indicator_value,
                    frequency,
                    unit_of_measure,
                    data_source,
                    LAG(indicator_value, 1) OVER (PARTITION BY indicator_code ORDER BY observation_date ASC) as prev_val,
                    ROW_NUMBER() OVER (PARTITION BY indicator_code ORDER BY observation_date DESC) as rn
                FROM main_marts.fact_macro_indicators
            )
            SELECT * FROM ranked WHERE rn = 1
            ORDER BY indicator_code ASC
        """)

        cards = []
        for _, r in df.iterrows():
            curr = r["indicator_value"]
            prev = r["prev_val"] if pd.notnull(r["prev_val"]) else curr
            change = curr - prev
            cards.append({
                "code": r["indicator_code"],
                "latest_value": curr,
                "previous_value": prev,
                "change": change,
                "frequency": r["frequency"],
                "unit": r["unit_of_measure"],
                "source": r["data_source"],
                "observation_date": str(r["observation_date"]),
            })
        return cards

    @staticmethod
    def get_indicator_history(code: str) -> pd.DataFrame:
        """Fetches historical time-series for a specific indicator code."""
        return db_client.query(f"""
            SELECT observation_date, indicator_value
            FROM main_marts.fact_macro_indicators
            WHERE indicator_code = '{code}'
            ORDER BY observation_date ASC
        """)
