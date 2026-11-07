"""Pytest configuration and shared test fixtures."""
from datetime import date, datetime
from pathlib import Path
import pytest

from src.ingestion.models import DailyStockRawRecord, MacroIndicatorRawRecord
from src.storage.lakehouse import LakehouseRawStorage


@pytest.fixture
def temp_lakehouse(tmp_path: Path) -> LakehouseRawStorage:
    """Fixture providing an isolated temporary Bronze Lakehouse storage instance."""
    return LakehouseRawStorage(base_path=tmp_path / "lakehouse" / "raw")


@pytest.fixture
def sample_stock_record() -> DailyStockRawRecord:
    """Fixture providing a valid daily stock record."""
    return DailyStockRawRecord(
        symbol="RELIANCE.NS",
        trade_date=date(2025, 1, 15),
        open=2950.0,
        high=2980.5,
        low=2942.0,
        close=2975.25,
        adj_close=2975.25,
        volume=2540000,
        source="yfinance",
    )


@pytest.fixture
def sample_macro_record() -> MacroIndicatorRawRecord:
    """Fixture providing a valid macro indicator record."""
    return MacroIndicatorRawRecord(
        indicator_code="REPO_RATE",
        trade_date=date(2025, 2, 7),
        value=6.50,
        frequency="policy_decision",
        unit="percentage",
        source="RBI",
    )
