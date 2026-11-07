"""Advanced automated pytest checks: boundary stress tests, circuit breakers, and reconciliation."""
from datetime import date, timedelta
import pytest
import pandas as pd
import duckdb

from src.quality.calendar_validator import CalendarValidator
from src.storage.staging_manager import SilverStagingManager
from src.storage.lakehouse import LakehouseRawStorage
from src.ingestion.models import DailyStockRawRecord


class TestCrossLayerReconciliation:
    """Verifies that no rows are silently lost or altered between Bronze and Silver."""

    def test_reconciliation_exact_row_counts(self, tmp_path):
        raw_storage = LakehouseRawStorage(base_path=tmp_path / "raw")
        warehouse_path = tmp_path / "warehouse" / "test.duckdb"

        # 3 unique records + 1 duplicate record
        r1 = DailyStockRawRecord(symbol="SBIN.NS", trade_date=date(2025, 1, 10), open=750, high=760, low=745, close=755, adj_close=755, volume=100)
        r2 = DailyStockRawRecord(symbol="SBIN.NS", trade_date=date(2025, 1, 11), open=755, high=765, low=750, close=760, adj_close=760, volume=100)
        r3 = DailyStockRawRecord(symbol="SBIN.NS", trade_date=date(2025, 1, 12), open=760, high=770, low=755, close=765, adj_close=765, volume=100)
        r1_dup = DailyStockRawRecord(symbol="SBIN.NS", trade_date=date(2025, 1, 10), open=750, high=762, low=745, close=758, adj_close=758, volume=120)

        raw_storage.write_partition("stocks_daily", date(2025, 1, 10), [r1, r1_dup])
        raw_storage.write_partition("stocks_daily", date(2025, 1, 11), [r2])
        raw_storage.write_partition("stocks_daily", date(2025, 1, 12), [r3])

        staging_mgr = SilverStagingManager(raw_storage=raw_storage, warehouse_path=warehouse_path)
        summary = staging_mgr.process_stocks_staging()

        assert summary["raw_rows"] == 4
        assert summary["staged_rows"] == 3
        assert summary["duplicates_removed"] == 1


class TestBoundaryStressCases:
    """QA boundary stress tests for extreme financial values."""

    def test_negative_and_inverted_boundary_sanitization(self, tmp_path):
        raw_storage = LakehouseRawStorage(base_path=tmp_path / "raw")
        warehouse_path = tmp_path / "warehouse" / "test.duckdb"

        # Flawed record: High < Low, Low > Open
        flawed = DailyStockRawRecord(
            symbol="BAD_PRICE.NS",
            trade_date=date(2025, 1, 10),
            open=100.0,
            high=90.0,   # Inverted High
            low=110.0,   # Inverted Low
            close=95.0,
            adj_close=95.0,
            volume=500,
        )
        raw_storage.write_partition("stocks_daily", date(2025, 1, 10), [flawed])

        staging_mgr = SilverStagingManager(raw_storage=raw_storage, warehouse_path=warehouse_path)
        res = staging_mgr.process_stocks_staging()

        staged_df = pd.read_parquet(res["silver_parquet"])
        row = staged_df.iloc[0]

        # Staging rules must sanitize High to be max(high, open, close) = 100.0
        assert row["high"] >= row["low"]
        assert row["high"] == 100.0
        # Low must be min(low, open, close) = 95.0
        assert row["low"] == 95.0


class TestSimulatedDropoutAlerts:
    """Tests that the CalendarValidator detects gaps in multiple scenarios."""

    def test_holiday_vs_dropout_discrimination(self):
        validator = CalendarValidator()
        # Monday to Friday with Good Friday holiday (2024-03-29)
        start = date(2024, 3, 25)  # Mon
        end = date(2024, 3, 29)    # Fri (Good Friday)

        expected = validator.get_expected_trading_days(start, end)
        assert len(expected) == 3  # Holi on 2024-03-25 and Good Friday on 2024-03-29 are holidays

        # Case 1: Ingested all expected days
        audit_full = validator.audit_coverage(set(expected), start, end)
        assert audit_full.is_clean is True
        assert audit_full.coverage_percentage == 100.0

        # Case 2: Dropped Wednesday 2024-03-27
        audit_incomplete = validator.audit_coverage(set(expected) - {date(2024, 3, 27)}, start, end)
        assert audit_incomplete.is_clean is False
        assert date(2024, 3, 27) in audit_incomplete.missing_trading_days
