"""Bronze Lakehouse Storage Manager: Hive partitioning & idempotent parquet writes."""
from datetime import date, datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import duckdb
import pandas as pd
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


class LakehouseRawStorage:
    """Manages immutable, idempotent, Hive-partitioned Bronze raw layer storage."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = Path(base_path) if base_path else settings.raw_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _compute_batch_hash(self, records: List[BaseModel]) -> str:
        """Computes deterministic SHA-256 fingerprint for a list of records."""
        combined_hashes = "".join(sorted([getattr(r, "payload_hash", str(r.model_dump())) for r in records]))
        return hashlib.sha256(combined_hashes.encode("utf-8")).hexdigest()

    def write_partition(
        self,
        dataset: str,
        partition_date: date,
        records: List[BaseModel],
    ) -> Dict[str, Any]:
        """Writes a batch of validated records into a Hive-partitioned Parquet file idempotently.

        Partition Path Layout:
            <raw_path>/<dataset>/year=YYYY/month=MM/day=DD/<dataset>_<hash>.parquet
        """
        if not records:
            return {"dataset": dataset, "records_written": 0, "path": None, "idempotent_skip": True}

        year_str = f"year={partition_date.year:04d}"
        month_str = f"month={partition_date.month:02d}"
        day_str = f"day={partition_date.day:02d}"

        partition_dir = self.base_path / dataset / year_str / month_str / day_str
        partition_dir.mkdir(parents=True, exist_ok=True)

        batch_hash = self._compute_batch_hash(records)
        manifest_file = partition_dir / f"{dataset}_manifest.json"
        parquet_file = partition_dir / f"{dataset}_{batch_hash[:12]}.parquet"

        # Idempotency Check: if manifest exists and batch_hash matches, skip duplicate write
        if manifest_file.exists() and parquet_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                if manifest.get("batch_hash") == batch_hash:
                    logger.info("Idempotent hit: %s partition for %s is unchanged. Skipping write.", dataset, partition_date)
                    return {
                        "dataset": dataset,
                        "partition_date": str(partition_date),
                        "records_written": len(records),
                        "parquet_path": str(parquet_file),
                        "idempotent_skip": True,
                        "batch_hash": batch_hash,
                    }
            except Exception as e:
                logger.warning("Manifest read error on %s: %s. Overwriting.", manifest_file, e)

        # Convert Pydantic records to pandas DataFrame
        data_dicts = [r.model_dump() for r in records]
        df = pd.DataFrame(data_dicts)

        # Write Parquet with Snappy compression
        df.to_parquet(parquet_file, index=False, engine="pyarrow", compression="snappy")

        # Write Manifest
        manifest_data = {
            "dataset": dataset,
            "partition_date": str(partition_date),
            "record_count": len(records),
            "batch_hash": batch_hash,
            "written_at_utc": datetime.now(timezone.utc).isoformat(),
            "parquet_file": parquet_file.name,
        }
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        logger.info("Successfully wrote %d records to %s", len(records), parquet_file)
        return {
            "dataset": dataset,
            "partition_date": str(partition_date),
            "records_written": len(records),
            "parquet_path": str(parquet_file),
            "idempotent_skip": False,
            "batch_hash": batch_hash,
        }

    def write_records_by_day(
        self,
        dataset: str,
        records: List[BaseModel],
        date_field: str = "trade_date",
    ) -> List[Dict[str, Any]]:
        """Splits heterogeneous multi-day records into daily Hive partitions and writes them."""
        from collections import defaultdict

        grouped = defaultdict(list)
        for r in records:
            d = getattr(r, date_field)
            if isinstance(d, datetime):
                d = d.date()
            grouped[d].append(r)

        results = []
        for partition_date, day_records in sorted(grouped.items()):
            res = self.write_partition(dataset, partition_date, day_records)
            results.append(res)
        return results

    def read_dataset(
        self,
        dataset: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """Reads partitioned Parquet files for a given dataset into a single pandas DataFrame."""
        dataset_dir = self.base_path / dataset
        if not dataset_dir.exists():
            return pd.DataFrame()

        parquet_files = list(dataset_dir.glob("**/*.parquet"))
        if not parquet_files:
            return pd.DataFrame()

        dfs = [pd.read_parquet(p) for p in parquet_files]
        combined = pd.concat(dfs, ignore_index=True)

        if "trade_date" in combined.columns:
            combined["trade_date"] = pd.to_datetime(combined["trade_date"]).dt.date
            if start_date:
                combined = combined[combined["trade_date"] >= start_date]
            if end_date:
                combined = combined[combined["trade_date"] <= end_date]
            combined = combined.sort_values(by=["trade_date"]).reset_index(drop=True)

        return combined

    def register_duckdb_view(
        self,
        dataset: str,
        con: duckdb.DuckDBPyConnection,
        view_name: Optional[str] = None,
    ) -> str:
        """Registers all partitioned Parquet files for a dataset as a queryable DuckDB view."""
        v_name = view_name or f"raw_{dataset}"
        glob_path = str(self.base_path / dataset / "**" / "*.parquet")
        con.execute(f"CREATE OR REPLACE VIEW {v_name} AS SELECT * FROM read_parquet('{glob_path}')")
        logger.info("Registered DuckDB view '%s' pointing to %s", v_name, glob_path)
        return v_name
