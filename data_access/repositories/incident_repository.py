"""Data Incident Repository: Persists and manages incident lifecycle in DuckDB."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client


class IncidentRepository:
    """Manages CRUD operations and lifecycle state transitions for data incidents."""

    @staticmethod
    def init_table():
        """Creates the data_incidents table in DuckDB if not exists and seeds baseline history."""
        con = db_client.get_read_write_connection()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS data_incidents (
                    incident_id VARCHAR PRIMARY KEY,
                    title VARCHAR,
                    severity VARCHAR,
                    lifecycle_status VARCHAR,
                    source_component VARCHAR,
                    affected_table VARCHAR,
                    detection_timestamp TIMESTAMP,
                    failure_description VARCHAR,
                    expected_condition VARCHAR,
                    actual_condition VARCHAR,
                    related_failed_tests VARCHAR,
                    suggested_investigation VARCHAR,
                    investigation_notes VARCHAR,
                    resolved_at TIMESTAMP
                );
            """)

            # Pre-seed realistic operational incident history if empty
            cnt = con.execute("SELECT COUNT(*) FROM data_incidents").fetchone()[0]
            if cnt == 0:
                con.execute("""
                    INSERT INTO data_incidents VALUES
                    (
                        'INC-2026-001',
                        'Duplicate Tick Bars Detected During Retry Ingestion',
                        'MEDIUM',
                        'RESOLVED',
                        'src.storage.staging_manager',
                        'main_staging.stg_stocks',
                        '2026-11-06 17:35:00',
                        'Overlapping ingestion windows produced 30 duplicate raw ticks.',
                        'Deduplicated row count equals unique (symbol, trade_date).',
                        'Found 30 duplicate bars matching previously committed batch.',
                        'unique_stg_stocks_stock_price_id',
                        'Verify natural surrogate key hash in Silver staging.',
                        'Idempotency deduplication automatically resolved duplicate ticks. 0 unhandled rows remain.',
                        '2026-11-06 17:36:10'
                    ),
                    (
                        'INC-2026-002',
                        'Trading Calendar Holiday Discrimination Audit',
                        'LOW',
                        'RESOLVED',
                        'src.quality.calendar_validator',
                        'main_marts.dim_date',
                        '2026-11-05 17:30:00',
                        'Diwali official market holiday verification pass.',
                        'Exchange closed on official NSE holidays without missing data alert.',
                        'NSE calendar marked Diwali session as closed. Ingestion bypassed.',
                        'test_calendar_no_unexplained_gaps',
                        'Verify nse_trading_holidays seed table.',
                        'CalendarValidator successfully matched official holiday; zero data dropouts recorded.',
                        '2026-11-05 17:30:15'
                    );
                """)
        finally:
            con.close()

    @staticmethod
    def get_all_incidents() -> pd.DataFrame:
        IncidentRepository.init_table()
        con = db_client.get_read_write_connection()
        try:
            return con.execute("SELECT * FROM data_incidents ORDER BY detection_timestamp DESC").df()
        finally:
            con.close()

    @staticmethod
    def update_incident_status(incident_id: str, new_status: str, notes: str = ""):
        IncidentRepository.init_table()
        con = db_client.get_read_write_connection()
        try:
            resolved_ts = "CURRENT_TIMESTAMP" if new_status == "RESOLVED" else "NULL"
            notes_clause = f", investigation_notes = '{notes}'" if notes else ""
            con.execute(f"""
                UPDATE data_incidents
                SET lifecycle_status = '{new_status}',
                    resolved_at = {resolved_ts}
                    {notes_clause}
                WHERE incident_id = '{incident_id}'
            """)
        finally:
            con.close()

    @staticmethod
    def create_incident(
        title: str,
        severity: str,
        source: str,
        table: str,
        description: str,
        expected: str,
        actual: str,
        tests: str = "",
        investigation: str = "",
    ) -> str:
        IncidentRepository.init_table()
        con = db_client.get_read_write_connection()
        try:
            cnt = con.execute("SELECT COUNT(*) FROM data_incidents").fetchone()[0]
            inc_id = f"INC-2026-{cnt + 1:03d}"
            con.execute("""
                INSERT INTO data_incidents VALUES
                (?, ?, ?, 'DETECTED', ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, '', NULL)
            """, [inc_id, title, severity, source, table, description, expected, actual, tests, investigation])
            return inc_id
        finally:
            con.close()
