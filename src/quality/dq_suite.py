"""Automated Data Quality Suite for DuckDB Lakehouse Layers (Bronze, Silver, Gold)."""
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import duckdb

from src.quality.dq_rules import (
    CheckResult,
    CheckStatus,
    LayerAuditSummary,
    RuleCategory,
)
from src.quality.calendar_validator import CalendarValidator

logger = logging.getLogger("data_quality_suite")


class DataQualitySuite:
    """Evaluates completeness, validity, consistency, timeliness, and anomalies across warehouse tables."""

    def __init__(self, warehouse_path: Optional[Path] = None):
        if warehouse_path is None:
            self.warehouse_path = Path(__file__).resolve().parent.parent.parent / "data" / "warehouse" / "curated.duckdb"
        else:
            self.warehouse_path = Path(warehouse_path)

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        if not self.warehouse_path.exists():
            raise FileNotFoundError(f"DuckDB warehouse not found at {self.warehouse_path}")
        return duckdb.connect(str(self.warehouse_path), read_only=True)

    def audit_gold_fact_daily_prices(self) -> LayerAuditSummary:
        """Audits Gold star schema fact table: fact_daily_prices."""
        con = self._get_connection()
        table_name = "main_marts.fact_daily_prices"
        results: List[CheckResult] = []

        try:
            total_records = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            if total_records == 0:
                return LayerAuditSummary(
                    layer_name="GOLD",
                    target_table=table_name,
                    total_checks=1,
                    passed_checks=0,
                    warning_checks=0,
                    failed_checks=1,
                    quality_score_pct=0.0,
                    results=[
                        CheckResult(
                            rule_name="table_not_empty",
                            category=RuleCategory.COMPLETENESS,
                            target_table=table_name,
                            status=CheckStatus.FAILED,
                            records_scanned=0,
                            records_failed=1,
                            failure_rate_pct=100.0,
                            details="Gold fact_daily_prices table has 0 rows.",
                            remediation_advice="Execute dbt run to build downstream marts.",
                        )
                    ],
                )

            # 1. Completeness: Mandatory Keys
            mandatory_cols = ["price_fact_id", "security_id", "date_id", "close_price"]
            for col in mandatory_cols:
                null_count = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} IS NULL").fetchone()[0]
                fail_pct = round((null_count / total_records) * 100, 2)
                status = CheckStatus.PASSED if null_count == 0 else CheckStatus.FAILED
                results.append(
                    CheckResult(
                        rule_name=f"not_null_{col}",
                        category=RuleCategory.COMPLETENESS,
                        target_table=table_name,
                        status=status,
                        records_scanned=total_records,
                        records_failed=null_count,
                        failure_rate_pct=fail_pct,
                        details=f"Column {col} has {null_count} nulls.",
                        remediation_advice="Check source ingestion and surrogate key generation in dbt staging." if null_count > 0 else "N/A",
                    )
                )

            # 2. Validity: OHLC Price Boundary Assertions
            # Rule: close_price > 0
            neg_close = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE close_price <= 0").fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="positive_close_price",
                    category=RuleCategory.VALIDITY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if neg_close == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=neg_close,
                    failure_rate_pct=round((neg_close / total_records) * 100, 2),
                    details=f"Found {neg_close} non-positive close prices.",
                    remediation_advice="Review upstream stock split or negative price anomalies." if neg_close > 0 else "N/A",
                )
            )

            # Rule: high >= low
            inverted_ohlc = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE high_price < low_price").fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="high_gte_low",
                    category=RuleCategory.VALIDITY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if inverted_ohlc == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=inverted_ohlc,
                    failure_rate_pct=round((inverted_ohlc / total_records) * 100, 2),
                    details=f"Found {inverted_ohlc} records where high_price < low_price.",
                    remediation_advice="Inverted high/low indicates raw tick corruption." if inverted_ohlc > 0 else "N/A",
                )
            )

            # Rule: high >= close and low <= close
            boundary_violations = con.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE close_price > high_price * 1.0001 OR close_price < low_price * 0.9999
            """).fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="close_within_high_low",
                    category=RuleCategory.VALIDITY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if boundary_violations == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=boundary_violations,
                    failure_rate_pct=round((boundary_violations / total_records) * 100, 2),
                    details=f"Found {boundary_violations} records where close is outside high/low bounds.",
                    remediation_advice="Enforce boundary clamp in Silver staging layer." if boundary_violations > 0 else "N/A",
                )
            )

            # 3. Technical Indicator Sanity: RSI 14 (Must be between 0 and 100)
            rsi_violations = con.execute(f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE rsi_14 IS NOT NULL AND (rsi_14 < 0 OR rsi_14 > 100)
            """).fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="rsi_bounds_0_to_100",
                    category=RuleCategory.VALIDITY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if rsi_violations == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=rsi_violations,
                    failure_rate_pct=round((rsi_violations / total_records) * 100, 2),
                    details=f"Found {rsi_violations} records with RSI outside [0, 100].",
                    remediation_advice="Review RSI calculation formula in int_stock_technicals.sql." if rsi_violations > 0 else "N/A",
                )
            )

            # 4. Bollinger Bands Structure: Upper >= Middle >= Lower
            bb_violations = con.execute(f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE bollinger_upper IS NOT NULL 
                  AND (bollinger_upper < bollinger_middle OR bollinger_middle < bollinger_lower)
            """).fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="bollinger_band_hierarchy",
                    category=RuleCategory.CONSISTENCY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if bb_violations == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=bb_violations,
                    failure_rate_pct=round((bb_violations / total_records) * 100, 2),
                    details=f"Found {bb_violations} records where Bollinger Upper < Middle or Middle < Lower.",
                    remediation_advice="Verify standard deviation multiplier in int_stock_technicals.sql." if bb_violations > 0 else "N/A",
                )
            )

            # 5. Statistical Anomaly: Intraday Return Outliers (> 15% absolute single-day return)
            extreme_returns = con.execute(f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE daily_return_pct IS NOT NULL AND ABS(daily_return_pct) > 0.15
            """).fetchone()[0]
            # Flag extreme return as WARNING (could be real circuit breaker event, e.g. corporate action)
            status_ret = CheckStatus.PASSED if extreme_returns == 0 else CheckStatus.WARNING
            results.append(
                CheckResult(
                    rule_name="extreme_daily_return_anomaly",
                    category=RuleCategory.ANOMALY,
                    target_table=table_name,
                    status=status_ret,
                    records_scanned=total_records,
                    records_failed=extreme_returns,
                    failure_rate_pct=round((extreme_returns / total_records) * 100, 2),
                    details=f"Found {extreme_returns} bars with absolute return > 15% (circuit limit breach).",
                    remediation_advice="Verify stock split, bonus issue, or market circuit breaker." if extreme_returns > 0 else "N/A",
                )
            )

            # 6. Volume Anomaly: Flag zero volume on active trading days
            zero_vol = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE volume = 0").fetchone()[0]
            status_vol = CheckStatus.PASSED if zero_vol == 0 else CheckStatus.WARNING
            results.append(
                CheckResult(
                    rule_name="zero_volume_trading_day",
                    category=RuleCategory.ANOMALY,
                    target_table=table_name,
                    status=status_vol,
                    records_scanned=total_records,
                    records_failed=zero_vol,
                    failure_rate_pct=round((zero_vol / total_records) * 100, 2),
                    details=f"Found {zero_vol} records with 0 traded volume on active days.",
                    remediation_advice="Check if security was suspended from trading." if zero_vol > 0 else "N/A",
                )
            )

            # 7. Timeliness: Freshness Check (Max trade date within 5 calendar days of today)
            max_date = con.execute(f"SELECT MAX(trade_date) FROM {table_name}").fetchone()[0]
            if max_date is not None:
                days_stale = (date.today() - max_date).days
                status_fresh = CheckStatus.PASSED if days_stale <= 5 else CheckStatus.WARNING
                results.append(
                    CheckResult(
                        rule_name="data_freshness_latency",
                        category=RuleCategory.TIMELINESS,
                        target_table=table_name,
                        status=status_fresh,
                        records_scanned=total_records,
                        records_failed=1 if status_fresh != CheckStatus.PASSED else 0,
                        failure_rate_pct=0.0 if status_fresh == CheckStatus.PASSED else 100.0,
                        details=f"Latest trade date is {max_date} ({days_stale} days old).",
                        remediation_advice="Trigger daily market close ingestion DAG." if status_fresh != CheckStatus.PASSED else "N/A",
                    )
                )

        finally:
            con.close()

        passed_count = sum(1 for r in results if r.status == CheckStatus.PASSED)
        warning_count = sum(1 for r in results if r.status == CheckStatus.WARNING)
        failed_count = sum(1 for r in results if r.status == CheckStatus.FAILED)
        total_checks = len(results)

        # Quality score formula: 100% - penalty (100% per fail, 20% per warning)
        score = max(0.0, round(((passed_count + 0.8 * warning_count) / total_checks) * 100, 2))

        return LayerAuditSummary(
            layer_name="GOLD",
            target_table=table_name,
            total_checks=total_checks,
            passed_checks=passed_count,
            warning_checks=warning_count,
            failed_checks=failed_count,
            quality_score_pct=score,
            results=results,
        )

    def audit_silver_staging_stocks(self) -> LayerAuditSummary:
        """Audits Silver Staging table: main_staging.stg_stocks."""
        con = self._get_connection()
        table_name = "main_staging.stg_stocks"
        results: List[CheckResult] = []

        try:
            total_records = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            if total_records == 0:
                return LayerAuditSummary(
                    layer_name="SILVER",
                    target_table=table_name,
                    total_checks=1,
                    passed_checks=0,
                    warning_checks=0,
                    failed_checks=1,
                    quality_score_pct=0.0,
                    results=[],
                )

            # 1. Uniqueness: stock_price_id
            pk_dups = con.execute(f"""
                SELECT COUNT(*) FROM (
                    SELECT stock_price_id, COUNT(*) FROM {table_name} GROUP BY stock_price_id HAVING COUNT(*) > 1
                )
            """).fetchone()[0]
            results.append(
                CheckResult(
                    rule_name="unique_stock_price_id",
                    category=RuleCategory.CONSISTENCY,
                    target_table=table_name,
                    status=CheckStatus.PASSED if pk_dups == 0 else CheckStatus.FAILED,
                    records_scanned=total_records,
                    records_failed=pk_dups,
                    failure_rate_pct=round((pk_dups / total_records) * 100, 2),
                    details=f"Found {pk_dups} duplicate primary keys.",
                    remediation_advice="Review SHA-256 natural key hash generation in staging." if pk_dups > 0 else "N/A",
                )
            )

            # 2. Null Checks
            for col in ["symbol", "trade_date", "close_price", "volume"]:
                nulls = con.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} IS NULL").fetchone()[0]
                results.append(
                    CheckResult(
                        rule_name=f"staging_not_null_{col}",
                        category=RuleCategory.COMPLETENESS,
                        target_table=table_name,
                        status=CheckStatus.PASSED if nulls == 0 else CheckStatus.FAILED,
                        records_scanned=total_records,
                        records_failed=nulls,
                        failure_rate_pct=round((nulls / total_records) * 100, 2),
                        details=f"Found {nulls} nulls in {col}.",
                        remediation_advice="Check source parquet file for missing values." if nulls > 0 else "N/A",
                    )
                )

        finally:
            con.close()

        passed_count = sum(1 for r in results if r.status == CheckStatus.PASSED)
        warning_count = sum(1 for r in results if r.status == CheckStatus.WARNING)
        failed_count = sum(1 for r in results if r.status == CheckStatus.FAILED)
        total_checks = len(results)
        score = max(0.0, round(((passed_count + 0.8 * warning_count) / total_checks) * 100, 2))

        return LayerAuditSummary(
            layer_name="SILVER",
            target_table=table_name,
            total_checks=total_checks,
            passed_checks=passed_count,
            warning_checks=warning_count,
            failed_checks=failed_count,
            quality_score_pct=score,
            results=results,
        )

    def run_full_suite(self) -> Dict[str, Any]:
        """Runs quality audit across Silver and Gold layers and calculates composite score."""
        gold_summary = self.audit_gold_fact_daily_prices()
        silver_summary = self.audit_silver_staging_stocks()

        total_checks = gold_summary.total_checks + silver_summary.total_checks
        passed_checks = gold_summary.passed_checks + silver_summary.passed_checks
        warning_checks = gold_summary.warning_checks + silver_summary.warning_checks
        failed_checks = gold_summary.failed_checks + silver_summary.failed_checks

        composite_score = round((gold_summary.quality_score_pct * 0.6) + (silver_summary.quality_score_pct * 0.4), 2)
        overall_status = CheckStatus.PASSED if failed_checks == 0 else CheckStatus.FAILED

        return {
            "overall_status": overall_status.value,
            "composite_quality_score_pct": composite_score,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "warning_checks": warning_checks,
            "failed_checks": failed_checks,
            "layers": {
                "gold": gold_summary.model_dump(),
                "silver": silver_summary.model_dump(),
            },
        }
