"""Unit tests for Phase 2: Calendar Validator, Silver Staging, and Airflow Tasks."""
from datetime import date, timedelta
from pathlib import Path
import pytest
import pandas as pd

from src.quality.calendar_validator import CalendarValidator
from src.storage.staging_manager import SilverStagingManager
from src.storage.lakehouse import LakehouseRawStorage
from src.ingestion.models import DailyStockRawRecord


class TestCalendarValidator:
    """Tests NSE Trading Calendar validation rules."""

    def test_weekend_detection(self):
        validator = CalendarValidator()
        # Saturday
        is_open, reason = validator.is_trading_day(date(2025, 1, 18))
        assert is_open is False
        assert "Weekend" in reason

        # Sunday
        is_open, reason = validator.is_trading_day(date(2025, 1, 19))
        assert is_open is False
        assert "Weekend" in reason

    def test_official_nse_holiday_detection(self):
        validator = CalendarValidator()
        # Republic Day 2024 (2024-01-26) was Friday
        is_open, reason = validator.is_trading_day(date(2024, 1, 26))
        assert is_open is False
        assert "Republic Day" in reason

    def test_regular_trading_day(self):
        validator = CalendarValidator()
        # Regular Wednesday
        is_open, reason = validator.is_trading_day(date(2025, 1, 15))
        assert is_open is True
        assert "Regular" in reason

    def test_audit_coverage_detects_data_dropout(self):
        validator = CalendarValidator()
        # Week of Monday Jan 13 to Friday Jan 17, 2025 (5 trading days, no holidays)
        start = date(2025, 1, 13)
        end = date(2025, 1, 17)

        # Simulate that Thursday Jan 16 is missing from ingestion
        actual_dates = {date(2025, 1, 13), date(2025, 1, 14), date(2025, 1, 15), date(2025, 1, 17)}
        report = validator.audit_coverage(actual_dates, start, end)

        assert report.is_clean is False
        assert date(2025, 1, 16) in report.missing_trading_days
        assert report.coverage_percentage == 80.0


class TestSilverStaging:
    """Tests Silver Layer deduplication and price sanity rules."""

    def test_deduplication_and_price_sanity(self, tmp_path):
        raw_storage = LakehouseRawStorage(base_path=tmp_path / "lakehouse" / "raw")
        warehouse_path = tmp_path / "warehouse" / "test.duckdb"

        # Create two records for same symbol and date (duplicate load scenario)
        r1 = DailyStockRawRecord(
            symbol="TCS.NS",
            trade_date=date(2025, 1, 15),
            open=4000.0,
            high=3950.0,  # Intentional sanity flaw: High < Open
            low=3900.0,
            close=3980.0,
            adj_close=3980.0,
            volume=100000,
        )
        r2 = DailyStockRawRecord(
            symbol="TCS.NS",
            trade_date=date(2025, 1, 15),
            open=4000.0,
            high=4050.0,
            low=3900.0,
            close=4020.0,
            adj_close=4020.0,
            volume=120000,
        )

        raw_storage.write_partition("stocks_daily", date(2025, 1, 15), [r1, r2])

        staging_mgr = SilverStagingManager(raw_storage=raw_storage, warehouse_path=warehouse_path)
        res = staging_mgr.process_stocks_staging()

        assert res["status"] == "success"
        assert res["staged_rows"] == 1  # Deduplicated down to 1
        assert res["duplicates_removed"] == 1

        # Check that price sanity rule enforced High >= max(Open, Close)
        staged_df = pd.read_parquet(res["silver_parquet"])
        assert staged_df.iloc[0]["high"] >= staged_df.iloc[0]["open"]
        assert staged_df.iloc[0]["high"] >= staged_df.iloc[0]["close"]
        assert staged_df.iloc[0]["low"] <= staged_df.iloc[0]["open"]


class TestDagIntegrity:
    """Tests that Airflow task callables execute without runtime exceptions."""

    def test_daily_dag_market_check_callable(self):
        from dags.dag_daily_market_ingest import task_check_market_holiday
        result = task_check_market_holiday()
        assert "is_open" in result
        assert "date" in result
