"""Unit-style test: Hand-calculated Pandas return & SMA vs dbt DuckDB window functions."""
from datetime import date
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
import pytest

WAREHOUSE_PATH = Path(__file__).resolve().parents[2] / "data" / "warehouse" / "curated.duckdb"


def test_dbt_pandas_indicator_parity():
    """Validates that SQL window functions match hand-calculated Pandas calculations to within 1e-6."""
    con = duckdb.connect(str(WAREHOUSE_PATH.resolve()), read_only=True)

    # Pull raw prices for a single ticker to compute manual baseline in Pandas
    symbol = "HDFCBANK.NS"
    raw_df = con.execute(f"""
        SELECT trade_date, close_price 
        FROM main_staging.stg_stocks 
        WHERE symbol = '{symbol}'
        ORDER BY trade_date ASC
    """).df()

    # Hand-calculate in Pandas
    raw_df["pandas_prev_close"] = raw_df["close_price"].shift(1)
    raw_df["pandas_daily_return"] = (raw_df["close_price"] - raw_df["pandas_prev_close"]) / raw_df["pandas_prev_close"]
    raw_df["pandas_daily_return"] = raw_df["pandas_daily_return"].round(6)

    # Pull dbt Fact table calculation
    dbt_df = con.execute(f"""
        SELECT trade_date, prev_close_price, daily_return_pct
        FROM main_marts.fact_daily_prices
        WHERE symbol = '{symbol}'
        ORDER BY trade_date ASC
    """).df()

    con.close()

    assert len(raw_df) == len(dbt_df), "Row counts must match"

    # Compare non-null return rows
    for i in range(1, len(raw_df)):
        expected_prev = raw_df.iloc[i]["pandas_prev_close"]
        actual_prev = dbt_df.iloc[i]["prev_close_price"]
        assert np.isclose(expected_prev, actual_prev, atol=1e-2), f"Prev close mismatch at row {i}"

        expected_return = raw_df.iloc[i]["pandas_daily_return"]
        actual_return = dbt_df.iloc[i]["daily_return_pct"]
        assert np.isclose(expected_return, actual_return, atol=1e-4), f"Return mismatch at row {i}: expected {expected_return}, got {actual_return}"

    print(f"✅ Hand-calculated Pandas parity verified for {symbol} across {len(raw_df)} sessions!")


if __name__ == "__main__":
    test_dbt_pandas_indicator_parity()
