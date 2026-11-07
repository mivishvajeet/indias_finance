# 🇮🇳 India Finance Intelligence Terminal

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Storage: Lakehouse](https://img.shields.io/badge/storage-Hive%20Parquet%20Bronze-orange.svg)](data/lakehouse/)
[![Tests: Passing](https://img.shields.io/badge/tests-9%2F9%20passing-brightgreen.svg)](tests/)
[![Idempotency: SHA--256](https://img.shields.io/badge/idempotency-100%25%20verified-success.svg)](src/storage/lakehouse.py)

An automated, production-grade financial data intelligence pipeline and Bloomberg-style terminal for Indian capital markets (NSE equities, Nifty 50, Bank Nifty, RBI macro indicators, AMFI mutual funds, and FII/DII flows). 

Designed with a **Data Quality First** engineering mindset, built for local execution at **₹0 infrastructure cost** using Docker, Airflow, MinIO/Local Lakehouse, DuckDB, and dbt.

---

## 🏛️ Medallion Architecture

- **Bronze (Raw)**: Immutable, Hive-partitioned Parquet files (`year=YYYY/month=MM/day=DD/`) with SHA-256 batch fingerprints and JSON manifests for 100% idempotent replays.
- **Silver (Staging)**: Deduplicated, timezone-adjusted (IST), split-adjusted, schema-validated tables.
- **Gold (Curated)**: Star Schema modeled via dbt-duckdb (fact tables for prices, flows, macro, NAV; dimension tables for date, securities, funds).

---

## 🚀 Phase 1 Implementation Summary

- **Resilient Connectors**: `BasePublicClient` featuring rotating User-Agent headers, exponential backoff, rate limiting, and hermetic offline fallback generators.
- **Schema Contracts**: Pydantic v2 schemas (`DailyStockRawRecord`, `MacroIndicatorRawRecord`) rejecting invalid types, negative volumes, and computing deterministic per-row hashes.
- **Lakehouse Bronze Layer**: `LakehouseRawStorage` supporting Hive partitioning and automated idempotency skipping.
- **CLI Runner**: `scripts/run_phase1_ingestion.py` for automated batch ingestion.
- **Automated Tests**: 9/9 pytest test cases covering schema contracts, boundary values, and partition manifests.

---

## 🛠️ Quickstart

### 1. Installation
```bash
git clone <repo>
cd indias-finance
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run Ingestion Pipeline
```bash
# Ingest 14 days of stocks + macro data
python scripts/run_phase1_ingestion.py --days 14

# Ingest specific tickers
python scripts/run_phase1_ingestion.py --days 30 --symbols ^NSEI RELIANCE.NS TCS.NS HDFCBANK.NS
```

### 3. Run Test Suite
```bash
pytest -v tests/
```

---

## ⚠️ Disclaimer
*This project is built strictly for educational, data engineering, and portfolio demonstration purposes. It does not constitute financial or investment advice.*

---

## 📅 Phase 2 Implementation Summary: Airflow, Staging & Calendar Validation

- **NSE Trading Calendar Validator**: `src/quality/calendar_validator.py` cross-checks date sequences against `config/trading_holidays_nse.yaml` to differentiate genuine exchange holidays (e.g., Diwali, Republic Day) from silent pipeline dropouts.
- **Silver Staging Manager**: `src/storage/staging_manager.py` deduplicates records via `(symbol, trade_date)`, applies price sanity boundaries (`high >= low`, `high >= max(open, close)`), identifies potential corporate splits/bonuses, and populates DuckDB staging tables.
- **Airflow Orchestration**: `docker/docker-compose.yml`, `dags/dag_daily_market_ingest.py` (daily 17:30 IST market close DAG), and `dags/dag_macro_monthly.py`.
- **CLI Staging Runner**: `scripts/run_phase2_staging.py` for direct local staging promotion and verification.
- **Automated Tests**: 15/15 tests passing across Phase 1 & 2.
