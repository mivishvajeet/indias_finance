"""Monthly Macroeconomic Refresh Pipeline: Runs on 1st of every month at 18:00 IST."""
from datetime import date, datetime, timedelta
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.macro_client import MacroDataIngestor
from src.storage.lakehouse import LakehouseRawStorage
from src.storage.staging_manager import SilverStagingManager

logger = logging.getLogger("airflow.dag.macro_monthly")


def task_monthly_macro_refresh(**context):
    today = date.today()
    start_date = today - timedelta(days=365)
    ingestor = MacroDataIngestor()
    records = ingestor.fetch_all(start_date=start_date, end_date=today)

    storage = LakehouseRawStorage()
    partitions = storage.write_records_by_day("macro_indicators", records)

    staging_mgr = SilverStagingManager()
    staging_res = staging_mgr.process_macro_staging(start_date, today)

    logger.info("Monthly macro refresh complete: %d records, %d partitions, Staged=%s", len(records), len(partitions), staging_res)
    return {"records": len(records), "staged": staging_res}


try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator

    default_args = {
        "owner": "data_engineering",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    dag_monthly = DAG(
        dag_id="dag_macro_monthly",
        default_args=default_args,
        description="Monthly RBI & MOSPI macro series update",
        schedule_interval="0 12 1 * *",  # 1st of month at 12:00 UTC / 17:30 IST
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=["macro", "rbi", "cpi"],
    )

    t_macro = PythonOperator(
        task_id="refresh_macro_indicators",
        python_callable=task_monthly_macro_refresh,
        dag=dag_monthly,
    )
except ImportError:
    dag_monthly = None
