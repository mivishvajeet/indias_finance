"""Phase 4 CLI Orchestrator:
Runs Automated Data Quality Suite, Cross-Layer Lakehouse Reconciliation, and Anomaly Audits.
Generates comprehensive JSON & Markdown Scorecard.
"""
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.quality.dq_suite import DataQualitySuite
from src.quality.reconciliation_auditor import LakehouseReconciliationAuditor
from src.alerts.alert_dispatcher import IncidentAlertDispatcher, AlertEvent, AlertSeverity

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase4_runner")


def run_phase4_audit():
    print("=" * 90)
    print(" 🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL — PHASE 4 DATA QUALITY AUDIT")
    print("=" * 90)

    dispatcher = IncidentAlertDispatcher()
    dq_suite = DataQualitySuite()
    reconciliation_auditor = LakehouseReconciliationAuditor()

    # 1. Run Lakehouse Cross-Layer Reconciliation
    print("\n--- [STEP 1] Running Cross-Layer Lakehouse Reconciliation Audit ---")
    rec_result = reconciliation_auditor.reconcile_stocks()
    print(reconciliation_auditor.generate_markdown_summary())

    # 2. Run Data Quality Suite across Silver & Gold
    print("\n--- [STEP 2] Running Automated Data Quality Rule Assertions ---")
    dq_summary = dq_suite.run_full_suite()

    print(f"\n📊 Overall Quality Status:      {dq_summary['overall_status']}")
    print(f"🎯 Composite Quality Score:     {dq_summary['composite_quality_score_pct']}%")
    print(f"✅ Total Assertions Passed:    {dq_summary['passed_checks']} / {dq_summary['total_checks']}")
    print(f"⚠️  Total Warnings Detected:    {dq_summary['warning_checks']}")
    print(f"❌ Total Critical Failures:    {dq_summary['failed_checks']}")

    print("\n" + "-" * 90)
    print(f"{'RULE NAME':<32} | {'LAYER':<7} | {'CATEGORY':<14} | {'SCANNED':<8} | {'FAILS':<6} | {'STATUS'}")
    print("-" * 90)

    all_results = []
    for layer_key, layer_data in dq_summary["layers"].items():
        for res in layer_data["results"]:
            all_results.append(res)
            status_symbol = "🟢 PASS" if res["status"] == "PASSED" else ("🟡 WARN" if res["status"] == "WARNING" else "🔴 FAIL")
            print(f"{res['rule_name']:<32} | {layer_data['layer_name']:<7} | {str(res['category'].value if hasattr(res['category'], 'value') else res['category']):<14} | {res['records_scanned']:<8} | {res['records_failed']:<6} | {status_symbol}")

    # 3. Check for Failures and Trigger Alert Dispatcher
    critical_fails = [r for r in all_results if r["status"] == "FAILED"]
    if critical_fails:
        print(f"\n🚨 ALERT: {len(critical_fails)} critical data quality check(s) failed!")
        for fail in critical_fails:
            dispatcher.notify_data_quality_breach(
                table_name=fail["target_table"],
                rule_name=fail["rule_name"],
                failure_count=fail["records_failed"],
                failure_pct=fail["failure_rate_pct"],
            )

    # 4. Generate Markdown Scorecard Document
    quality_dir = PROJECT_ROOT / "data" / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = quality_dir / "dq_report.json"
    scorecard_md_path = quality_dir / "dq_scorecard.md"

    # Export JSON
    with open(report_json_path, "w", encoding="utf-8") as f:
        full_report = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "data_quality_summary": dq_summary,
            "reconciliation": rec_result.model_dump(),
        }
        json.dump(full_report, f, indent=2, default=str)

    # Export Markdown
    with open(scorecard_md_path, "w", encoding="utf-8") as f:
        f.write("# 🇮🇳 India Finance Lakehouse Data Quality Scorecard\n\n")
        f.write(f"**Audit Timestamp:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`  \n")
        f.write(f"**Overall Status:** `{'🟢 PASSED' if dq_summary['overall_status'] == 'PASSED' else '🔴 FAILED'}`  \n")
        f.write(f"**Composite Data Quality Score:** `{dq_summary['composite_quality_score_pct']}%`  \n\n")
        
        f.write("## 1. Cross-Layer Lakehouse Reconciliation\n\n")
        f.write(reconciliation_auditor.generate_markdown_summary())
        f.write("\n\n## 2. Layer-by-Layer Rule Audit Matrix\n\n")
        f.write("| Rule Name | Lakehouse Layer | Category | Records Scanned | Failures | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for res in all_results:
            status_str = "🟢 PASS" if res["status"] == "PASSED" else ("🟡 WARN" if res["status"] == "WARNING" else "🔴 FAIL")
            f.write(f"| `{res['rule_name']}` | `{res['target_table']}` | {res['category'].value if hasattr(res['category'], 'value') else res['category']} | {res['records_scanned']:,} | {res['records_failed']} | {status_str} |\n")
        
        f.write("\n\n## 3. Remediation Guidelines\n\n")
        for res in all_results:
            if res["status"] != "PASSED" and res["remediation_advice"] != "N/A":
                f.write(f"- **{res['rule_name']}**: {res['details']} ➔ *Remediation: {res['remediation_advice']}*\n")
        
        f.write("\n---\n*India Finance Intelligence Terminal — Enterprise QA & Data Quality Gate*\n")

    print(f"\n[+] Data Quality Scorecard exported to:\n    - JSON: {report_json_path}\n    - Markdown: {scorecard_md_path}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_phase4_audit()
