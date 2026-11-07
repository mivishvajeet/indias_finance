# ⚡ India Finance Intelligence Terminal — Interview Quick Revision Cheat Sheet

> **Purpose**: Rapid review cheat sheet designed to be read 30 minutes before a technical interview for Data Engineer, Analytics Engineer, or Financial Data Analyst roles.  

---

## 🏛️ 1. Architecture on One Page

```
Primary Sources (NSE Equities, AMFI Mutual Funds, RBI/MOSPI Macro)
      ↓ (Exponential Backoff + User-Agent Pool + Pydantic Contracts)
BRONZE LAKEHOUSE: Apache Parquet, Hive Partitioning (year/month/day), SHA-256 Batch Manifests (Idempotency)
      ↓ (Deduplication on (symbol, trade_date) + NSE Trading Calendar Validator)
SILVER STAGING: Cleaned DuckDB Views (stg_stocks, stg_macro, stg_mf_nav)
      ↓ (dbt-duckdb Transformations: Intermediate Technicals + Fiscal Year Dimensions)
GOLD MARTS: Ralph Kimball Star Schema (fact_daily_prices, fact_mf_nav, fact_macro, dim_date)
      ↓ (Automated Observability & Circuit Breakers)
QUALITY & INCIDENTS: 67 dbt tests + 17 Python DQ rules (100% Verified) + Incident State Machine
      ↓ (Decoupled Read-Only DuckDB Connection Pool)
SERVING & AI: 11 Bloomberg Terminal Workspaces (Streamlit 8502) + Safe Local Text-to-SQL Assistant
```

---

## 📊 2. Verified Physical Row Counts

| Layer | Dataset / Table Name | Physical Count | Engineering Rule / Notes |
| :--- | :--- | :---: | :--- |
| **Bronze** | Raw Ingested Stock Ticks | **163 records** | Contains 30 duplicate raw ticks produced during simulated retry ingestion. |
| **Silver** | `main_staging.stg_stocks` | **133 records** | Cleaned via natural surrogate key deduplication on `(symbol, trade_date)`. |
| **Gold** | `main_marts.fact_daily_prices` | **133 records** | **100.0% Retention Rate** from Silver; exactly 0 unexplained dropouts. |
| **Gold** | `main_marts.fact_macro_indicators` | **98 records** | RBI Repo Rate, MOSPI CPI/WPI, USD/INR time-series. |
| **Gold** | `main_marts.fact_mf_nav` | **500 records** | Top 5 AMFI mutual fund schemes historical NAV series. |
| **Gold** | `main_marts.dim_date` | **1096 records** | 3-year Indian Fiscal Year calendar (April 1 to March 31). |
| **Gold** | `main_marts.dim_security` | **22 records** | Tracked NSE equities joined with sector classification. |

---

## 📐 3. Core Financial Formulas Cheat Sheet

### 1. Compound Annual Growth Rate (CAGR)
$$\text{CAGR} = \left(\frac{V_{\text{final}}}{V_{\text{initial}}}\right)^{\frac{365.25}{\text{days}}} - 1$$

### 2. Annualized Volatility (Indian Trading Year)
$$\sigma_{\text{annual}} = \sigma_{\text{daily}} \times \sqrt{252}$$

### 3. Sharpe Ratio (Indian Benchmark)
$$\text{Sharpe} = \frac{\text{CAGR} - R_f}{\sigma_{\text{annual}}}, \quad \text{where } R_f = 6.50\% \text{ (Indian 10Y G-Sec Yield)}$$

### 4. Sortino Ratio (Downside Deviation)
$$\text{Sortino} = \frac{\text{CAGR} - R_f}{\sigma_{\text{downside}} \times \sqrt{252}}, \quad \text{where } \sigma_{\text{downside}} = \sqrt{\frac{1}{N}\sum \min(0, R_t)^2}$$

### 5. Maximum Drawdown (MDD)
$$\text{Drawdown}_t = \frac{P_t - \max_{i \le t}(P_i)}{\max_{i \le t}(P_i)}, \quad \text{MDD} = \min_t(\text{Drawdown}_t)$$

### 6. Relative Strength Index (RSI 14)
$$\text{RS} = \frac{\text{SMA}_{14}(\text{Gains})}{\text{SMA}_{14}(\text{Losses})}, \quad \text{RSI} = 100 - \left(\frac{100}{1 + \text{RS}}\right)$$

### 7. Bollinger Bands (20-day, 2σ)
$$\text{Upper} = \text{SMA}_{20} + 2\sigma_{20}, \quad \text{Middle} = \text{SMA}_{20}, \quad \text{Lower} = \text{SMA}_{20} - 2\sigma_{20}$$

---

## 🛠️ 4. Execution & Pipeline Commands

```bash
# 1. Ingest Raw Market Data into Bronze Parquet Lakehouse
python scripts/run_phase1_ingestion.py

# 2. Cleanse, Deduplicate & Validate into Silver Staging
python scripts/run_phase2_staging.py

# 3. Compile dbt Models & Run 67 Automated Tests (Circuit Breaker)
python scripts/run_phase3_pipeline.py

# 4. Execute 17-Rule Data Quality Suite & Reconciliation Waterfall
python scripts/run_phase4_dq_audit.py

# 5. Run Full 45-Test Automated Pytest Suite
pytest -v tests/

# 6. Launch 11-Workspace Financial Terminal UI
streamlit run ui/terminal_app.py --server.port 8502
```

