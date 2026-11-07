"""CLI Runner for Phase 1: Stock & Macro Ingestion into Bronze Lakehouse."""
import argparse
from datetime import date, timedelta
import logging
import sys
import time

# Ensure project root is in sys.path
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.nse_stocks import NseStockIngestor
from src.ingestion.macro_client import MacroDataIngestor
from src.storage.lakehouse import LakehouseRawStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("phase1_runner")


def run_pipeline(days: int = 14, symbols: list = None, include_macro: bool = True):
    print("=" * 80)
    print(" 🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL — PHASE 1 RAW INGESTION")
    print("=" * 80)

    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    print(f"[*] Ingestion Date Range: {start_date} to {end_date} ({days} days)")

    storage = LakehouseRawStorage()
    t0 = time.time()

    # 1. Stocks & Benchmark Indices Ingestion
    print("\n--- [1/2] Ingesting Stock & Benchmark Price Bars ---")
    stock_ingestor = NseStockIngestor()
    target_symbols = symbols or ["^NSEI", "^NSEBANK", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    print(f"[*] Target Symbols ({len(target_symbols)}): {', '.join(target_symbols)}")

    stock_records = stock_ingestor.fetch_universe(
        symbols=target_symbols,
        start_date=start_date,
        end_date=end_date,
    )
    print(f"[+] Total stock raw bars fetched: {len(stock_records)}")

    # Write to Bronze Lakehouse
    stock_partitions = storage.write_records_by_day("stocks_daily", stock_records)
    print(f"[+] Stock partitions created/verified: {len(stock_partitions)}")
    skips = sum(1 for p in stock_partitions if p.get("idempotent_skip"))
    if skips > 0:
        print(f"    (Idempotent skips: {skips}/{len(stock_partitions)})")

    # 2. Macroeconomic Indicators Ingestion
    macro_records = []
    if include_macro:
        print("\n--- [2/2] Ingesting Macroeconomic Series & FX ---")
        macro_ingestor = MacroDataIngestor()
        macro_records = macro_ingestor.fetch_all(start_date=start_date - timedelta(days=90), end_date=end_date)
        print(f"[+] Total macro observations fetched: {len(macro_records)}")

        macro_partitions = storage.write_records_by_day("macro_indicators", macro_records)
        print(f"[+] Macro partitions created/verified: {len(macro_partitions)}")

    elapsed = round(time.time() - t0, 2)

    # Summary table
    print("\n" + "=" * 80)
    print(" 📊 PHASE 1 INGESTION SUMMARY REPORT")
    print("=" * 80)
    print(f" Execution Time: {elapsed} seconds")
    print(f" Raw Lakehouse Storage: {storage.base_path.resolve()}")
    print(f" Total Stock Records: {len(stock_records)}")
    print(f" Total Macro Records: {len(macro_records)}")
    print(f" Sample Partition Path: {stock_partitions[0]['parquet_path'] if stock_partitions else 'N/A'}")
    print("=" * 80)
    print(" Phase 1 Ingestion Pipeline Completed Successfully! 🚀\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 1 Raw Financial Data Ingestion")
    parser.add_argument("--days", type=int, default=14, help="Number of historical days to ingest")
    parser.add_argument("--symbols", nargs="+", default=None, help="Specific symbols to ingest")
    parser.add_argument("--no-macro", action="store_true", help="Skip macroeconomic ingestion")
    args = parser.parse_args()

    run_pipeline(
        days=args.days,
        symbols=args.symbols,
        include_macro=not args.no_macro,
    )
