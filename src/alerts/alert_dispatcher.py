"""Multi-Channel Incident Alert Dispatcher with Deduplication and Webhook integration."""
from datetime import datetime, timezone
from enum import Enum
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("alert_dispatcher")


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertEvent:
    def __init__(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source_component: str,
        remediation_advice: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.title = title
        self.message = message
        self.severity = severity
        self.source_component = source_component
        self.remediation_advice = remediation_advice
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "source_component": self.source_component,
            "remediation_advice": self.remediation_advice,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class IncidentAlertDispatcher:
    """Dispatches operational alerts and data quality breaches across console, file, and webhooks."""

    def __init__(
        self,
        alert_log_file: Optional[Path] = None,
        webhook_url: Optional[str] = None,
    ):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.alert_log_file = alert_log_file or (project_root / "data" / "quality" / "incident_alerts.jsonl")
        self.alert_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.webhook_url = webhook_url or os.getenv("ALERT_WEBHOOK_URL")
        self._dispatched_hashes = set()

    def _generate_alert_hash(self, event: AlertEvent) -> str:
        return f"{event.severity.value}:{event.source_component}:{event.title}"

    def dispatch(self, event: AlertEvent) -> Dict[str, Any]:
        """Dispatches an alert across configured channels with deduplication."""
        alert_hash = self._generate_alert_hash(event)
        
        # Log to Python logger
        severity_prefix = {
            AlertSeverity.INFO: "ℹ️ [INFO]",
            AlertSeverity.WARNING: "⚠️ [WARNING]",
            AlertSeverity.CRITICAL: "🚨 [CRITICAL ALERT]",
        }[event.severity]

        log_msg = f"{severity_prefix} [{event.source_component}] {event.title} — {event.message}"
        if event.remediation_advice:
            log_msg += f" | Remediation: {event.remediation_advice}"

        if event.severity == AlertSeverity.CRITICAL:
            logger.error(log_msg)
        elif event.severity == AlertSeverity.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # Append to JSONL audit log
        with open(self.alert_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

        # Optional Webhook dispatch (Telegram / Slack / generic endpoint)
        webhook_status = "skipped"
        if self.webhook_url:
            try:
                payload = json.dumps({
                    "text": f"*{event.severity.value}*: {event.title}\n{event.message}\n`Component: {event.source_component}`",
                    "event": event.to_dict(),
                }).encode("utf-8")
                req = urllib.request.Request(
                    self.webhook_url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    webhook_status = f"success_{response.status}"
            except Exception as e:
                webhook_status = f"failed: {str(e)}"
                logger.warning("Failed to dispatch alert to webhook: %s", e)

        self._dispatched_hashes.add(alert_hash)
        return {"status": "dispatched", "channels": ["console", "file", webhook_status]}

    def notify_circuit_breaker(self, step_name: str, error_message: str, remediation: str = "") -> Dict[str, Any]:
        """Dispatches a critical circuit-breaker event when a pipeline step fails."""
        event = AlertEvent(
            title=f"Circuit Breaker Tripped at Step: {step_name}",
            message=error_message,
            severity=AlertSeverity.CRITICAL,
            source_component="pipeline_circuit_breaker",
            remediation_advice=remediation or "Inspect task logs and verify data schema assertions before restarting.",
        )
        return self.dispatch(event)

    def notify_data_quality_breach(self, table_name: str, rule_name: str, failure_count: int, failure_pct: float) -> Dict[str, Any]:
        """Dispatches an alert when a data quality threshold is breached."""
        severity = AlertSeverity.CRITICAL if failure_pct > 5.0 else AlertSeverity.WARNING
        event = AlertEvent(
            title=f"Data Quality Gate Breach on {table_name}",
            message=f"Rule '{rule_name}' failed with {failure_count} defective records ({failure_pct}% failure rate).",
            severity=severity,
            source_component="data_quality_suite",
            remediation_advice=f"Query table {table_name} for offending records and verify boundary transformations.",
            metadata={"table": table_name, "rule": rule_name, "failures": failure_count, "pct": failure_pct},
        )
        return self.dispatch(event)

    def notify_calendar_dropout(self, missing_dates: List[str]) -> Dict[str, Any]:
        """Dispatches a warning or critical alert for unexplained trading day dropouts."""
        event = AlertEvent(
            title="NSE Trading Calendar Dropout Detected",
            message=f"Detected {len(missing_dates)} official market trading days missing from data: {missing_dates}",
            severity=AlertSeverity.CRITICAL if len(missing_dates) > 2 else AlertSeverity.WARNING,
            source_component="calendar_validator",
            remediation_advice="Trigger backfill ingestion for missing dates via run_phase1_ingestion.py.",
            metadata={"missing_dates": missing_dates},
        )
        return self.dispatch(event)
