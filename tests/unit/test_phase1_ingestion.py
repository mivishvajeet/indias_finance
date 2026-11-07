"""Unit tests for Phase 1: Models, Base Client, Ingestion, and Idempotent Storage."""
from datetime import date, datetime
import pytest
from pydantic import ValidationError

from src.ingestion.models import DailyStockRawRecord, MacroIndicatorRawRecord
from src.ingestion.nse_stocks import NseStockIngestor
from src.ingestion.macro_client import MacroDataIngestor
from src.storage.lakehouse import LakehouseRawStorage


class TestIngestionModels:
    """Tests Pydantic contracts and data parsing."""

    def test_daily_stock_model_valid(self, sample_stock_record):
        assert sample_stock_record.symbol == "RELIANCE.NS"
        assert sample_stock_record.trade_date == date(2025, 1, 15)
        assert sample_stock_record.close == 2975.25
        assert len(sample_stock_record.payload_hash) == 64  # SHA-256 length

    def test_daily_stock_model_rejects_negative_volume(self):
        with pytest.raises(ValidationError):
            DailyStockRawRecord(
                symbol="TCS.NS",
                trade_date=date(2025, 1, 15),
                open=4000.0,
                high=4050.0,
                low=3980.0,
                close=4020.0,
                adj_close=4020.0,
                volume=-500,  # Prohibited negative volume
                source="test",
            )

    def test_daily_stock_hash_determinism(self):
        r1 = DailyStockRawRecord(
            symbol="INFY.NS",
            trade_date=date(2025, 1, 10),
            open=1800.0,
            high=1820.0,
            low=1790.0,
            close=1815.0,
            adj_close=1815.0,
            volume=100000,
        )
        r2 = DailyStockRawRecord(
            symbol="INFY.NS",
            trade_date=date(2025, 1, 10),
            open=1800.0,
            high=1820.0,
            low=1790.0,
            close=1815.0,
            adj_close=1815.0,
            volume=100000,
        )
        assert r1.payload_hash == r2.payload_hash

    def test_macro_indicator_model(self, sample_macro_record):
        assert sample_macro_record.indicator_code == "REPO_RATE"
        assert sample_macro_record.value == 6.50
        assert len(sample_macro_record.payload_hash) == 64


class TestLakehouseStorage:
    """Tests partitioning layout and idempotency guarantees."""

    def test_partition_directory_structure(self, temp_lakehouse, sample_stock_record):
        res = temp_lakehouse.write_partition(
            dataset="stocks_daily",
            partition_date=sample_stock_record.trade_date,
            records=[sample_stock_record],
        )
        assert res["records_written"] == 1
        assert res["idempotent_skip"] is False

        expected_part = "stocks_daily/year=2025/month=01/day=15"
        assert expected_part in res["parquet_path"]

    def test_idempotent_skip_on_identical_payload(self, temp_lakehouse, sample_stock_record):
        # First write
        res1 = temp_lakehouse.write_partition(
            dataset="stocks_daily",
            partition_date=sample_stock_record.trade_date,
            records=[sample_stock_record],
        )
        assert res1["idempotent_skip"] is False

        # Second write with exact same payload
        res2 = temp_lakehouse.write_partition(
            dataset="stocks_daily",
            partition_date=sample_stock_record.trade_date,
            records=[sample_stock_record],
        )
        # QA assertion: Idempotent skip must be True!
        assert res2["idempotent_skip"] is True
        assert res2["records_written"] == 1

    def test_read_dataset_dataframe(self, temp_lakehouse, sample_stock_record):
        temp_lakehouse.write_partition(
            dataset="stocks_daily",
            partition_date=sample_stock_record.trade_date,
            records=[sample_stock_record],
        )
        df = temp_lakehouse.read_dataset("stocks_daily")
        assert len(df) == 1
        assert df.iloc[0]["symbol"] == "RELIANCE.NS"
        assert df.iloc[0]["close"] == 2975.25


class TestIngestionConnectors:
    """Tests Stock and Macro Ingestors."""

    def test_macro_ingestor_baseline(self):
        ingestor = MacroDataIngestor()
        records = ingestor.fetch_all(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
        assert len(records) > 0
        codes = {r.indicator_code for r in records}
        assert "USD_INR" in codes
        assert "REPO_RATE" in codes

    def test_stock_ingestor_fallback(self):
        ingestor = NseStockIngestor()
        # Test synthetic fallback generator produces valid records
        fallback_records = ingestor._generate_fallback_series("TCS.NS", date(2025, 1, 1), date(2025, 1, 10))
        assert len(fallback_records) > 0
        for r in fallback_records:
            assert r.symbol == "TCS.NS"
            assert r.high >= r.low
            assert r.volume > 0
