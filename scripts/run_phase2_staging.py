"""CLI Runner for Phase 2: Calendar Validation and Silver Staging Promotion into DuckDB."""
from datetime import date, timedelta
import logging
import sys
from pathlib import Path
import duckdb

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.quality.calendar_validator import CalendarValidator
from src.storage.lakehouse import LakehouseRawStorage
from src.storage.staging_manager import SilverStagingManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("phase2_runner")


def run_phase2():
    print("=" * 80)
    print(" 🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL — PHASE 2 STAGING & CALENDAR AUDIT")
    print("=" * 80)

    # 1. Trading Calendar Validation
    print("")
    print("--- [1/2] National Stock Exchange (NSE) Calendar Coverage Audit ---")
    raw_storage = LakehouseRawStorage()
    stocks_df = raw_storage.read_dataset("stocks_daily")

    validator = CalendarValidator()

    if not stocks_df.empty:
        actual_dates = set(stocks_df["trade_date"].unique())
        start_date = min(actual_dates)
        end_date = max(actual_dates)
        report = validator.audit_coverage(actual_dates, start_date, end_date)

        print(f"[*] Audit Date Window: {report.start_date} to {report.end_date} ({report.total_calendar_days} calendar days)")
        print(f"[+] Total Expected Trading Days: {report.expected_trading_days}")
        print(f"[+] Actual Trading Days Found:   {report.actual_trading_days_found}")
        print(f"[+] Official NSE Holidays:       {report.official_holiday_days}")
        print(f"[+] Weekend Days Skipped:        {report.weekend_days}")
        print(f"[+] Pipeline Calendar Coverage:  {report.coverage_percentage}%")

        if report.is_clean:
            print("[✅] CALENDAR AUDIT PASSED: Zero missing trading days detected!")
        else:
            print(f"[⚠️] CALENDAR AUDIT WARNING: Missing {len(report.missing_trading_days)} days: {report.missing_trading_days}")
    else:
        print("[!] No stock data found in Bronze layer. Run Phase 1 ingestion first.")

    # 2. Promote to Silver Staging Layer
    print("")
    print("--- [2/2] Promoting Bronze Data to Silver Staging (DuckDB Sync) ---")
    staging_mgr = SilverStagingManager()
    staging_summary = staging_mgr.run_all_staging()

    stock_res = staging_summary.get("stocks", {})
    macro_res = staging_summary.get("macro", {})

    print("[+] Stock Staging Table ('stg_stocks_daily'):")
    print(f"    - Raw Input Rows:       {stock_res.get('raw_rows', 0)}")
    print(f"    - Cleaned Staged Rows:  {stock_res.get('staged_rows', 0)}")
    print(f"    - Duplicates Removed:   {stock_res.get('duplicates_removed', 0)}")
    print(f"    - Parquet Output:       {stock_res.get('silver_parquet')}")

    print("[+] Macro Staging Table ('stg_macro_indicators'):")
    print(f"    - Raw Input Rows:       {macro_res.get('raw_rows', 0)}")
    print(f"    - Cleaned Staged Rows:  {macro_res.get('staged_rows', 0)}")
    print(f"    - Duplicates Removed:   {macro_res.get('duplicates_removed', 0)}")
    print(f"    - Parquet Output:       {macro_res.get('silver_parquet')}")

    # 3. DuckDB SQL Table Verification
    print("")
    print("--- [3] DuckDB Staging Tables Direct SQL Scan ---")
    con = duckdb.connect(str(staging_mgr.warehouse_path))

    stock_check = con.execute("""
        SELECT 
            COUNT(*) as staged_rows,
            COUNT(DISTINCT symbol) as unique_symbols,
            ROUND(AVG(close), 2) as avg_price,
            SUM(CASE WHEN is_split_adjusted THEN 1 ELSE 0 END) as corporate_actions_flagged
        FROM stg_stocks_daily
    """).df()
    print(" DuckDB stg_stocks_daily:")
    print(stock_check.to_string(index=False))

    macro_check = con.execute("""
        SELECT 
            indicator_code,
            COUNT(*) as observations,
            ROUND(MIN(value), 4) as min_val,
            ROUND(MAX(value), 4) as max_val
        FROM stg_macro_indicators
        GROUP BY indicator_code
    """).df()
    print("")
    print(" DuckDB stg_macro_indicators:")
    print(macro_check.to_string(index=False))
    con.close()

    print("")
    print("=" * 80)
    print(" 🚀 PHASE 2 STAGING & CALENDAR VALIDATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_phase2()
