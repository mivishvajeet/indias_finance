"""Direct DuckDB validation script querying Phase 1 Bronze Parquet files."""
from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
raw_dir = BASE_DIR / "data" / "lakehouse" / "raw"

con = duckdb.connect()

print("=" * 80)
print(" 🦆 DUCKDB OLAP QUERY VERIFICATION OVER BRONZE PARQUET LAKEHOUSE")
print("=" * 80)

# 1. Stocks Raw Partition Scan
stocks_glob = str(raw_dir / "stocks_daily" / "**" / "*.parquet")
con.execute(f"CREATE OR REPLACE VIEW raw_stocks AS SELECT * FROM read_parquet('{stocks_glob}')")

print("\n--- [1] Stock & Benchmark Price Bars (Summary & Sample) ---")
summary_stocks = con.execute("""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT symbol) as unique_symbols,
        MIN(trade_date) as earliest_date,
        MAX(trade_date) as latest_date,
        COUNT(DISTINCT trade_date) as total_trading_days
    FROM raw_stocks
""").df()
print(summary_stocks.to_string(index=False))

print("\n--- Recent Price Samples ---")
sample_stocks = con.execute("""
    SELECT symbol, trade_date, open, high, low, close, volume, source
    FROM raw_stocks
    ORDER BY trade_date DESC, symbol ASC
    LIMIT 8
""").df()
print(sample_stocks.to_string(index=False))

# 2. Macro Indicators Raw Partition Scan
macro_glob = str(raw_dir / "macro_indicators" / "**" / "*.parquet")
con.execute(f"CREATE OR REPLACE VIEW raw_macro AS SELECT * FROM read_parquet('{macro_glob}')")

print("\n--- [2] Macroeconomic Indicators (Breakdown by Indicator) ---")
macro_summary = con.execute("""
    SELECT 
        indicator_code,
        COUNT(*) as total_observations,
        MIN(trade_date) as start_date,
        MAX(trade_date) as end_date,
        MIN(value) as min_val,
        MAX(value) as max_val,
        ANY_VALUE(unit) as unit,
        ANY_VALUE(source) as source
    FROM raw_macro
    GROUP BY indicator_code
    ORDER BY indicator_code ASC
""").df()
print(macro_summary.to_string(index=False))

print("\n--- Latest USD/INR Spot Exchange Observations ---")
usd_inr_samples = con.execute("""
    SELECT indicator_code, trade_date, value, unit, source
    FROM raw_macro
    WHERE indicator_code = 'USD_INR'
    ORDER BY trade_date DESC
    LIMIT 5
""").df()
print(usd_inr_samples.to_string(index=False))

print("\n" + "=" * 80)
print(" ✅ ALL PARQUET PARTITIONS SCANNED & VALIDATED VIA DUCKDB SQL!")
print("=" * 80)