---

## 🚀 5. Top 25 Rapid-Fire Interview Questions & Punchy Answers

1. **What is the project?** An institutional-grade Medallion Lakehouse and Financial Intelligence Terminal for Indian capital markets built on DuckDB, dbt, Parquet, and Streamlit.
2. **What problem does it solve?** Solves fragmented public market sources, ingestion duplicates, false holiday dropout alerts, unverified financial formulas, and concurrency lock contention.
3. **What is the Bronze layer?** Hive-partitioned Apache Parquet files storing immutable raw extracts accompanied by SHA-256 batch manifests.
4. **How is idempotency enforced?** By computing an SHA-256 fingerprint over sorted rows; if manifest matches on re-run, write is aborted with zero disk I/O.
5. **What happens in Silver?** Deduplication on `(symbol, trade_date)`, boundary assertions (`price > 0`), and trading calendar validation against official NSE holidays.
6. **Why a custom calendar validator?** Standard Monday-Friday calendars trigger false missing data alerts on Indian market holidays like Diwali and Holi.
7. **What is Gold?** A Ralph Kimball star schema with 4 dimensions and 3 fact tables modeled using dbt-duckdb.
8. **What is Indian FY?** April 1 to March 31, modeled directly in `dim_date` (`fiscal_year`, `fiscal_quarter`).
9. **Where are technical indicators computed?** In SQL inside dbt intermediate models (`int_stock_technicals.sql`) for columnar vectorized performance.
10. **How did you test indicator accuracy?** Parity test comparing dbt SQL output against Pandas calculation to 4 decimal places ($10^{-4}$).
11. **What is the risk-free rate used?** 6.50%, the official benchmark yield of the Indian 10-Year Government Bond (G-Sec).
12. **Why Sortino over Sharpe?** Sortino penalizes only downside volatility, ignoring upside volatility that benefits investors.
13. **How does the circuit breaker work?** Halts pipeline execution immediately if any dbt test fails or if Python DQ score falls below 95%.
14. **What is the reconciliation result?** Bronze 163 records ➔ Silver 133 records (-30 dups) ➔ Gold 133 records (100.0% retention).
15. **How many automated tests exist?** 112 total tests: 67 dbt data tests and 45 pytest tests (100% pass rate).
16. **Why DuckDB?** High-performance vectorized columnar OLAP engine that runs in-process with zero cloud infrastructure cost.
17. **How do you prevent DuckDB lock contention?** Decoupled architecture: analytical reads use `read_only=True` on `curated.duckdb`; incident writes go to `operational_metadata.duckdb`.
18. **Why Parquet over CSV?** Columnar compression, projection pruning, embedded statistics, and typed schemas.
19. **How does Ask Finance AI work?** AST-based SELECT-only validator ensures safe natural-language-to-SQL translation with zero paid cloud API dependencies.
20. **What is the grain of `fact_daily_prices`?** One record per security per trading date: `(security_id, date_id)`.
21. **What is the grain of `fact_mf_nav`?** One record per mutual fund scheme per NAV date: `(fund_id, date_id)`.
22. **What is the blast-radius impact analysis?** When a model or table fails, the Lineage Service traces all upstream sources and downstream dashboard dependencies.
23. **How is the terminal styled?** Institutional Bloomberg dark theme (`#080C12`, `#111A26`) with tabular monospace numerals (JetBrains Mono).
24. **How would you scale to 10 TB?** Migrate Bronze to Amazon S3, transition dbt to Amazon EMR / Spark, and orchestrate via AWS MWAA.
25. **What is the cloud cost?** ₹0.00. Entirely local, reproducible, and self-contained.

---

## ⚠️ 6. Ten Technical Interview Traps to Avoid

1. **Never claim official NSE API integration**: NSE has no free public REST API; be transparent that data is ingested via `yfinance` with fallback synthesis and AMFI portal parsing.
2. **Don't confuse `ROWS BETWEEN` with `RANGE BETWEEN`**: Always emphasize that 20-day moving averages require `ROWS BETWEEN 19 PRECEDING` to count actual trading sessions, not calendar days.
3. **Don't claim DuckDB is an OLTP database**: DuckDB is an in-process columnar OLAP engine designed for analytics, not high-concurrency transactional row inserts.
4. **Never say "100% quality means zero bugs"**: Data quality tests verify schema contracts and statistical thresholds; they do not guarantee that source numbers were not manipulated at the source.
5. **Don't forget the risk-free rate context**: If an interviewer asks for Sharpe ratio, never assume 2% or 0%; always state you used the Indian 10Y G-Sec rate of 6.50%.
6. **Don't confuse idempotency with caching**: Idempotency ensures identical state upon re-execution; caching avoids re-computation.
7. **Avoid vague explanations of reconciliation**: Cite exact verified numbers: 163 Bronze ➔ 133 Silver (-30 duplicate raw ticks) ➔ 133 Gold (100% retention).
8. **Don't claim AI runs in the cloud**: Highlight that Ask Finance AI is local, deterministic, and guardrailed with strict SELECT-only AST validation.
9. **Don't overlook DuckDB concurrency**: Be prepared to explain how `read_only=True` avoids database lock collisions with Streamlit.
10. **Never present planned features as implemented**: Distinguish clearly between what is active in the codebase and future roadmap items.
