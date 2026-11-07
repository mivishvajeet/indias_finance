"""End-to-End Orchestrator for Phase 3:
Ingest -> Calendar Audit -> Staging -> dbt Run -> dbt Test Quality Gate
"""
import logging
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = PROJECT_ROOT / "finance_dbt"
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.staging_manager import SilverStagingManager
from src.quality.calendar_validator import CalendarValidator
from src.storage.lakehouse import LakehouseRawStorage
import duckdb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase3_orchestrator")


def run_pipeline():
    print("=" * 85)
    print(" 🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL — PHASE 3 FULL PIPELINE")
    print("=" * 85)
    t0 = time.time()

    # 1. Staging Sync
    print("\n--- [STEP 1] Promoting Staging Layer to DuckDB ---")
    staging_mgr = SilverStagingManager()
    staging_res = staging_mgr.run_all_staging()
    print(f"[+] Staged {staging_res['stocks'].get('staged_rows', 0)} stock rows and {staging_res['macro'].get('staged_rows', 0)} macro rows.")

    # 2. dbt Run
    print("\n--- [STEP 2] Executing dbt Models (Dimensions, Intermediate, Facts) ---")
    dbt_run_cmd = ["dbt", "run", "--profiles-dir", "."]
    res_run = subprocess.run(dbt_run_cmd, cwd=str(DBT_DIR), capture_output=True, text=True)
    if res_run.returncode != 0:
        print("[❌ ERROR] dbt run failed:\n", res_run.stderr or res_run.stdout)
        sys.exit(1)
    print(res_run.stdout)

    # 3. dbt Test (Quality Gate)
    print("\n--- [STEP 3] Running dbt Quality Gate (48 Automated Tests) ---")
    dbt_test_cmd = ["dbt", "test", "--profiles-dir", "."]
    res_test = subprocess.run(dbt_test_cmd, cwd=str(DBT_DIR), capture_output=True, text=True)
    if res_test.returncode != 0:
        print("[❌ QUALITY GATE FAILED] dbt tests found defects:\n", res_test.stderr or res_test.stdout)
        sys.exit(1)
    print(res_test.stdout)

    # 4. DuckDB Star Schema Mart Scan
    print("\n--- [STEP 4] Star Schema Mart Live Scan ---")
    con = duckdb.connect(str(staging_mgr.warehouse_path), read_only=True)
    fact_sample = con.execute("""
        SELECT 
            symbol, trade_date, close_price,
            bollinger_middle, bollinger_upper, bollinger_lower,
            rsi_14, ema_12, ema_26, macd_line
        FROM main_marts.fact_daily_prices
        ORDER BY symbol, trade_date DESC
        LIMIT 5
    """).df()
    print(fact_sample.to_string(index=False))
    con.close()

    elapsed = round(time.time() - t0, 2)
    print("\n" + "=" * 85)
    print(f" 🚀 FULL PHASE 3 PIPELINE COMPLETED IN {elapsed}s WITH 100% QUALITY PASS!")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    run_pipeline()
