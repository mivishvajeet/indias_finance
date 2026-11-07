# 📁 India Finance Intelligence Terminal — Complete File Inventory & Forensic Audit

> **Scope**: Exhaustive forensic audit of every active directory, module, script, model, test, and configuration file in the **India Finance Intelligence Terminal** repository.  
> **Audited Date**: 2026-11-07  
> **Architecture**: Medallion Lakehouse (Bronze ➔ Silver ➔ Gold) × Data Observability × Local AI × Streamlit Terminal  

---

## 📑 Table of Contents
1. [Architectural Overview & Directory Hierarchy](#1-architectural-overview--directory-hierarchy)
2. [Data Ingestion & Extraction Layer (`src/ingestion/`)](#2-data-ingestion--extraction-layer-srcingestion)
3. [Lakehouse Storage & Staging Management (`src/storage/`)](#3-lakehouse-storage--staging-management-srcstorage)
4. [Data Quality & Circuit Breaker Suite (`src/quality/`, `src/alerts/`)](#4-data-quality--circuit-breaker-suite-srcquality-srcalerts)
5. [Analytics & Quantitative Risk Engine (`src/analytics/`)](#5-analytics--quantitative-risk-engine-srcanalytics)
6. [dbt Dimensional Transformation Models (`finance_dbt/`)](#6-dbt-dimensional-transformation-models-finance_dbt)
7. [Central Data Access & Repositories (`data_access/`)](#7-central-data-access--repositories-data_access)
8. [Platform Service Layer (`services/`)](#8-platform-service-layer-services)
9. [AI Engine & Safe Text-to-SQL Assistant (`ai/`)](#9-ai-engine--safe-text-to-sql-assistant-ai)
10. [Streamlit Terminal UI & Workspaces (`ui/`)](#10-streamlit-terminal-ui--workspaces-ui)
11. [Pipeline Automation & Execution Entrypoints (`scripts/`)](#11-pipeline-automation--execution-entrypoints-scripts)
12. [Automated Verification & Test Suites (`tests/`)](#12-automated-verification--test-suites-tests)
13. [Configuration & Reference Dictionaries (`config/`)](#13-configuration--reference-dictionaries-config)
14. [Orchestration DAGs (`dags/`, `docker/`, `ci/`)](#14-orchestration-dags-dags-docker-ci)
15. [Technical Debt, Dead Code, and Forensic Findings](#15-technical-debt-dead-code-and-forensic-findings)

---

## 1. Architectural Overview & Directory Hierarchy

The repository organizes financial data engineering across clear architectural boundaries:

```
financeAI/
├── config/                  # Static market YAMLs (NSE holidays, Nifty50 universe, Macro series)
├── dags/                    # Apache Airflow DAG definitions for automated scheduling
├── data/
│   ├── lakehouse/raw/       # Bronze Layer: Hive-partitioned Parquet files + SHA-256 manifests
│   ├── lakehouse/staging/   # Silver staging Parquet dumps
│   ├── quality/             # Automated DQ scorecard JSONs and Markdown reports
│   └── warehouse/           # Gold Layer: DuckDB in-process analytical stores (curated.duckdb)
├── data_access/             # DuckDB connection pooling and repository CRUD operations
├── docker/                  # Local containerization (Docker Compose for Airflow & dependencies)
├── finance_dbt/             # dbt-duckdb transformation project (13 models, 3 macros, 2 seeds)
├── services/                # Decoupled business logic & analytics services for UI
├── src/
│   ├── alerts/              # Incident notification dispatchers and alert formats
│   ├── analytics/           # Financial risk engine (Sharpe, Sortino, CAGR, Drawdown)
│   ├── ingestion/           # NSE equities, AMFI mutual funds, and RBI/MOSPI extractors
│   ├── quality/             # Data contract assertions, calendar validator, reconciliation auditor
│   └── storage/             # Lakehouse partition writer & Silver staging deduplicator
├── tests/                   # 45 Pytest automated tests (Unit, AI safety, DQ, Risk, Services)
└── ui/                      # Bloomberg-styled Streamlit financial terminal (11 modular workspaces)
```

---

## 2. Data Ingestion & Extraction Layer (`src/ingestion/`)

### `src/ingestion/base_client.py`
- **Purpose**: Abstract base class establishing standard retry loops, backoff delays, User-Agent rotation, and session pooling for all external network requests.
- **Why It Exists**: External financial endpoints (NSE, AMFI, RBI) enforce strict rate limits and bot detection; this module standardizes fault-tolerant network interaction.
- **Imports**: `logging`, `random`, `time`, `typing`, `requests`, `urllib3`.
- **Classes**:
  - `BaseIngestionClient`: Base client providing `_fetch_with_retry(url, headers, params, max_retries, backoff_factor)` and `_get_random_user_agent()`.
- **Key Functionality**:
  - `_get_random_user_agent()`: Rotates through 6 modern browser User-Agent strings (Chrome, Firefox, Safari on Windows/macOS).
  - `_fetch_with_retry()`: Implements exponential backoff: `backoff * 2^(attempt - 1)`. Handles HTTP 429, 500, 502, 503, 504.
- **Data In/Out**: Reads HTTP payloads; returns `requests.Response` or raises `RuntimeError`.
- **Dependencies**: Inherited by `NseStockClient`, `MacroClient`, `AmfiMfClient`.
- **What Breaks If Removed**: All network extraction fails immediately.
- **Business Rule**: Enforces maximum 3 retries with random jitter to avoid thundering-herd effect against public government servers.

### `src/ingestion/nse_stocks.py`
- **Purpose**: Extracts daily OHLCV trading bars for NSE-listed securities via `yfinance` with fallback synthetic generation.
- **Why It Exists**: Ingests primary equity price series for Indian blue-chips (Nifty 50 constituents) and indices (^NSEI).
- **Imports**: `datetime`, `pathlib`, `pandas`, `yfinance`, `src.ingestion.base_client`, `src.ingestion.models`.
- **Classes**:
  - `NseStockClient`: Client managing equity data extraction.
- **Key Functionality**:
  - `fetch_daily_bars(symbol, start_date, end_date)`: Fetches price bars, sanitizes column names (`Open`, `High`, `Low`, `Close`, `Volume`), validates positive volume, and returns a validated list of `DailyStockBar` records.
  - `_generate_fallback_bars()`: Deterministic geometric Brownian motion generator ensuring tests and offline demos never crash if Yahoo Finance API is rate-limited or blocked.
- **Data In/Out**: Queries yfinance; outputs list of `DailyStockBar` domain objects.
- **Called By**: `scripts/run_phase1_ingestion.py`, `dags/dag_daily_market_ingest.py`.
- **What Breaks If Removed**: Bronze equity data cannot be refreshed.
- **Business Rule**: Appends `.NS` ticker suffix for NSE listings; ensures `high >= low` and `volume >= 0`.

### `src/ingestion/macro_client.py`
- **Purpose**: Extracts macroeconomic indicators from Reserve Bank of India (RBI) and MOSPI datasets.
- **Why It Exists**: Ingests monetary policy (Repo Rate, Reverse Repo), inflation (CPI, WPI), and currency exchange (USD/INR).
- **Imports**: `datetime`, `pandas`, `src.ingestion.base_client`, `src.ingestion.models`.
- **Classes**:
  - `MacroClient`: Ingestion client for macro indicators.
- **Key Functionality**:
  - `fetch_indicator(series_id, start_date, end_date)`: Fetches official time-series or falls back to curated baseline datasets (`data/sample/rbi_indicators.csv`).
- **Data In/Out**: Returns list of `MacroIndicatorRecord`.
- **Called By**: `scripts/run_phase1_ingestion.py`, `dags/dag_macro_monthly.py`.
- **What Breaks If Removed**: Macro Intelligence page and macro risk factors lose underlying data.
- **Business Rule**: Standardizes disparate reporting frequencies (Monthly CPI, Bi-Monthly Monetary Policy, Daily FX) into unified observation records.

### `src/ingestion/amfi_mf.py`
- **Purpose**: Ingests Net Asset Value (NAV) historical records for Indian Mutual Funds directly from AMFI (Association of Mutual Funds in India).
- **Why It Exists**: Provides official historical NAV series for top equity mutual fund schemes in India.
- **Imports**: `datetime`, `io`, `requests`, `pandas`, `src.ingestion.base_client`.
- **Classes**:
  - `AmfiMfClient`: Client parsing AMFI NAV text/portal records.
- **Key Functionality**:
  - `fetch_scheme_nav(scheme_code, start_date, end_date)`: Parses semicolon/tab-delimited AMFI official text files; filters target scheme code; extracts `Scheme Code`, `NAV Date`, `Net Asset Value`.
  - Fallback mechanism generates consistent historical NAV series based on official fund inception parameters.
- **Data In/Out**: Returns pandas DataFrame of mutual fund NAV history.
- **Called By**: `scripts/run_phase1_ingestion.py`, `tests/unit/test_phase5_mf_and_risk.py`.
- **What Breaks If Removed**: Mutual Fund Intelligence and Fund Risk Scorecards cannot operate.
- **Business Rule**: Strips invalid non-numeric NAV strings (e.g., "N.A.", closed schemes); validates positive NAV.

### `src/ingestion/models.py`
- **Purpose**: Pydantic/dataclass schema definitions and validation contracts for raw ingested entities.
- **Why It Exists**: Prevents malformed, truncated, or typed-corrupted records from ever entering the Bronze Lakehouse.
- **Classes**:
  - `DailyStockBar`: Validates `symbol` (str), `trade_date` (date), `open_price`, `high_price`, `low_price`, `close_price` (positive floats), `volume` (non-negative int).
  - `MacroIndicatorRecord`: Validates `indicator_code`, `observation_date`, `indicator_value`, `frequency`.
  - `IngestionBatchMetadata`: Encapsulates batch ID, source, timestamp, record count, and SHA-256 fingerprint.
- **Key Functionality**: Computes SHA-256 natural key hash per record: SHA256(symbol + trade_date).
- **What Breaks If Removed**: Strict type assertion fails across ingestion and staging.

---

## 3. Lakehouse Storage & Staging Management (`src/storage/`)

### `src/storage/lakehouse.py`
- **Purpose**: Manages Bronze Lakehouse storage on disk: Hive-style partitioning, Parquet writing, and SHA-256 batch manifest verification.
- **Why It Exists**: Implements idempotent, zero-duplicate storage for all incoming raw batches.
- **Imports**: `hashlib`, `json`, `pathlib`, `datetime`, `pyarrow.parquet`, `pandas`.
- **Classes**:
  - `LakehouseStorage`: Primary partition and storage manager.
- **Key Functionality**:
  - `write_partition(dataset_name, df, partition_date)`: Writes Hive directory path: `data/lakehouse/raw/{dataset}/year=YYYY/month=MM/day=DD/{dataset}_{fingerprint}.parquet`.
  - `compute_batch_fingerprint(df)`: Generates SHA-256 digest over the canonical string representation of sorted rows.
  - `is_duplicate_batch(dataset_name, partition_date, fingerprint)`: Reads partition manifest (`{dataset}_manifest.json`); if fingerprint matches, returns `True` and aborts write.
  - `read_dataset(dataset_name)`: Reads all partitioned Parquet files into a unified Arrow/Pandas DataFrame.
- **Data In/Out**: Takes Pandas DataFrames; writes Parquet files + JSON manifests.
- **Called By**: All ingestion scripts, `staging_manager.py`.
- **What Breaks If Removed**: Raw data idempotency and Lakehouse storage are completely lost.
- **Business Rule**: Enforces idempotent skipping: identical re-runs cost 0 write I/O.

### `src/storage/staging_manager.py`
- **Purpose**: Bridges Bronze raw Parquet into Silver staging tables in DuckDB.
- **Why It Exists**: Applies deduplication on natural keys (`symbol`, `trade_date`), validates basic schema constraints, and loads cleaned staging records into DuckDB.
- **Imports**: `logging`, `pathlib`, `duckdb`, `pandas`, `src.storage.lakehouse`.
- **Classes**:
  - `StagingManager`: Orchestrates Bronze ➔ Silver loading.
- **Key Functionality**:
  - `stage_stocks()`: Reads Bronze equity Parquet; deduplicates on `(symbol, trade_date)` keeping latest; drops rows where `close_price <= 0`; registers `stg_stocks_daily` in DuckDB.
  - `stage_macro()`: Deduplicates on `(indicator_code, observation_date)`; registers `stg_macro_indicators`.
  - `stage_mutual_funds()`: Deduplicates on `(scheme_code, nav_date)`; registers `stg_mf_nav`.
- **Data In/Out**: Reads raw Parquet files; writes to `data/lakehouse/staging/` and loads into `curated.duckdb`.
- **Called By**: `scripts/run_phase2_staging.py`.
- **What Breaks If Removed**: dbt cannot run because source staging tables are not populated.
- **Business Rule**: Prunes duplicate ticks produced during network retries.

---

## 4. Data Quality & Circuit Breaker Suite (`src/quality/`, `src/alerts/`)

### `src/quality/calendar_validator.py`
- **Purpose**: Validates trading day completeness against the official National Stock Exchange of India (NSE) trading calendar.
- **Why It Exists**: Crucial for Indian markets to distinguish between official stock exchange holidays (Diwali Laxmi Pujan, Holi, Independence Day) and catastrophic data extraction dropouts.
- **Imports**: `datetime`, `pathlib`, `yaml`, `pandas`.
- **Classes**:
  - `TradingCalendarValidator`: Calendar audit engine.
- **Key Functionality**:
  - `is_trading_day(dt)`: Returns `False` if weekend (Saturday/Sunday) or present in `config/trading_holidays_nse.yaml`.
  - `audit_trading_coverage(df, date_col, symbol)`: Evaluates expected vs actual trading dates between min and max dates. Flagged missing dates that are NOT official holidays trigger `DATA_DROPOUT_DETECTED`.
- **Data In/Out**: Reads trading holidays YAML; scans DataFrame dates; outputs list of unexplained missing dates.
- **Called By**: `StagingManager`, `DataQualitySuite`, `scripts/run_phase2_qa_deep_audit.py`.
- **What Breaks If Removed**: False-positive alerts will fire on every Indian public holiday, or true missing data will go undetected.
- **Business Rule**: Incorporates Muhurat Trading (special 1-hour evening session on Diwali) and scheduled market closures.

### `src/quality/dq_rules.py`
- **Purpose**: Declarative domain-specific data quality rule specifications.
- **Why It Exists**: Defines standardized contracts for null checks, uniqueness, boundary assertions, and anomaly thresholds across financial datasets.
- **Classes**:
  - `QualityCategory` (Enum): `SCHEMA_VALIDITY`, `COMPLETENESS`, `UNIQUENESS`, `FINANCIAL_BOUNDARIES`, `TEMPORAL_CONSISTENCY`, `RECONCILIATION`.
  - `DQRule`: Dataclass specifying `rule_id`, `name`, `category`, `assertion_fn`, `threshold_pct`, `severity`.
- **Key Functionality**: Contains 17 built-in validation rules covering equity, macro, and mutual fund tables.
- **What Breaks If Removed**: Data quality checks lose standardized evaluation criteria.

### `src/quality/dq_suite.py`
- **Purpose**: Executes the 17-rule automated Data Quality Suite against DuckDB tables and generates the DQ scorecard.
- **Why It Exists**: Acts as the automated circuit breaker before data is certified for institutional analytics.
- **Imports**: `json`, `logging`, `pathlib`, `duckdb`, `pandas`, `src.quality.dq_rules`.
- **Classes**:
  - `DataQualitySuite`: Runner and report generator.
- **Key Functionality**:
  - `run_full_suite()`: Connects to `curated.duckdb`, scans `main_staging` and `main_marts` tables, executes SQL rule queries, calculates `passed_checks`, `failed_checks`, and `composite_quality_score_pct`.
  - `generate_scorecard_markdown()`: Writes `data/quality/dq_scorecard.md`.
  - `save_report_json()`: Writes `data/quality/dq_report.json`.
- **Data In/Out**: Reads DuckDB tables; writes JSON/Markdown audit scorecards.
- **Called By**: `scripts/run_phase4_dq_audit.py`, `ui/pages/data_quality.py`.
- **What Breaks If Removed**: Operational quality observability and circuit breakers fail.
- **Business Rule**: If composite quality score drops below 95%, triggers `CRITICAL` alert to AlertDispatcher.

### `src/quality/reconciliation_auditor.py`
- **Purpose**: Performs strict mathematical cross-layer reconciliation: Bronze Raw ➔ Silver Staging ➔ Gold Marts.
- **Why It Exists**: Ensures zero unexplained data loss across the Medallion Lakehouse.
- **Imports**: `pathlib`, `duckdb`, `src.storage.lakehouse`.
- **Classes**:
  - `LakehouseReconciliationAuditor`: Multi-tier record reconciler.
- **Key Functionality**:
  - `reconcile_stocks()`: Counts Bronze raw records (163) ➔ Silver staged records (133, minus 30 deduplicated ticks) ➔ Gold fact table records (133).
  - Asserts: Retention Rate = Gold Records / Silver Unique Records = 100.0%.
- **Called By**: `scripts/run_phase4_dq_audit.py`, `ui/pages/data_quality.py`.
- **What Breaks If Removed**: Platform cannot prove data integrity between raw files and analytics tables.
- **Business Rule**: Unexplained retention drop below 100% raises immediate reconciliation breach.

### `src/alerts/alert_dispatcher.py`
- **Purpose**: Dispatches structured alerts and persists audit logs when data quality checks or ingestion fail.
- **Why It Exists**: Provides operational incident notification mechanism for data engineers.
- **Imports**: `json`, `logging`, `pathlib`, `datetime`.
- **Classes**:
  - `IncidentAlertDispatcher`: Alert router and incident logger.
- **Key Functionality**:
  - `dispatch_alert(title, severity, source, details)`: Writes structured JSON record to `data/quality/incident_alerts.jsonl` and logs to stdout.
  - Automatically raises incident records for critical pipeline failures.
- **Data In/Out**: Appends JSONL events to `data/quality/incident_alerts.jsonl`.
- **Called By**: `dq_suite.py`, `staging_manager.py`, `scripts/run_phase3_pipeline.py`.
- **What Breaks If Removed**: Incidents fail to notify or persist in operational logs.

---

## 5. Analytics & Quantitative Risk Engine (`src/analytics/`)

### `src/analytics/risk_engine.py`
- **Purpose**: High-precision financial quantitative analytics engine for asset risk profiling.
- **Why It Exists**: Calculates institutional investment metrics for Indian equities and AMFI mutual funds according to rigorous quantitative finance standards.
- **Imports**: `math`, `numpy`, `pandas`.
- **Classes**:
  - `FinancialRiskEngine`: Vectorized risk calculations.
- **Key Functionality**:
  - `calculate_cagr(series, dates)`: Compound Annual Growth Rate:
    `CAGR = (V_final / V_initial) ^ (365.25 / days) - 1`
  - `calculate_annualized_volatility(daily_returns, trading_days=252)`:
    `Volatility = std(R_daily) * sqrt(252)`
  - `calculate_sharpe_ratio(daily_returns, risk_free_rate=0.065)`:
    `Sharpe = (CAGR - R_f) / Volatility`
    Uses the official 6.50% Indian 10-Year Government Bond (G-Sec) benchmark rate.
  - `calculate_sortino_ratio(daily_returns, risk_free_rate=0.065)`:
    `Sortino = (CAGR - R_f) / (Downside_std * sqrt(252))`
  - `calculate_drawdown_series(price_series)`: Computes rolling peak and percentage drawdown:
    `DD_t = (P_t - max_{i <= t}(P_i)) / max_{i <= t}(P_i)`
    and returns `max_drawdown = min(DD)`.
- **Data In/Out**: Takes Pandas Series of prices/NAVs and dates; returns structured risk metrics dictionary.
- **Called By**: `services/risk_service.py`, `services/mutual_fund_service.py`, `tests/unit/test_phase5_mf_and_risk.py`.
- **What Breaks If Removed**: Mutual Fund Intelligence and Risk Analytics lose institutional risk metrics.
- **Business Rule**: Enforces Indian 252-day annualization factor and 6.5% G-Sec risk-free rate.

---

## 6. dbt Dimensional Transformation Models (`finance_dbt/`)

### `finance_dbt/dbt_project.yml` & `profiles.yml`
- **Purpose**: Defines project configuration, model paths, materializations, and DuckDB database connection.
- **Key Configurations**:
  - Target: `dev` ➔ DuckDB at `data/warehouse/curated.duckdb`.
  - Staging models materialize as `view`.
  - Intermediate models materialize as `view`.
  - Dimensions & Facts materialize as `table` in schema `main_marts`.

### Staging Models (`finance_dbt/models/staging/`)
- `stg_stocks.sql`: Selects from DuckDB table `main.stg_stocks_daily`, casts types, and validates non-null columns.
- `stg_macro.sql`: Casts `observation_date` to `DATE`, parses `indicator_value` as `DOUBLE`.
- `stg_mf_nav.sql`: Cleans AMFI scheme codes and casts `nav` to positive `DOUBLE`.

### Intermediate Models (`finance_dbt/models/intermediate/`)
- `int_stock_daily_returns.sql`: Uses `LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date)` to calculate `daily_return_pct`.
- `int_stock_ema_macd.sql`: Computes 12-day and 26-day exponential moving averages, MACD Line (`EMA_12 - EMA_26`), and 9-day signal line.
- `int_stock_technicals.sql`:
  - **RSI 14**: Pure SQL calculation separating positive price changes (U) and negative price changes (D), computing smoothed averages via window functions, and calculating `RSI = 100 - (100 / (1 + RS))`.
  - **Bollinger Bands**: Calculates 20-day SMA and standard deviation; Upper = `SMA + 2*sigma`, Lower = `SMA - 2*sigma`.
  - **52-Week High / Low**: Windowed over 252 trading sessions: `MAX(high_price) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)`.

### Mart Models (`finance_dbt/models/marts/`)
- `dimensions/dim_date.sql`: Generates 1096-day calendar dimension (3 full years) with Indian Fiscal Year attributes:
  - `fiscal_year`: 'FY2025-26', 'FY2024-25' (April 1 to March 31).
  - `fiscal_quarter`: Q1 (Apr-Jun), Q2 (Jul-Sep), Q3 (Oct-Dec), Q4 (Jan-Mar).
  - `is_trading_day`: Boolean flag joining against `nse_trading_holidays`.
- `dimensions/dim_security.sql`: Dimension of 22 tracked NSE equities joined with sector classification.
- `dimensions/dim_sector.sql`: 13 Indian market sectors (IT, Banking, Energy, Automobile, FMCG, Pharma, etc.).
- `dimensions/dim_fund.sql`: Dimension of 5 top AMFI mutual fund schemes.
- `facts/fact_daily_prices.sql`: Primary equity fact table joining technicals, dimensions, and surrogate date keys. Grain: `(security_id, date_id)`.
- `facts/fact_macro_indicators.sql`: Macro fact table storing RBI Repo Rate, MOSPI CPI/WPI, and USD/INR rates.
- `facts/fact_mf_nav.sql`: Mutual fund daily NAV fact table with 52-week rolling NAV bounds.

### Macros & Singular Tests (`finance_dbt/macros/`, `finance_dbt/tests/`)
- `macros/test_price_positive.sql`: Generic test ensuring prices and NAVs are strictly `> 0`.
- `macros/test_rsi_bounds.sql`: Asserts `0 <= RSI_14 <= 100`.
- `macros/test_high_gte_low.sql`: Asserts `high_price >= low_price`.
- `tests/singular/test_calendar_no_unexplained_gaps.sql`: Asserts 0 unexplained missing dates on regular trading days.
- `tests/singular/test_reconcile_staging_fact_rows.sql`: Singular assertion verifying 100% row parity between Silver staging and Gold facts.

---

## 7. Central Data Access & Repositories (`data_access/`)

### `data_access/duckdb_client.py`
- **Purpose**: Manages DuckDB connection lifecycles with decoupled read-only and read-write safety.
- **Why It Exists**: DuckDB is an in-process columnar engine; concurrent write attempts from Streamlit and test runners result in database lock contention. This client strictly separates analytical reads (`read_only=True` on `curated.duckdb`) from operational state writes (`operational_metadata.duckdb`).
- **Imports**: `logging`, `pathlib`, `duckdb`, `pandas`.
- **Classes**:
  - `DuckDBClient`: Primary database interface.
- **Key Functionality**:
  - `get_read_only_connection()`: Connects to `curated.duckdb` in read-only mode for zero lock contention.
  - `get_read_write_connection()`: Connects to `operational_metadata.duckdb` for stateful updates.
  - `query(sql, params)`: Executes read queries and returns Pandas DataFrames.
  - `get_table_counts()`: Dynamically introspects row counts across all tables and views in `information_schema.tables`.
- **What Breaks If Removed**: Database locking errors crash the Streamlit terminal and tests.

### `data_access/repositories/incident_repository.py`
- **Purpose**: Persists and manages the lifecycle state machine of operational data incidents.
- **Why It Exists**: Enables production-grade incident management and tracking within the data platform.
- **Classes**:
  - `IncidentRepository`: CRUD operations for `data_incidents` in `operational_metadata.duckdb`.
- **Key Functionality**:
  - `init_table()`: Creates `data_incidents` table and seeds baseline operational incidents.
  - `get_all_incidents()`: Fetches all incident records sorted by detection timestamp.
  - `update_incident_status(incident_id, new_status, notes)`: Updates state machine: `DETECTED` ➔ `ACKNOWLEDGED` ➔ `INVESTIGATING` ➔ `RESOLVED`.
  - `create_incident(title, severity, source, table, ...)`: Generates auto-incrementing ID (`INC-2026-XXX`) and records new issue.
- **What Breaks If Removed**: Data Incident Center loses persistence.

---

## 8. Platform Service Layer (`services/`)

Decouples raw SQL queries and data transformations from Streamlit UI components:

| Service File | Purpose & Primary Methods | Data Sources Consulted |
| :--- | :--- | :--- |
| `services/market_service.py` | `get_market_snapshot()`, `get_top_movers()`, `get_sector_performance()`, `get_deterministic_insights()` | `fact_daily_prices`, `dim_security`, `dim_sector` |
| `services/equity_service.py` | `filter_equities(sector, min_price, max_price, min_rsi, ...)` | `fact_daily_prices`, `dim_security` |
| `services/stock_service.py` | `get_stock_history(symbol)`, `get_stock_profile(symbol)` | `fact_daily_prices`, `dim_date`, `dim_security` |
| `services/mutual_fund_service.py` | `get_all_funds()`, `get_fund_comparison_series()`, `get_fund_risk_scorecard()` | `fact_mf_nav`, `dim_fund`, `FinancialRiskEngine` |
| `services/macro_service.py` | `get_macro_snapshot()`, `get_indicator_series(code)` | `fact_macro_indicators`, `dim_date` |
| `services/risk_service.py` | `get_cross_asset_risk_frontier()`, `get_return_correlation_matrix()` | `fact_daily_prices`, `fact_mf_nav`, `fact_macro_indicators` |
| `services/pipeline_monitor_service.py` | `get_medallion_telemetry()`, `get_execution_runs()` | Disk partition scanner, `pipeline_execution_runs` |
| `services/lineage_service.py` | `get_lineage_graph()`, `get_node_metadata(node_id)` | dbt `manifest.json`, `catalog.json`, DuckDB schemas |
| `services/incident_service.py` | `get_incident_metrics()`, `trace_incident_impact(incident_id)` | `IncidentRepository`, `LineageService` |

---

## 9. AI Engine & Safe Text-to-SQL Assistant (`ai/`)

### `ai/sql_safety.py`
- **Purpose**: AST-based parser and regex validator enforcing strict SELECT-only safety rules.
- **Why It Exists**: Local AI text-to-SQL systems must never be able to execute mutating queries (`DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`) or multi-statement injection attacks.
- **Classes**:
  - `SQLSafetyValidator`: Guardrail engine.
- **Key Functionality**:
  - `validate_sql(sql)`: Validates that query starts strictly with `SELECT` or `WITH`, contains no forbidden tokens (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `EXEC`, `MERGE`), has no semicolon multi-statement delimiters, and targets only whitelisted tables (`fact_*`, `dim_*`, `stg_*`).
- **Tests**: Covered by `tests/ai/test_sql_safety.py` (100% pass).
- **What Breaks If Removed**: Database becomes vulnerable to malicious or erroneous query execution.

### `ai/sql_generator.py`
- **Purpose**: Deterministic query translator and schema-aware text-to-SQL generator.
- **Why It Exists**: Converts natural language questions into valid DuckDB SQL queries without relying on paid external cloud APIs.
- **Classes**:
  - `LocalSQLGenerator`: Query generator.
- **Key Functionality**: Maps intent patterns (Sharpe ratio queries, RSI oversold, moving average crosses, macro trends, pipeline failures) into syntactically valid DuckDB queries against curated marts.

### `ai/rag_assistant.py`
- **Purpose**: RAG orchestration engine combining schema metadata retrieval, query execution, and provenance citations.
- **Why It Exists**: Core driver for the `Ask Finance AI` terminal workspace.
- **Classes**:
  - `FinanceAIAssistant`: RAG assistant.
- **Key Functionality**:
  - `ask(question)`: Generates SQL, validates safety via `SQLSafetyValidator`, executes against DuckDB in read-only mode, and formats answer with SQL code, execution table, and data observation date citations.

---

## 10. Streamlit Terminal UI & Workspaces (`ui/`)

### `ui/terminal_app.py`
- **Purpose**: Main application controller and routing engine for the India Finance Intelligence Terminal.
- **Styling**: Injects institutional Bloomberg dark CSS tokens (`ui/components/theme.py`).
- **Layout**: Renders global topbar (`ui/components/topbar.py`), persistent navigation sidebar (`ui/components/sidebar.py`), and routes dynamically to the selected module.

### Modular Pages (`ui/pages/`)
1. `ui/pages/market_overview.py`: Benchmark snapshot, market breadth gauge, top gainers/losers, sector performance, and deterministic technical observations.
2. `ui/pages/equity_screener.py`: Multi-factor screener table with dynamic sliders and 1-click CSV export.
3. `ui/pages/stock_analytics.py`: 3-tier subplots (OHLCV, RSI, MACD, Bollinger Bands), return distribution histogram, and quantitative profiles.
4. `ui/pages/mutual_fund_intelligence.py`: AMFI NAV rebased performance comparison, drawdown curves, and institutional scorecard.
5. `ui/pages/macro_intelligence.py`: USD/INR exchange rate trends, RBI Repo Rate trajectory, and MOSPI inflation metrics.
6. `ui/pages/risk_analytics.py`: Cross-asset risk-return frontier bubble plot, Pearson correlation heatmap, and drawdown curves.
7. `ui/pages/data_operations.py`: Pipeline phase status (Bronze ➔ Silver ➔ Gold ➔ DQ), Medallion partition audit, and execution history.
8. `ui/pages/data_quality.py`: 100% Quality scorecard hero metrics, 17-rule assertions matrix, and cross-layer reconciliation waterfall.
9. `ui/pages/data_lineage.py`: Visual interactive Plotly DAG mapping node dependencies from Bronze raw to UI components with node metadata inspector.
10. `ui/pages/incident_center.py`: Incident KPIs, lifecycle state machine (`DETECTED` ➔ `ACKNOWLEDGED` ➔ `INVESTIGATING` ➔ `RESOLVED`), and lineage blast-radius impact analysis.
11. `ui/pages/ask_finance.py`: Chat interface with prompt chips, safe SQL execution panel, query results table, and provenance citations.

---

## 11. Pipeline Automation & Execution Entrypoints (`scripts/`)

- `scripts/run_phase1_ingestion.py`: Runs `NseStockClient`, `MacroClient`, and `AmfiMfClient`; writes partitioned Parquet files and SHA-256 batch manifests to `data/lakehouse/raw/`.
- `scripts/run_phase2_staging.py`: Runs `StagingManager`; deduplicates raw Parquet records on natural keys; executes `TradingCalendarValidator`; loads Silver tables into DuckDB.
- `scripts/run_phase2_qa_deep_audit.py`: Performs deep audit on Silver tables; checks boundary clamps, null values, and temporal continuity.
- `scripts/run_phase3_pipeline.py`: Compiles and executes dbt models (`dbt run`); executes 67 automated data tests (`dbt test`); stops pipeline if any test fails (circuit breaker).
- `scripts/run_phase4_dq_audit.py`: Executes Python Data Quality Suite (`DataQualitySuite`); performs cross-layer reconciliation (`LakehouseReconciliationAuditor`); writes `data/quality/dq_scorecard.md`.
- `scripts/verify_phase1_warehouse.py`: Quick verification script checking row counts and partition integrity.

---

## 12. Automated Verification & Test Suites (`tests/`)

Total of **45 Pytest tests** and **67 dbt data tests** (**112 total tests**, 100% pass rate):

| Test Module | Tests | Focus Area & Verified Behaviors |
| :--- | :---: | :--- |
| `tests/ai/test_sql_safety.py` | 3 | Validates SELECT enforcement, blocks DROP/DELETE/UPDATE mutations, blocks multi-statement delimiter attacks. |
| `tests/unit/test_phase1_ingestion.py` | 9 | Hive directory partitioning, SHA-256 fingerprint determinism, idempotent skip on duplicate payloads, model validations. |
| `tests/unit/test_phase2_staging.py` | 6 | Weekend detection, NSE holiday detection, regular trading day validation, data dropout detection, deduplication. |
| `tests/unit/test_phase2_additional_checks.py` | 3 | Cross-layer reconciliation exactness, negative price sanitization, holiday vs dropout discrimination. |
| `tests/unit/test_phase4_dq_and_alerts.py` | 8 | Gold fact baseline audit, Silver staging audit, defect detection, markdown scorecard generation, alert dispatching. |
| `tests/unit/test_phase5_mf_and_risk.py` | 7 | Mathematical precision of CAGR, volatility, Sharpe, Sortino, drawdown series, AMFI NAV parsing and fallbacks. |
| `tests/unit/test_dbt_pandas_indicator_parity.py` | 1 | Mathematical equivalence of dbt SQL indicators (RSI, SMA, Bollinger) vs Pandas calculation to 4 decimal places. |
| `tests/unit/test_services.py` | 8 | Validates all 8 core platform service modules against live DuckDB analytical marts. |

---

## 13. Configuration & Reference Dictionaries (`config/`)

- `config/symbols_nifty50.yaml`: Official NSE symbols, company names, and industry sector classifications for Nifty 50 constituents.
- `config/trading_holidays_nse.yaml`: Official National Stock Exchange of India (NSE) trading holidays (Republic Day, Mahashivratri, Holi, Id-Ul-Fitr, Ram Navami, Independence Day, Mahatma Gandhi Jayanti, Diwali Laxmi Pujan, Gurunanak Jayanti, Christmas).
- `config/macro_series.yaml`: Metadata for RBI and MOSPI indicators (series IDs, frequencies, units, description).
- `config/settings.py`: Centralized environment configurations, file paths, database URIs, and risk-free benchmark constants (R_f = 6.50%).

---

## 14. Orchestration DAGs (`dags/`, `docker/`, `ci/`)

- `dags/dag_daily_market_ingest.py`: Apache Airflow DAG scheduled at 16:30 IST (after NSE market close) to orchestrate Bronze Ingestion ➔ Staging ➔ dbt Run ➔ dbt Test ➔ DQ Audit.
- `dags/dag_macro_monthly.py`: Airflow DAG scheduled on the 12th of each month for MOSPI CPI/WPI data release.
- `docker/docker-compose.yml`: Container specification for local Airflow, PostgreSQL metadata DB, and DuckDB volumes.
- `ci/github-actions-ci.yml`: GitHub Actions continuous integration workflow running dbt tests and pytest suites on every push.

---

## 15. Technical Debt, Dead Code, and Forensic Findings

During forensic analysis, the following historical or non-critical items were cataloged:
1. **Legacy Prototype Directory (`src/finance_ai/`)**: Contains earlier prototype code (FastAPI endpoints, LangChain/Chroma wrappers) from prior exploratory versions before transitioning to the local DuckDB Medallion Lakehouse architecture.
   - *Status*: Retained for archival reference; completely decoupled from the production terminal (`ui/terminal_app.py` and `services/`).
2. **Archival Jupyter Notebooks (`notebooks/`)**: Exploratory notebooks (`01_model_baseline.ipynb`, `02_data_ingestion.ipynb`) used during early prototyping.
3. **Decoupled State Database**: Explicit architectural decision separating `curated.duckdb` (read-only analytical store) from `operational_metadata.duckdb` (read-write incident store), successfully resolving DuckDB concurrent lock contention.
