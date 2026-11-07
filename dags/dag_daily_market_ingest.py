"""Daily Market Close Pipeline: Scheduled Monday to Friday at 17:30 IST (12:00 UTC).
Orchestrates: Ingestion -> Calendar Audit -> Staging -> dbt Run -> dbt Test (Quality Gate)
"""
from datetime import date, datetime, timedelta
import logging
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = PROJECT_ROOT / "finance_dbt"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.nse_stocks import NseStockIngestor
from src.ingestion.macro_client import MacroDataIngestor
from src.storage.lakehouse import LakehouseRawStorage
from src.storage.staging_manager import SilverStagingManager
from src.quality.calendar_validator import CalendarValidator

logger = logging.getLogger("airflow.dag.daily_market_ingest")


def task_check_market_holiday(**context):
    """Checks if today is an official NSE trading holiday or weekend."""
    today = date.today()
    validator = CalendarValidator()
    is_open, reason = validator.is_trading_day(today)
    logger.info("Market check for %s: is_open=%s (%s)", today, is_open, reason)
    return {"is_open": is_open, "reason": reason, "date": today.isoformat()}


def task_ingest_stocks_raw(**context):
    """Ingests daily OHLCV bars for Nifty 50 and benchmark indices into Bronze lakehouse."""
    today = date.today()
    start_date = today - timedelta(days=14)
    ingestor = NseStockIngestor()
    records = ingestor.fetch_universe(start_date=start_date, end_date=today)

    storage = LakehouseRawStorage()
    partitions = storage.write_records_by_day("stocks_daily", records)
    logger.info("Ingested %d stock bars into %d partitions", len(records), len(partitions))
    return {"total_records": len(records), "partitions": len(partitions)}


def task_ingest_macro_raw(**context):
    """Ingests latest USD/INR and macro updates into Bronze lakehouse."""
    today = date.today()
    start_date = today - timedelta(days=45)
    ingestor = MacroDataIngestor()
    records = ingestor.fetch_all(start_date=start_date, end_date=today)

    storage = LakehouseRawStorage()
    partitions = storage.write_records_by_day("macro_indicators", records)
    logger.info("Ingested %d macro observations into %d partitions", len(records), len(partitions))
    return {"total_records": len(records), "partitions": len(partitions)}


def task_audit_calendar_coverage(**context):
    """Audits Bronze stock data against the official NSE calendar for silent dropouts."""
    storage = LakehouseRawStorage()
    df = storage.read_dataset("stocks_daily")
    if df.empty:
        logger.warning("No data found for calendar audit.")
        return {"status": "empty"}

    actual_dates = set(df["trade_date"].unique())
    start_date = min(actual_dates)
    end_date = max(actual_dates)

    validator = CalendarValidator()
    report = validator.audit_coverage(actual_dates, start_date, end_date)
    logger.info("Calendar Audit: Coverage=%.2f%%, Missing Days=%s", report.coverage_percentage, report.missing_trading_days)
    return report.model_dump()


def task_process_silver_staging(**context):
    """Deduplicates, validates price sanity, and populates DuckDB staging tables."""
    staging_mgr = SilverStagingManager()
    summary = staging_mgr.run_all_staging()
    logger.info("Silver Staging Complete: %s", summary)
    return summary


def task_dbt_run(**context):
    """Executes dbt models: Staging -> Intermediate Technicals -> Star Schema Marts."""
    logger.info("Starting dbt run in %s", DBT_DIR)
    cmd = ["dbt", "run", "--profiles-dir", "."]
    res = subprocess.run(cmd, cwd=str(DBT_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        logger.error("dbt run FAILED:\n%s", res.stderr or res.stdout)
        raise RuntimeError(f"dbt run failed with exit code {res.returncode}")
    logger.info("dbt run SUCCEEDED:\n%s", res.stdout)
    return {"status": "success"}


def task_dbt_test(**context):
    """Runs all 48 dbt schema and singular tests. Fails the DAG if any data assertion fails."""
    logger.info("Starting dbt test quality gate in %s", DBT_DIR)
    cmd = ["dbt", "test", "--profiles-dir", "."]
    res = subprocess.run(cmd, cwd=str(DBT_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        logger.error("dbt test QUALITY GATE FAILED:\n%s", res.stderr or res.stdout)
        raise AssertionError("Data Quality Gate Failure: dbt test detected defects in warehouse tables!")
    logger.info("dbt test QUALITY GATE PASSED (0 defects):\n%s", res.stdout)
    return {"status": "passed"}


# Airflow DAG definition
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    default_args = {
        "owner": "data_engineering",
        "depends_on_past": False,
        "email_on_failure": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=3),
    }

    dag = DAG(
        dag_id="dag_daily_market_ingest",
        default_args=default_args,
        description="Daily Indian market ingestion, dbt star schema modeling & quality testing",
        schedule_interval="30 12 * * 1-5",  # 12:00 UTC = 17:30 IST Mon-Fri
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=["india_finance", "stocks", "dbt", "data_quality"],
    )

    t1 = PythonOperator(task_id="check_market_holiday", python_callable=task_check_market_holiday, dag=dag)
    t2 = PythonOperator(task_id="ingest_stocks_raw", python_callable=task_ingest_stocks_raw, dag=dag)
    t3 = PythonOperator(task_id="ingest_macro_raw", python_callable=task_ingest_macro_raw, dag=dag)
    t4 = PythonOperator(task_id="audit_calendar_coverage", python_callable=task_audit_calendar_coverage, dag=dag)
    t5 = PythonOperator(task_id="process_silver_staging", python_callable=task_process_silver_staging, dag=dag)
    t6 = PythonOperator(task_id="dbt_run_models", python_callable=task_dbt_run, dag=dag)
    t7 = PythonOperator(task_id="dbt_test_quality_gate", python_callable=task_dbt_test, dag=dag)

    # Lineage dependency chain: Circuit breaker terminates DAG if t7 fails
    t1 >> [t2, t3] >> t4 >> t5 >> t6 >> t7

except ImportError:
    dag = None
