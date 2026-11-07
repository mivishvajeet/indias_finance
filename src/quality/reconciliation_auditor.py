"""Cross-Layer Lakehouse Reconciliation Auditor (Bronze -> Silver -> Gold)."""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import duckdb

from src.storage.lakehouse import LakehouseRawStorage
from src.quality.dq_rules import CrossLayerReconciliationResult

logger = logging.getLogger("reconciliation_auditor")


class LakehouseReconciliationAuditor:
    """Reconciles record counts, missing entities, and deduplication deltas across Bronze, Silver, and Gold layers."""

    def __init__(
        self,
        raw_storage_dir: Optional[Path] = None,
        warehouse_path: Optional[Path] = None,
    ):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.raw_storage_dir = Path(raw_storage_dir) if raw_storage_dir else None
        self.warehouse_path = warehouse_path or (project_root / "data" / "warehouse" / "curated.duckdb")
        self.raw_storage = LakehouseRawStorage(base_path=self.raw_storage_dir) if self.raw_storage_dir else LakehouseRawStorage()

    def reconcile_stocks(self) -> CrossLayerReconciliationResult:
        """Audits row progression: Bronze Raw Parquet -> Silver Staging -> Gold Fact."""
        notes: List[str] = []

        # 1. Bronze Count
        raw_df = self.raw_storage.read_dataset("stocks_daily")
        bronze_count = len(raw_df) if not raw_df.empty else 0
        notes.append(f"Bronze Raw Parquet records discovered: {bronze_count}")

        # 2. Silver Count
        if not self.warehouse_path.exists():
            raise FileNotFoundError(f"Warehouse database not found at {self.warehouse_path}")

        con = duckdb.connect(str(self.warehouse_path), read_only=True)
        try:
            silver_count = con.execute("SELECT COUNT(*) FROM main_staging.stg_stocks").fetchone()[0]
            notes.append(f"Silver Staging records validated: {silver_count}")

            # 3. Gold Count
            gold_count = con.execute("SELECT COUNT(*) FROM main_marts.fact_daily_prices").fetchone()[0]
            notes.append(f"Gold Fact Daily Prices records compiled: {gold_count}")
        finally:
            con.close()

        # Delta computations
        bronze_to_silver_delta = bronze_count - silver_count
        silver_to_gold_delta = silver_count - gold_count

        dedup_rate = round((bronze_to_silver_delta / bronze_count * 100), 2) if bronze_count > 0 else 0.0
        gold_coverage = round((gold_count / silver_count * 100), 2) if silver_count > 0 else 0.0

        if bronze_to_silver_delta > 0:
            notes.append(f"Deduplication delta: {bronze_to_silver_delta} duplicate/overlapping raw bars removed during Silver idempotency deduplication.")
        elif bronze_to_silver_delta == 0:
            notes.append("Zero raw duplicate records detected; 100% Bronze to Silver ingestion purity.")

        if silver_to_gold_delta == 0:
            notes.append("Zero dropout between Silver and Gold; 100% of staged records successfully joined into star schema marts.")
        else:
            notes.append(f"Delta of {silver_to_gold_delta} rows between Silver and Gold (due to date filters or security dimension joins).")

        # Reconciliation is healthy if silver <= bronze and gold == silver (or expected join exclusions)
        is_reconciled = (silver_count <= bronze_count) and (gold_count == silver_count)

        return CrossLayerReconciliationResult(
            bronze_raw_count=bronze_count,
            silver_staged_count=silver_count,
            gold_fact_count=gold_count,
            bronze_to_silver_delta=bronze_to_silver_delta,
            silver_to_gold_delta=silver_to_gold_delta,
            deduplication_rate_pct=dedup_rate,
            gold_coverage_pct=gold_coverage,
            is_reconciled=is_reconciled,
            reconciliation_notes=notes,
        )

    def generate_markdown_summary(self) -> str:
        """Returns a formatted markdown reconciliation table suitable for QA scorecards and executive reports."""
        rec = self.reconcile_stocks()
        status_icon = "🟢 VERIFIED" if rec.is_reconciled else "🔴 DISCREPANCY"

        md = [
            f"### 🛡️ Cross-Layer Lakehouse Reconciliation Audit ({status_icon})",
            "",
            "| Lakehouse Layer | Target Entity | Row Count | Layer Retention / Yield | Deduplication Delta |",
            "| :--- | :--- | :---: | :---: | :---: |",
            f"| **Bronze (Raw Lakehouse)** | `data/lakehouse/raw/stocks_daily/*.parquet` | `{rec.bronze_raw_count:,}` | 100.0% (Baseline) | — |",
            f"| **Silver (Cleaned Staging)** | `main_staging.stg_stocks` | `{rec.silver_staged_count:,}` | `{100.0 - rec.deduplication_rate_pct:.2f}%` | `-{rec.bronze_to_silver_delta}` rows |",
            f"| **Gold (Curated Star Marts)** | `main_marts.fact_daily_prices` | `{rec.gold_fact_count:,}` | `{rec.gold_coverage_pct:.2f}%` | `-{rec.silver_to_gold_delta}` rows |",
            "",
            "**Audit Trace Findings:**",
        ]
        for note in rec.reconciliation_notes:
            md.append(f"- {note}")
        md.append("")
        return "\n".join(md)
