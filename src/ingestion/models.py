"""Pydantic data models defining the Bronze / Raw Layer schemas."""
from datetime import date, datetime, timezone
import hashlib
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DailyStockRawRecord(BaseModel):
    """Schema for individual daily stock and index price bar in Bronze raw layer."""

    symbol: str = Field(..., description="Ticker symbol e.g. RELIANCE.NS, ^NSEI")
    trade_date: date = Field(..., description="Trading date (YYYY-MM-DD)")
    open: float = Field(..., description="Opening price in INR")
    high: float = Field(..., description="Day highest traded price in INR")
    low: float = Field(..., description="Day lowest traded price in INR")
    close: float = Field(..., description="Closing price in INR")
    adj_close: float = Field(..., description="Dividend and split adjusted close in INR")
    volume: int = Field(..., ge=0, description="Trading volume (shares/contracts)")
    source: str = Field(default="yfinance", description="Data provider or archive source")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC ingestion timestamp")
    payload_hash: str = Field(default="", description="SHA-256 fingerprint of the record")

    @field_validator("high")
    @classmethod
    def validate_high(cls, v: float, info) -> float:
        # Note: Pre-ingestion sanity. Formal DQ layer will evaluate cross-row metrics
        return round(float(v), 4)

    def model_post_init(self, __context) -> None:
        if not self.payload_hash:
            # Deterministic hash over primary business keys + close
            raw_str = f"{self.symbol}|{self.trade_date.isoformat()}|{self.close:.4f}|{self.volume}"
            self.payload_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


class MacroIndicatorRawRecord(BaseModel):
    """Schema for macroeconomic indicator observations in Bronze raw layer."""

    indicator_code: str = Field(..., description="Code e.g. REPO_RATE, CPI_INFLATION, USD_INR")
    trade_date: date = Field(..., description="Observation or effective date (YYYY-MM-DD)")
    value: float = Field(..., description="Numerical value of the indicator")
    frequency: str = Field(..., description="Observation frequency: daily, monthly, quarterly")
    unit: str = Field(..., description="Unit of measurement: percentage, INR_per_USD, index")
    source: str = Field(..., description="Data source e.g. RBI, MOSPI, yfinance")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC ingestion timestamp")
    payload_hash: str = Field(default="", description="SHA-256 fingerprint of the observation")

    def model_post_init(self, __context) -> None:
        if not self.payload_hash:
            raw_str = f"{self.indicator_code}|{self.trade_date.isoformat()}|{self.value:.4f}"
            self.payload_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


class IngestionResult(BaseModel):
    """Execution summary returned by an ingestion run."""

    dataset: str
    total_records: int
    unique_keys: int
    partition_paths: List[str]
    is_idempotent_skip: bool = False
    execution_time_sec: float
    error_message: Optional[str] = None
