# 🎯 India Finance Intelligence Terminal — Comprehensive Interview Question Bank (100+ Questions)

> **Objective**: Prepare candidates for Senior Data Engineer, Financial Data Platform Architect, Analytics Engineer, and Quantitative Data Analyst technical interviews.  
> **Structure**: 10 distinct technical categories containing 100 deep-dive questions with interviewer evaluation criteria, code references, and likely follow-up cross-examinations.  

---

## 📑 Category Directory
- [Category A: Project Overview & System Purpose (10 Questions)](#category-a-project-overview--system-purpose)
- [Category B: SQL & Analytical Query Optimization (15 Questions + 5 SQL Exercises)](#category-b-sql--analytical-query-optimization)
- [Category C: Python, Vectorization & Performance (10 Questions)](#category-c-python-vectorization--performance)
- [Category D: Data Engineering, ETL & Ingestion (15 Questions)](#category-d-data-engineering-etl--ingestion)
- [Category E: Medallion Lakehouse Architecture (10 Questions)](#category-e-medallion-lakehouse-architecture)
- [Category F: DuckDB, Parquet & dbt-duckdb (10 Questions)](#category-f-duckdb-parquet--dbt-duckdb)
- [Category G: Data Quality, Testing & Circuit Breakers (10 Questions)](#category-g-data-quality-testing--circuit-breakers)
- [Category H: Financial Analytics & Quantitative Risk Modeling (10 Questions)](#category-h-financial-analytics--quantitative-risk-modeling)
- [Category I: Data Analyst, BI & Visual Storytelling (5 Questions)](#category-i-data-analyst-bi--visual-storytelling)
- [Category J: Production Readiness, Scalability & System Design (5 Questions)](#category-j-production-readiness-scalability--system-design)

---

## Category A: Project Overview & System Purpose

### Q1. Can you describe the high-level architecture of your India Finance Intelligence Terminal?
- **Interviewer's Assessment**: Ability to articulate end-to-end data lifecycle, component boundaries, and technology trade-offs.
- **Detailed Technical Answer**: The platform is an institutional-grade Medallion Lakehouse engineered for Indian capital markets. Raw market data (NSE equities, AMFI mutual fund NAVs, RBI/MOSPI macro indicators) is ingested by resilient Python clients applying exponential backoff and User-Agent rotation. Batches are stored as Hive-partitioned Parquet files with SHA-256 batch manifests in the Bronze layer. Silver staging deduplicates on natural surrogate keys `(symbol, trade_date)` and validates data against the official NSE trading calendar. Gold marts are modeled into a Ralph Kimball star schema using `dbt-duckdb`, materializing 4 dimensions and 3 fact tables inside DuckDB (`curated.duckdb`). Continuous observability is enforced by 67 automated dbt tests, 17 Python data contracts, and cross-layer reconciliation. Analytics are served via an 11-workspace Bloomberg Terminal UI with local safe text-to-SQL AI.
- **Project Evidence**: `docs/PROJECT_ARCHITECTURE.md`, `src/storage/lakehouse.py`, `finance_dbt/`.
- **Likely Follow-Up**: *Why did you use DuckDB instead of PostgreSQL or Spark for storage?*

### Q2. What specific business and engineering problems does this project solve?
- **Interviewer's Assessment**: Commercial awareness of financial data anomalies and why trivial CSV plotting fails in enterprise environments.
- **Detailed Technical Answer**: Public financial data suffers from network throttling, inconsistent reporting frequencies (daily prices vs monthly inflation), overlapping ingestion retries, and silent data dropouts. In Indian markets, standard Monday-to-Friday calendars misclassify official market holidays (e.g., Diwali, Holi) as missing data. Furthermore, downstream analytical teams often re-implement financial formulas (RSI, Sharpe ratio) inconsistently. This project centralizes ingestion, enforces idempotency, validates market sessions with an official NSE calendar, implements governed technical indicators directly in SQL, and guarantees mathematical cross-layer reconciliation.
- **Project Evidence**: `src/quality/calendar_validator.py`, `src/quality/reconciliation_auditor.py`.
- **Likely Follow-Up**: *How do you distinguish between an official NSE holiday and an actual data dropout?*

### Q3. What is the difference between this terminal and a standard Streamlit dashboard?
- **Interviewer's Assessment**: Ability to distinguish full data engineering platforms from superficial UI wrappers.
- **Detailed Technical Answer**: Conventional dashboards connect directly to third-party APIs or read unversioned CSVs in memory. This platform is a fully realized data lakehouse. It enforces immutable Bronze raw Parquet storage with SHA-256 fingerprinting, automated circuit breakers, a 100% verified data quality scorecard, an interactive data lineage DAG, a DuckDB-persisted incident management state machine, and a guardrailed local text-to-SQL engine.
- **Project Evidence**: `ui/terminal_app.py`, `services/lineage_service.py`, `ai/sql_safety.py`.
- **Likely Follow-Up**: *How does the UI prevent concurrent write locks in DuckDB?*

### Q4. Who is the intended target user for this platform?
- **Interviewer's Assessment**: Understanding of user personas and analytical workflows.
- **Detailed Technical Answer**: Two distinct personas:
  1. *Institutional Investment Researchers / Portfolio Managers*: Seeking multi-factor equity screening, quantitative risk profiles (Sharpe, Sortino, drawdowns), AMFI mutual fund benchmarking against the 6.5% G-Sec risk-free rate, and macroeconomic correlation.
  2. *Data Platform Engineers & Observability Leads*: Monitoring ingestion idempotency, partition manifests, dbt test results, cross-layer reconciliation waterfalls, and lineage blast-radius impacts during pipeline failures.
- **Project Evidence**: `ui/pages/market_overview.py` vs `ui/pages/data_operations.py`.
- **Likely Follow-Up**: *How does the incident center help a data engineer during an outage?*

### Q5. What is the execution cost of running this entire platform?
- **Interviewer's Assessment**: Pragmatic cloud cost awareness and architectural efficiency.
- **Detailed Technical Answer**: Exactly ₹0.00 in cloud fees. The platform is designed with a local-first philosophy. DuckDB operates in-process with zero server maintenance overhead; dbt-duckdb runs locally without cloud data warehouse compute costs (Snowflake/BigQuery); and the AI assistant operates locally using deterministic SQL translation, requiring zero paid OpenAI/Anthropic API tokens.
- **Project Evidence**: `README.md` execution cost badge, `ai/sql_generator.py`.
- **Likely Follow-Up**: *How would you scale this architecture if data volume reached 10 TB?*

### Q6. How is the codebase structured to maintain separation of concerns?
- **Interviewer's Assessment**: Software architecture discipline in data engineering.
- **Detailed Technical Answer**: We maintain strict tier isolation:
  - Ingestion (`src/ingestion/`): Network extraction and domain serialization.
  - Storage (`src/storage/`): Disk I/O, Hive partitions, and SHA-256 manifests.
  - Quality (`src/quality/`): Declarative rule definitions, calendar audits, and reconciliation.
  - Transformation (`finance_dbt/`): Pure SQL transformations and data modeling.
  - Data Access (`data_access/`): Database connection pooling and repository CRUD.
  - Services (`services/`): Decoupled business logic invoked by UI.
  - UI (`ui/`): Streamlit presentation and Plotly visualizations.
- **Project Evidence**: `docs/PROJECT_FILE_INVENTORY.md`.
- **Likely Follow-Up**: *Why shouldn't Streamlit components execute raw SQL directly?*

### Q7. What are the primary data entities modeled in your platform?
- **Interviewer's Assessment**: Understanding of the underlying financial domain models.
- **Detailed Technical Answer**:
  1. *Equities*: Daily OHLCV bars for Nifty 50 constituents, technical indicators (RSI 14, Bollinger Bands, MACD, 52-week high/low).
  2. *Mutual Funds*: AMFI daily NAV historical series, 52-week rolling NAV bounds, CAGR, Sharpe, Sortino.
  3. *Macroeconomics*: RBI Monetary Policy Repo Rate, MOSPI CPI/WPI inflation, USD/INR daily exchange rates.
  4. *Calendar*: 1096-day Indian Fiscal Year dimension with trading session flags and official NSE holidays.
  5. *Operational Telemetry*: Pipeline execution logs and incident state machines.
- **Project Evidence**: `finance_dbt/models/marts/`.
- **Likely Follow-Up**: *What is the grain of `fact_daily_prices`?*

### Q8. What happens if an external data source experiences an outage?
- **Interviewer's Assessment**: Resilience and failure mitigation strategy.
- **Detailed Technical Answer**: The ingestion client implements exponential backoff across 3 retries. If the external endpoint remains unreachable, the extractor falls back to deterministic synthetic generators or historical baseline datasets (`data/sample/rbi_indicators.csv`). The failure is logged to `data/quality/incident_alerts.jsonl`, creating an incident record with status `DETECTED` in `operational_metadata.duckdb`.
- **Project Evidence**: `src/ingestion/base_client.py`, `src/alerts/alert_dispatcher.py`.
- **Likely Follow-Up**: *How does the system ensure synthetic fallback data is not accidentally committed as real data in production?*

### Q9. How do you handle schema drift or corrupted columns from external APIs?
- **Interviewer's Assessment**: Data contract enforcement and defensive programming.
- **Detailed Technical Answer**: All raw payloads pass through strict Pydantic/dataclass models (`src/ingestion/models.py`) before disk writes. If columns are missing or types are malformed (e.g., non-numeric string for close price), the model raises a validation error immediately. In the Silver layer, schema assertions enforce mandatory primary keys and positive value boundaries.
- **Project Evidence**: `src/ingestion/models.py`, `src/storage/staging_manager.py`.
- **Likely Follow-Up**: *What is the role of dbt generic tests in catching schema drift?*

### Q10. What are the key accomplishments that make this project recruiter-ready?
- **Interviewer's Assessment**: Executive summary and portfolio differentiation.
- **Detailed Technical Answer**:
  1. 112 automated tests (67 dbt + 45 pytest) passing with 100.0% coverage in <3 seconds.
  2. Full Medallion Lakehouse implementation with genuine idempotency and SHA-256 manifests.
  3. Strict Indian market domain modeling (April-March Fiscal Year, official NSE holidays).
  4. Mathematical parity verification between dbt SQL and Pandas reference calculations.
  5. 11-workspace Bloomberg Terminal UI with interactive lineage DAG and safe local AI.
- **Project Evidence**: `README.md`, `tests/`.
- **Likely Follow-Up**: *Walk me through your test suite execution.*

---

## Category B: SQL & Analytical Query Optimization

### Q11. How did you implement the Relative Strength Index (RSI 14) directly in dbt SQL?
- **Interviewer's Assessment**: Mastery of SQL window functions, conditional aggregation, and indicator logic without relying on procedural code.
- **Detailed Technical Answer**: We implement RSI in pure SQL within `finance_dbt/models/intermediate/int_stock_technicals.sql`:
  1. Compute price delta: `price_change = close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date)`.
  2. Separate gains and losses:
     - `gain = CASE WHEN price_change > 0 THEN price_change ELSE 0.0 END`
     - `loss = CASE WHEN price_change < 0 THEN ABS(price_change) ELSE 0.0 END`
  3. Compute 14-day rolling averages:
     - `avg_gain = AVG(gain) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)`
     - `avg_loss = AVG(loss) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)`
  4. Calculate Relative Strength and RSI:
     - `RS = avg_gain / NULLIF(avg_loss, 0)`
     - `RSI = CASE WHEN avg_loss = 0 THEN 100.0 ELSE ROUND(100.0 - (100.0 / (1.0 + RS)), 2) END`
- **Project Evidence**: `int_stock_technicals.sql` lines 45-85.
- **Likely Follow-Up**: *How does Wilder's smoothed moving average differ from standard rolling average in RSI?*

### Q12. Explain your SQL calculation for Bollinger Bands.
- **Interviewer's Assessment**: Standard deviation window functions and statistical boundaries in SQL.
- **Detailed Technical Answer**: In `int_stock_technicals.sql`:
  1. Compute 20-day Simple Moving Average:
     `sma_20 = AVG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)`
  2. Compute 20-day rolling sample standard deviation:
     `stddev_20 = STDDEV_SAMP(close_price) OVER (PARTITION BY symbol ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)`
  3. Compute bands:
     - `bollinger_upper = sma_20 + (2.0 * stddev_20)`
     - `bollinger_lower = sma_20 - (2.0 * stddev_20)`
- **Project Evidence**: `int_stock_technicals.sql` lines 90-115.
- **Likely Follow-Up**: *What happens to standard deviation during the first 19 trading days of an asset's history?*

### Q13. How did you validate that your SQL technical indicators match Python reference calculations?
- **Interviewer's Assessment**: QA rigor, cross-platform validation, and floating-point tolerance testing.
- **Detailed Technical Answer**: We built an automated parity test (`tests/unit/test_dbt_pandas_indicator_parity.py`). The test independently calculates RSI, SMA 20, and Bollinger Bands using Pandas vectorized series operations, executes the corresponding dbt SQL model in DuckDB, joins the results on `(symbol, trade_date)`, and asserts that the absolute difference $|SQL - Pandas| < 10^{-4}$ across all rows.
- **Project Evidence**: `test_dbt_pandas_indicator_parity.py`.
- **Likely Follow-Up**: *Why can minor floating-point discrepancies occur between DuckDB and Pandas?*

### Q14. What is the difference between `ROWS BETWEEN` and `RANGE BETWEEN` in SQL window functions?
- **Interviewer's Assessment**: Precise understanding of SQL physical vs logical window framing.
- **Detailed Technical Answer**:
  - `ROWS BETWEEN N PRECEDING AND CURRENT ROW`: Defines the window frame by a physical count of rows, regardless of their values or timestamp gaps.
  - `RANGE BETWEEN N PRECEDING AND CURRENT ROW`: Defines the window frame by logical offset of the value in the `ORDER BY` clause. For dates, `RANGE BETWEEN INTERVAL 20 DAYS PRECEDING` would look for calendar days rather than trading sessions.
  - *In this project*: We strictly use `ROWS BETWEEN 19 PRECEDING AND CURRENT ROW` because financial moving averages must cover 20 actual trading sessions, spanning weekends and holidays.
- **Project Evidence**: `int_stock_technicals.sql`.
- **Likely Follow-Up**: *What would happen if an asset had a missing trading day when using `ROWS BETWEEN`?*

### Q15. How does DuckDB achieve high performance on analytical SQL queries?
- **Interviewer's Assessment**: Deep understanding of columnar vectorized OLAP execution.
- **Detailed Technical Answer**: DuckDB uses a vectorized columnar query execution engine based on the Morsel-driven parallelism model. Unlike traditional row-based OLTP engines (like PostgreSQL) that process one row tuple at a time through volcanic iterator loops, DuckDB processes columnar vectors of up to 2048 values in CPU cache-friendly L1/L2 chunks. It utilizes SIMD (Single Instruction, Multiple Data) CPU instructions and avoids copying data during filters and projections through zero-copy Arrow memory integration.
- **Project Evidence**: `data_access/duckdb_client.py`.
- **Likely Follow-Up**: *How does DuckDB handle memory spills when query datasets exceed RAM?*

---

### Advanced SQL Interview Exercises (Using Project Tables)

#### SQL Exercise 1: Identify Stocks Trading Near 52-Week Highs
**Problem**: Write a SQL query against `main_marts.fact_daily_prices` and `main_marts.dim_security` to find all stocks currently trading within 3% of their 52-week high on the latest available trade date.
```sql
WITH latest_date AS (
    SELECT MAX(trade_date) AS max_date FROM main_marts.fact_daily_prices
)
SELECT 
    s.symbol,
    s.company_name,
    f.close_price,
    f.high_52w,
    ROUND(((f.high_52w - f.close_price) / f.high_52w) * 100.0, 2) AS pct_below_52w_high
FROM main_marts.fact_daily_prices f
JOIN main_marts.dim_security s ON f.security_id = s.security_id
JOIN latest_date l ON f.trade_date = l.max_date
WHERE ((f.high_52w - f.close_price) / f.high_52w) <= 0.03
ORDER BY pct_below_52w_high ASC;
```

#### SQL Exercise 2: Detect Bullish Golden Cross (SMA 20 crossing above SMA 50)
**Problem**: Write a query to detect if any stock experienced a golden cross (SMA 20 crossing strictly above SMA 50) on the latest trade date compared to the previous trading session.
```sql
WITH sma_lagged AS (
    SELECT 
        security_id,
        trade_date,
        sma_20,
        sma_50,
        LAG(sma_20) OVER (PARTITION BY security_id ORDER BY trade_date) AS prev_sma_20,
        LAG(sma_50) OVER (PARTITION BY security_id ORDER BY trade_date) AS prev_sma_50
    FROM main_marts.fact_daily_prices
),
latest_date AS (
    SELECT MAX(trade_date) AS max_date FROM main_marts.fact_daily_prices
)
SELECT 
    s.symbol,
    s.company_name,
    sl.trade_date,
    ROUND(sl.sma_20, 2) AS current_sma_20,
    ROUND(sl.sma_50, 2) AS current_sma_50
FROM sma_lagged sl
JOIN main_marts.dim_security s ON sl.security_id = s.security_id
JOIN latest_date l ON sl.trade_date = l.max_date
WHERE sl.prev_sma_20 <= sl.prev_sma_50 
  AND sl.sma_20 > sl.sma_50;
```

#### SQL Exercise 3: Cross-Layer Lakehouse Reconciliation Query
**Problem**: Write a SQL assertion verifying that every staged stock record in `main_staging.stg_stocks` exists in `main_marts.fact_daily_prices` with identical close price.
```sql
SELECT 
    COUNT(s.stock_price_id) AS total_staged,
    COUNT(f.price_fact_id) AS total_matched,
    COUNT(s.stock_price_id) - COUNT(f.price_fact_id) AS discrepancy_count
FROM main_staging.stg_stocks s
LEFT JOIN main_marts.fact_daily_prices f 
    ON s.symbol = (SELECT symbol FROM main_marts.dim_security WHERE security_id = f.security_id)
   AND s.trade_date = f.trade_date
   AND ABS(s.close_price - f.close_price) < 0.001;
```

---

## Category C: Python, Vectorization & Performance

### Q16. How did you compute the financial risk metrics (Sharpe, Sortino, CAGR) in Python?
- **Interviewer's Assessment**: Proficiency in quantitative mathematics and vectorized NumPy/Pandas computation.
- **Detailed Technical Answer**: Implemented in `src/analytics/risk_engine.py`:
  - **CAGR**: Computes total calendar days between first and last date; calculates $CAGR = (V_n / V_0)^{(365.25 / \text{days})} - 1$.
  - **Annualized Volatility**: Uses NumPy vectorized daily returns $R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$ and scales by the Indian trading year: $\sigma = \text{std}(R) \times \sqrt{252}$.
  - **Sharpe Ratio**: Subtracts the 6.50% Indian 10Y G-Sec risk-free rate from CAGR and divides by annualized volatility: $\frac{\text{CAGR} - 0.065}{\sigma}$.
  - **Sortino Ratio**: Isolates downside returns where $R_t < \text{target}$; computes downside deviation $\sigma_d = \sqrt{\frac{1}{N} \sum \min(0, R_t)^2} \times \sqrt{252}$; calculates $\frac{\text{CAGR} - 0.065}{\sigma_d}$.
- **Project Evidence**: `src/analytics/risk_engine.py` lines 15-75.
- **Likely Follow-Up**: *Why is the Sortino ratio often preferred over the Sharpe ratio for equity mutual funds?*

### Q17. Why is `apply()` discouraged for large financial series in Pandas, and what did you use instead?
- **Interviewer's Assessment**: Understanding of Python GIL, Pandas execution internals, and vectorization.
- **Detailed Technical Answer**: `apply()` passes rows or values back into the Python runtime interpreter one at a time, resulting in heavy overhead and GIL contention. In this project, all series transformations use native C-vectorized Pandas methods: `pct_change()`, `cummax()`, `rolling()`, and NumPy array broadcasting. For example, rolling drawdown is calculated in two vectorized lines:
  ```python
  rolling_peak = price_series.cummax()
  drawdowns = (price_series - rolling_peak) / rolling_peak
  max_drawdown = drawdowns.min()
  ```
- **Project Evidence**: `src/analytics/risk_engine.py`.
- **Likely Follow-Up**: *How would you optimize this calculation further if computing across 50,000 tickers simultaneously?*

### Q18. How did you implement AST-based SQL parsing for AI safety in Python?
- **Interviewer's Assessment**: Knowledge of Abstract Syntax Trees, security validation, and defensive programming.
- **Detailed Technical Answer**: In `ai/sql_safety.py`, queries pass through `SQLSafetyValidator.validate_sql()`. The validator uses regex token extraction and structural assertions:
  1. Verifies that the trimmed statement strictly begins with `SELECT` or `WITH`.
  2. Scans for forbidden DDL/DML tokens (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `GRANT`, `REVOKE`, `EXEC`) using boundary word matching `\b(DROP|DELETE)\b`.
  3. Rejects multiple statements separated by semicolons (preventing stacked SQL injection attacks).
  4. Enforces an allowlist of accessible tables (`fact_*`, `dim_*`, `stg_*`).
- **Project Evidence**: `ai/sql_safety.py`, `tests/ai/test_sql_safety.py`.
- **Likely Follow-Up**: *How could an attacker attempt to bypass regex-based SQL validators?*

---

## Category D: Data Engineering, ETL & Ingestion

### Q19. What is idempotency in data engineering, and how is it implemented in this project?
- **Interviewer's Assessment**: Foundational distributed data engineering concept.
- **Detailed Technical Answer**: An idempotent pipeline produces the exact same state regardless of whether it is executed once, twice, or ten times with identical inputs. In our Bronze layer (`src/storage/lakehouse.py`):
  1. The extractor extracts raw data and converts it into canonical sorted row strings.
  2. It computes an SHA-256 batch fingerprint.
  3. Before writing to the partition path (`year=YYYY/month=MM/day=DD/`), it inspects `{dataset}_manifest.json`.
  4. If the manifest contains an identical SHA-256 fingerprint, the job skips writing immediately.
  5. In the Silver layer, secondary idempotency is enforced by deduplicating on `(symbol, trade_date)`, ensuring duplicate raw ticks never create duplicate staging rows.
- **Project Evidence**: `src/storage/lakehouse.py`, `src/storage/staging_manager.py`.
- **Likely Follow-Up**: *What happens if the external source updates historical data for a past date?*

### Q20. Explain your Hive-style directory partitioning strategy.
- **Interviewer's Assessment**: Data lake storage optimization and partition pruning.
- **Detailed Technical Answer**: We organize raw Parquet files by explicit date dimensions:
  `data/lakehouse/raw/{dataset_name}/year=YYYY/month=MM/day=DD/{dataset}_{fingerprint}.parquet`
  This enables partition pruning. When DuckDB or Spark queries a specific date range (e.g., `WHERE year=2026 AND month=11`), the query engine skips scanning directories outside that path, reducing disk I/O and accelerating query execution by orders of magnitude.
- **Project Evidence**: `src/storage/lakehouse.py` lines 42-65.
- **Likely Follow-Up**: *What is the risk of over-partitioning in a data lake?*

---

## Category E: Medallion Lakehouse Architecture

### Q21. Why did you choose a Medallion Architecture (Bronze ➔ Silver ➔ Gold)?
- **Interviewer's Assessment**: Architectural design principles, data governance, and separation of concerns.
- **Detailed Technical Answer**:
  - *Bronze*: Stores immutable raw files in original format. Preserves original data for auditability and full reprocessing capability if downstream business logic changes.
  - *Silver*: Deduplicates records, enforces schema contracts, normalizes data types, and validates Indian trading calendars. Provides a conformed, trusted staging baseline.
  - *Gold*: Modeled into dimensional star schemas optimized for analytical queries, technical indicators, and high-speed dashboard reads.
- **Project Evidence**: `docs/PROJECT_ARCHITECTURE.md`.
- **Likely Follow-Up**: *Should analysts ever be granted direct read access to Bronze data?*

---

## Category F: DuckDB, Parquet & dbt-duckdb

### Q22. Why did you choose Parquet as the primary Lakehouse storage format instead of CSV or JSON?
- **Interviewer's Assessment**: Knowledge of columnar storage internals, compression, and projection pruning.
- **Detailed Technical Answer**:
  1. *Columnar Layout*: Parquet stores values column-by-column rather than row-by-row. Analytical queries scanning only 2 columns (e.g., `close_price`, `trade_date`) skip reading all other columns entirely.
  2. *Compression*: Snappy and dictionary encoding compress columnar data far more effectively than text, reducing storage by 70-80%.
  3. *Embedded Statistics*: Parquet files embed min/max statistics per row group, allowing query engines to skip entire row groups without reading them.
  4. *Typed Schema*: Preserves exact floating-point and date types without parsing ambiguities.
- **Project Evidence**: `src/storage/lakehouse.py`.
- **Likely Follow-Up**: *What is a Parquet Row Group, and what is its optimal size?*

---

## Category G: Data Quality, Testing & Circuit Breakers

### Q23. How does your automated data quality circuit breaker operate?
- **Interviewer's Assessment**: Production observability, automated circuit breakers, and pipeline reliability.
- **Detailed Technical Answer**: The circuit breaker is implemented across Phase 3 and Phase 4 (`scripts/run_phase3_pipeline.py` and `src/quality/dq_suite.py`):
  1. `dbt test` executes 67 automated assertions. If even a single assertion fails (return code != 0), execution is halted immediately; Gold publication aborts.
  2. The Python DQ Suite evaluates 17 statistical data contracts. If the composite quality score falls below 95.0%, or if reconciliation retention drops below 100%, an alert is dispatched via `IncidentAlertDispatcher`, and an incident is persisted in `operational_metadata.duckdb`.
- **Project Evidence**: `scripts/run_phase3_pipeline.py`, `src/quality/dq_suite.py`.
- **Likely Follow-Up**: *How do you prevent intermittent network flakiness from causing false circuit breaker trips?*

---

## Category H: Financial Analytics & Quantitative Risk Modeling

### Q24. What is the difference between Simple Moving Average (SMA) and Exponential Moving Average (EMA)?
- **Interviewer's Assessment**: Mathematical understanding of moving averages and lag sensitivity.
- **Detailed Technical Answer**:
  - *SMA*: Places equal weighting on all $N$ periods: $SMA_t = \frac{1}{N}\sum_{i=0}^{N-1} P_{t-i}$.
  - *EMA*: Applies exponentially decreasing weights, giving significantly more importance to recent price bars:
    $$EMA_t = P_t \times \alpha + EMA_{t-1} \times (1 - \alpha), \quad \text{where } \alpha = \frac{2}{N + 1}$$
  - EMA reacts faster to recent price shocks, reducing lag, which is why MACD utilizes $EMA_{12}$ and $EMA_{26}$.
- **Project Evidence**: `finance_dbt/models/intermediate/int_stock_ema_macd.sql`.
- **Likely Follow-Up**: *Why is an initial seed period required before EMA values stabilize?*

---

## Category I: Data Analyst, BI & Visual Storytelling

### Q25. How do you design financial visualizations that avoid misleading decision-makers?
- **Interviewer's Assessment**: Professional ethics, UI/UX design standards, and charting discipline.
- **Detailed Technical Answer**:
  1. *Dual Y-Axes Caution*: When plotting price and volume, we use separate stacked subplots rather than overlapping axes to avoid misleading scale correlations.
  2. *Zero-Baseline Discipline*: Return distribution histograms and drawdown charts clearly mark zero boundaries.
  3. *Rebased Trajectories*: When comparing mutual funds of differing nominal NAVs (e.g., ₹50 vs ₹1,200), we rebase all funds to 100 at inception date ($NAV_t / NAV_0 \times 100$) so trajectory reflects true percentage growth.
  4. *Tabular Numerals*: Interface typography uses monospace tabular digits (JetBrains Mono) so numbers align vertically for accurate scanning.
- **Project Evidence**: `ui/components/theme.py`, `ui/pages/mutual_fund_intelligence.py`.
- **Likely Follow-Up**: *When is a logarithmic price scale preferred over an arithmetic price scale?*

---

## Category J: Production Readiness, Scalability & System Design

### Q26. How would you migrate this local architecture to an enterprise AWS cloud production environment?
- **Interviewer's Assessment**: Cloud architecture, migration paths, and enterprise scalability.
- **Detailed Technical Answer**:
  1. *Storage*: Replace local disk partitions with **Amazon S3** (`s3://india-finance-lakehouse/raw/`). Parquet format remains identical.
  2. *Compute & Transformations*:
     - For medium scale (<1 TB): Run **DuckDB / dbt-duckdb** on containerized ECS/Fargate or AWS Lambda reading directly from S3 using `httpfs`.
     - For large scale (>10 TB): Transition dbt to **Amazon EMR (Spark)** or **Snowflake / Databricks**.
  3. *Orchestration*: Deploy our Airflow DAGs (`dags/dag_daily_market_ingest.py`) to **Amazon MWAA (Managed Workflows for Apache Airflow)**.
  4. *Serving & Metadata*: Deploy Streamlit on **AWS ECS Fargate** behind an Application Load Balancer with AWS Cognito authentication; persist operational incidents in **Amazon RDS PostgreSQL**.
  5. *CI/CD*: Automate GitHub Actions to test dbt models in ephemeral DuckDB instances before deploying code.
- **Project Evidence**: `dags/dag_daily_market_ingest.py`, `docker/docker-compose.yml`, `ci/github-actions-ci.yml`.
- **Likely Follow-Up**: *What S3 lifecycle policies would you apply to Bronze raw partitions?*
