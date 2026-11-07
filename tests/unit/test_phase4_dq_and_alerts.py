"""Unit and Integration Tests for Phase 4 Data Quality Suite, Reconciliation, and Alerts."""
import json
from pathlib import Path
import pytest
import duckdb

from src.quality.dq_rules import CheckStatus, RuleCategory
from src.quality.dq_suite import DataQualitySuite
from src.quality.reconciliation_auditor import LakehouseReconciliationAuditor
from src.alerts.alert_dispatcher import IncidentAlertDispatcher, AlertEvent, AlertSeverity


class TestDataQualitySuite:
    """Tests the automated rule assertions on DuckDB lakehouse tables."""

    def test_gold_fact_audit_baseline(self):
        suite = DataQualitySuite()
        summary = suite.audit_gold_fact_daily_prices()

        assert summary.total_checks >= 10
        assert summary.failed_checks == 0
        assert summary.quality_score_pct >= 95.0
        assert summary.target_table == "main_marts.fact_daily_prices"

    def test_silver_staging_audit_baseline(self):
        suite = DataQualitySuite()
        summary = suite.audit_silver_staging_stocks()

        assert summary.total_checks >= 5
        assert summary.failed_checks == 0
        assert summary.quality_score_pct >= 95.0
        assert summary.target_table == "main_staging.stg_stocks"

    def test_suite_detects_simulated_boundary_defect(self, tmp_path):
        """Verify the DQ suite catches an artificially injected negative close price in a mock warehouse."""
        mock_db = tmp_path / "mock_curated.duckdb"
        con = duckdb.connect(str(mock_db))
        con.execute("CREATE SCHEMA main_marts;")
        con.execute("""
            CREATE TABLE main_marts.fact_daily_prices (
                price_fact_id VARCHAR,
                security_id VARCHAR,
                date_id INTEGER,
                trade_date DATE,
                close_price DOUBLE,
                high_price DOUBLE,
                low_price DOUBLE,
                volume BIGINT,
                rsi_14 DOUBLE,
                bollinger_upper DOUBLE,
                bollinger_middle DOUBLE,
                bollinger_lower DOUBLE,
                daily_return_pct DOUBLE
            );
            INSERT INTO main_marts.fact_daily_prices VALUES
            ('1', 'S1', 20261101, '2026-11-01', -50.0, 100.0, 90.0, 1000, 50.0, 110.0, 100.0, 90.0, 0.01),
            ('2', 'S1', 20261102, '2026-11-02', 105.0, 100.0, 110.0, 1000, 105.0, 110.0, 100.0, 90.0, 0.05);
        """)
        con.close()

        suite = DataQualitySuite(warehouse_path=mock_db)
        summary = suite.audit_gold_fact_daily_prices()

        assert summary.failed_checks > 0
        # Positive price rule should fail
        pos_rule = next(r for r in summary.results if r.rule_name == "positive_close_price")
        assert pos_rule.status == CheckStatus.FAILED
        assert pos_rule.records_failed == 1

        # High >= low rule should fail
        high_low_rule = next(r for r in summary.results if r.rule_name == "high_gte_low")
        assert high_low_rule.status == CheckStatus.FAILED
        assert high_low_rule.records_failed == 1

        # RSI rule should fail (105.0 > 100)
        rsi_rule = next(r for r in summary.results if r.rule_name == "rsi_bounds_0_to_100")
        assert rsi_rule.status == CheckStatus.FAILED
        assert rsi_rule.records_failed == 1


class TestCrossLayerReconciliation:
    """Tests cross-layer reconciliation between raw lakehouse and curated marts."""

    def test_reconciliation_exactness(self):
        auditor = LakehouseReconciliationAuditor()
        result = auditor.reconcile_stocks()

        assert result.bronze_raw_count >= result.silver_staged_count
        assert result.silver_staged_count == result.gold_fact_count
        assert result.gold_coverage_pct == 100.0
        assert result.is_reconciled is True
        assert len(result.reconciliation_notes) >= 3

    def test_markdown_summary_generation(self):
        auditor = LakehouseReconciliationAuditor()
        md = auditor.generate_markdown_summary()

        assert "Cross-Layer Lakehouse Reconciliation Audit" in md
        assert "Bronze (Raw Lakehouse)" in md
        assert "Silver (Cleaned Staging)" in md
        assert "Gold (Curated Star Marts)" in md
        assert "🟢 VERIFIED" in md


class TestIncidentAlertDispatcher:
    """Tests enterprise alert dispatching, audit logging, and circuit-breaker triggers."""

    def test_dispatch_and_audit_log(self, tmp_path):
        log_file = tmp_path / "test_alerts.jsonl"
        dispatcher = IncidentAlertDispatcher(alert_log_file=log_file)

        event = AlertEvent(
            title="Test Quality Gate Alert",
            message="Unit test simulated defect",
            severity=AlertSeverity.WARNING,
            source_component="unit_test",
            remediation_advice="No action required.",
        )
        res = dispatcher.dispatch(event)

        assert res["status"] == "dispatched"
        assert log_file.exists()

        with open(log_file, "r") as f:
            lines = [json.loads(line) for line in f]

        assert len(lines) == 1
        assert lines[0]["title"] == "Test Quality Gate Alert"
        assert lines[0]["severity"] == "WARNING"

    def test_circuit_breaker_notification(self, tmp_path):
        log_file = tmp_path / "test_circuit_breaker.jsonl"
        dispatcher = IncidentAlertDispatcher(alert_log_file=log_file)

        res = dispatcher.notify_circuit_breaker(
            step_name="dbt_test_quality_gate",
            error_message="Unique constraint failed on fact_daily_prices",
        )
        assert res["status"] == "dispatched"

        with open(log_file, "r") as f:
            entry = json.loads(f.readline())
        assert entry["severity"] == "CRITICAL"
        assert "Circuit Breaker Tripped" in entry["title"]

    def test_calendar_dropout_notification(self, tmp_path):
        log_file = tmp_path / "test_calendar_dropout.jsonl"
        dispatcher = IncidentAlertDispatcher(alert_log_file=log_file)

        res = dispatcher.notify_calendar_dropout(["2026-11-04", "2026-11-05", "2026-11-06"])
        assert res["status"] == "dispatched"

        with open(log_file, "r") as f:
            entry = json.loads(f.readline())
        assert entry["severity"] == "CRITICAL"
        assert len(entry["metadata"]["missing_dates"]) == 3
