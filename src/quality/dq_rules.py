"""Data Quality Rule definitions, categories, and audit result models."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CheckStatus(str, Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class RuleCategory(str, Enum):
    COMPLETENESS = "COMPLETENESS"
    VALIDITY = "VALIDITY"
    TIMELINESS = "TIMELINESS"
    CONSISTENCY = "CONSISTENCY"
    ANOMALY = "ANOMALY"


class CheckResult(BaseModel):
    """Result of an individual data quality check."""
    rule_name: str
    category: RuleCategory
    target_table: str
    status: CheckStatus
    records_scanned: int
    records_failed: int = 0
    failure_rate_pct: float = 0.0
    details: str = ""
    remediation_advice: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_passing(self) -> bool:
        return self.status == CheckStatus.PASSED


class LayerAuditSummary(BaseModel):
    """Aggregated quality scorecard for a specific lakehouse layer."""
    layer_name: str
    target_table: str
    total_checks: int
    passed_checks: int
    warning_checks: int
    failed_checks: int
    quality_score_pct: float
    results: List[CheckResult] = Field(default_factory=list)


class CrossLayerReconciliationResult(BaseModel):
    """Reconciliation report comparing Bronze, Silver, and Gold layers."""
    bronze_raw_count: int
    silver_staged_count: int
    gold_fact_count: int
    bronze_to_silver_delta: int
    silver_to_gold_delta: int
    deduplication_rate_pct: float
    gold_coverage_pct: float
    is_reconciled: bool
    reconciliation_notes: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
