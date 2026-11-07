"""Daily Market Close Pipeline: Scheduled Monday to Friday at 17:30 IST (12:00 UTC)."""
from datetime import date, datetime, timedelta
import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
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
    if not is_open:
        logger.info("Market is CLOSED today (%s). Downstream pipeline will run in audit mode.", reason)
    return {"is_open": is_open, "reason": reason, "date": today.isoformat()}


def task_ingest_stocks_raw(**context):
    """Ingests daily OHLCV bars for Nifty 50 and benchmark indices into Bronze lakehouse."""
    today = date.today()
    start_date = today - timedelta(days=5)  # Safe overlapping window for revision detection
    ingestor = NseStockIngestor()
    records = ingestor.fetch_universe(start_date=start_date, end_date=today)

    storage = LakehouseRawStorage()
    partitions = storage.write_records_by_day("stocks_daily", records)
    logger.info("Ingested %d stock bars into %d partitions", len(records), len(partitions))
    return {"total_records": len(records), "partitions": len(partitions)}


def task_ingest_macro_raw(**context):
    """Ingests latest USD/INR and macro updates into Bronze lakehouse."""
    today = date.today()
    start_date = today - timedelta(days=30)
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

    if not report.is_clean:
        logger.error("DATA DROPOUT ALERT: Market was open but data missing on: %s", report.missing_trading_days)
    return report.model_dump()


def task_process_silver_staging(**context):
    """Deduplicates, validates price sanity, and populates DuckDB staging tables."""
    staging_mgr = SilverStagingManager()
    summary = staging_mgr.run_all_staging()
    logger.info("Silver Staging Complete: %s", summary)
    return summary


# Airflow DAG definition (Compatible with Airflow LocalExecutor or Standalone Python execution)
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    default_args = {
        "owner": "data_engineering",
        "depends_on_past": False,
        "email_on_failure": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=3),
    }

    dag = DAG(
        dag_id="dag_daily_market_ingest",
        default_args=default_args,
        description="Daily Indian market ingestion & staging pipeline at 17:30 IST",
        schedule_interval="30 12 * * 1-5",  # 12:00 UTC = 17:30 IST Monday to Friday
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=["india_finance", "stocks", "staging", "data_quality"],
    )

    t1 = PythonOperator(task_id="check_market_holiday", python_callable=task_check_market_holiday, dag=dag)
    t2 = PythonOperator(task_id="ingest_stocks_raw", python_callable=task_ingest_stocks_raw, dag=dag)
    t3 = PythonOperator(task_id="ingest_macro_raw", python_callable=task_ingest_macro_raw, dag=dag)
    t4 = PythonOperator(task_id="audit_calendar_coverage", python_callable=task_audit_calendar_coverage, dag=dag)
    t5 = PythonOperator(task_id="process_silver_staging", python_callable=task_process_silver_staging, dag=dag)

    t1 >> [t2, t3] >> t4 >> t5

except ImportError:
    # Airflow not installed in local environment; CLI runner handles local orchestration
    dag = None
