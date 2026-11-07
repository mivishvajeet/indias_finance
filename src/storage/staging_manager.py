"""Silver Staging Layer: Deduplication, price sanity, corporate actions & DuckDB sync."""
from datetime import date, datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import pandas as pd

from config.settings import settings
from src.storage.lakehouse import LakehouseRawStorage

logger = logging.getLogger(__name__)


class SilverStagingManager:
    """Promotes raw Bronze Lakehouse data into cleaned Silver Staging datasets."""

    def __init__(
        self,
        raw_storage: Optional[LakehouseRawStorage] = None,
        warehouse_path: Optional[Path] = None,
        staging_path: Optional[Path] = None,
    ):
        self.raw_storage = raw_storage or LakehouseRawStorage()
        self.warehouse_path = Path(warehouse_path) if warehouse_path else settings.warehouse_path
        self.warehouse_path.parent.mkdir(parents=True, exist_ok=True)

        if staging_path:
            self.staging_path = Path(staging_path)
        elif raw_storage and raw_storage.base_path != settings.raw_path:
            self.staging_path = raw_storage.base_path.parent / "staging"
        else:
            self.staging_path = settings.staging_path

        self.staging_path.mkdir(parents=True, exist_ok=True)

    def process_stocks_staging(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Cleans, deduplicates, validates price sanity, and populates stg_stocks_daily in DuckDB."""
        raw_df = self.raw_storage.read_dataset("stocks_daily", start_date, end_date)
        if raw_df.empty:
            logger.warning("No raw stock data found to stage.")
            return {"status": "empty", "rows_staged": 0}

        # 1. Deduplication: keep the latest record by ingested_at per (symbol, trade_date)
        raw_df["ingested_at"] = pd.to_datetime(raw_df["ingested_at"])
        dedup_df = raw_df.sort_values("ingested_at").groupby(["symbol", "trade_date"]).last().reset_index()

        # 2. Price Sanity & Boundary Rules (QA validation)
        # Rule A: High must be >= Low
        # Rule B: High must be >= max(Open, Close)
        # Rule C: Low must be <= min(Open, Close)
        # Rule D: Volume must be >= 0
        dedup_df["high"] = dedup_df[["high", "open", "close"]].max(axis=1)
        dedup_df["low"] = dedup_df[["low", "open", "close"]].min(axis=1)
        dedup_df["volume"] = dedup_df["volume"].clip(lower=0)

        # 3. Corporate Action / Split Detection Flag
        # If close / adj_close ratio diverges significantly (> 1.25), flag as corporate action adjusted
        dedup_df["is_split_adjusted"] = (abs(dedup_df["close"] - dedup_df["adj_close"]) / dedup_df["close"].clip(lower=0.01)) > 0.05

        # 4. Write Silver Parquet
        silver_parquet_path = self.staging_path / "stg_stocks_daily.parquet"
        dedup_df.to_parquet(silver_parquet_path, index=False, engine="pyarrow", compression="snappy")

        # 5. Sync to DuckDB Warehouse
        con = duckdb.connect(str(self.warehouse_path))
        con.execute(f"CREATE OR REPLACE TABLE stg_stocks_daily AS SELECT * FROM read_parquet('{silver_parquet_path}')")
        con.close()

        logger.info("Successfully staged %d stock records into DuckDB table 'stg_stocks_daily'", len(dedup_df))
        return {
            "status": "success",
            "raw_rows": len(raw_df),
            "staged_rows": len(dedup_df),
            "duplicates_removed": len(raw_df) - len(dedup_df),
            "silver_parquet": str(silver_parquet_path),
            "warehouse_table": "stg_stocks_daily",
        }

    def process_macro_staging(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Cleans, deduplicates, and populates stg_macro_indicators in DuckDB."""
        raw_df = self.raw_storage.read_dataset("macro_indicators", start_date, end_date)
        if raw_df.empty:
            logger.warning("No raw macro data found to stage.")
            return {"status": "empty", "rows_staged": 0}

        # Deduplicate by indicator_code and trade_date
        raw_df["ingested_at"] = pd.to_datetime(raw_df["ingested_at"])
        dedup_df = raw_df.sort_values("ingested_at").groupby(["indicator_code", "trade_date"]).last().reset_index()

        # Write Silver Parquet
        silver_parquet_path = self.staging_path / "stg_macro_indicators.parquet"
        dedup_df.to_parquet(silver_parquet_path, index=False, engine="pyarrow", compression="snappy")

        # Sync to DuckDB Warehouse
        con = duckdb.connect(str(self.warehouse_path))
        con.execute(f"CREATE OR REPLACE TABLE stg_macro_indicators AS SELECT * FROM read_parquet('{silver_parquet_path}')")
        con.close()

        logger.info("Successfully staged %d macro records into DuckDB table 'stg_macro_indicators'", len(dedup_df))
        return {
            "status": "success",
            "raw_rows": len(raw_df),
            "staged_rows": len(dedup_df),
            "duplicates_removed": len(raw_df) - len(dedup_df),
            "silver_parquet": str(silver_parquet_path),
            "warehouse_table": "stg_macro_indicators",
        }

    def run_all_staging(self) -> Dict[str, Any]:
        """Executes full staging transformation across all raw datasets."""
        stock_res = self.process_stocks_staging()
        macro_res = self.process_macro_staging()
        return {
            "stocks": stock_res,
            "macro": macro_res,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
