# 🇮🇳 India Finance Intelligence Terminal

[![Python 3.12](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![dbt Tests: 67/67 PASS](https://img.shields.io/badge/dbt%20tests-67%2F67%20PASS-brightgreen.svg)](finance_dbt/)
[![Pytest: 27/27 PASS](https://img.shields.io/badge/pytest-27%2F27%20PASS-brightgreen.svg)](tests/)
[![Quality Score: 100%](https://img.shields.io/badge/Data%20Quality-100.0%25%20Verified-00FFA3.svg)](data/quality/dq_scorecard.md)
[![Execution Cost: ₹0](https://img.shields.io/badge/Cloud%20Cost-%E2%82%B90.00%20(Local%20DuckDB)-success.svg)](#architecture)

An enterprise-grade, local-first **Medallion Lakehouse** and **Financial Terminal** built for Indian capital markets (NSE equities, benchmark indices, mutual funds, and macroeconomic indicators). 

Engineered with a **QA-first paradigm**: automated circuit breakers, idempotency fingerprints, cross-layer reconciliation, and deterministic statistical anomaly checks.

---

## 🏛️ Medallion Lakehouse Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Resilient Ingestion Layer"]
        NSE[NSE Equities / yfinance] -->|Backoff & User-Agent Pool| BRONZE_STK[(Bronze Stocks Parquet)]
        MACRO[RBI & MOSPI Macro] -->|Deterministic Schema| BRONZE_MAC[(Bronze Macro Parquet)]
        AMFI[AMFI Mutual Fund NAVs] -->|SHA-256 Batch Fingerprint| BRONZE_MF[(Bronze MF Parquet)]
    end

    subgraph Silver ["2. Staging & Cleansing Layer (DuckDB)"]
        BRONZE_STK -->|Deduplication & Natural Keys| STG_STK[stg_stocks]
        BRONZE_MAC -->|Temporal Continuity Check| STG_MAC[stg_macro]
        BRONZE_MF -->|Price Boundary Clamp| STG_MF[stg_mf_nav]
        CAL[NSE Trading Calendar Validator] -.->|Audit Gaps| STG_STK
    end

    subgraph Gold ["3. Curated Star Schema Marts (dbt-duckdb)"]
        STG_STK --> INT_RET[int_stock_daily_returns]
        INT_RET --> INT_TECH[int_stock_technicals]
        INT_TECH --> FACT_PRICES[fact_daily_prices]
        
        STG_MAC --> FACT_MACRO[fact_macro_indicators]
        STG_MF --> FACT_MF[fact_mf_nav]
        
        DIM_DATE[dim_date - Indian FY] --> FACT_PRICES
        DIM_SEC[dim_security] --> FACT_PRICES
        DIM_SECT[dim_sector] --> DIM_SEC
        DIM_FUND[dim_fund] --> FACT_MF
    end

    subgraph Quality ["4. Quality Gates & Incident Alerts"]
        DBT_TEST{dbt 67 Data Tests} -->|Circuit Breaker| GATE[DQ Scorecard]
        PYTHON_DQ{17 Python DQ Rules} -->|Cross-Layer Reconciliation| GATE
        GATE -->|Failure Alert| ALERTS[Incident Alert Dispatcher]
    end

    subgraph Serving ["5. Analytics & Serving"]
        FACT_PRICES --> UI[Bloomberg-Style Terminal UI]
        FACT_MF --> RISK[Risk Analytics Engine - Sharpe/Sortino]
        RISK --> UI
        GATE --> UI
    end
```

---

## ⭐ Key Data Engineering Highlights

1. **Idempotent Partitioned Lakehouse (Bronze)**:
   - Hive-style directory partitioning (`year=YYYY/month=MM/day=DD/`).
   - Every batch writes a companion JSON manifest with an SHA-256 fingerprint. Re-ingesting identical data skips writes with zero I/O cost.

2. **Indian Market Calendar & Fiscal Year (April–March)**:
   - Built-in validator for NSE market holidays (Diwali, Holi, Republic Day) and trading sessions.
   - Accurately discriminates between legitimate market holidays and critical data dropouts.

3. **High-Precision SQL Financial Indicators (dbt)**:
   - **RSI 14**: Pure SQL calculation with zero-loss conditional handling.
   - **Bollinger Bands**: 20-day moving average $\pm 2\sigma$ standard deviations.
   - **EMA 12 / EMA 26 & MACD**: Recursive exponential smoothing approximations.
   - **52-Week High/Low**: Windowed across 252 Indian market trading sessions.
   - **Parity Tested**: Automated unit test verifies dbt SQL output against Pandas calculation to 4 decimal places.

4. **Institutional Mutual Fund Risk Engine**:
   - Calculates **Compound Annual Growth Rate (CAGR)**, **Annualized Volatility** ($\sigma \times \sqrt{252}$), **Sharpe Ratio** (vs 6.5% Indian 10Y benchmark), **Sortino Ratio** (downside deviation), and **Max Drawdown**.

5. **Cross-Layer Lakehouse Reconciliation Matrix (`🟢 VERIFIED`)**:
   - Reconciles record counts across Bronze, Silver, and Gold layers:
     - **Bronze Raw Lakehouse**: 163 records
     - **Silver Staging**: 133 records (*-30 duplicate raw bars eliminated by idempotency deduplication*)
     - **Gold Marts**: 133 records (*100.0% retention into star schema facts; 0 unexplained dropouts*)

---

## 📐 Star Schema Dimensional Model

```mermaid
erDiagram
    dim_date ||--o{ fact_daily_prices : "has date"
    dim_date ||--o{ fact_macro_indicators : "has date"
    dim_date ||--o{ fact_mf_nav : "has date"
    dim_security ||--o{ fact_daily_prices : "trades"
    dim_sector ||--o{ dim_security : "categorizes"
    dim_fund ||--o{ fact_mf_nav : "declares"

    fact_daily_prices {
        varchar price_fact_id PK
        varchar security_id FK
        integer date_id FK
        date trade_date
        double close_price
        double daily_return_pct
        double sma_20
        double bollinger_upper
        double bollinger_lower
        double rsi_14
        double macd_line
    }

    fact_mf_nav {
        varchar nav_fact_id PK
        varchar fund_id FK
        integer date_id FK
        varchar scheme_code
        double nav
        double daily_return_pct
        double nav_high_52w
        double nav_low_52w
    }

    dim_date {
        integer date_id PK
        date calendar_date
        varchar indian_fiscal_year
        integer fiscal_quarter
        boolean is_trading_day
    }
```

---

## 🚀 Quickstart & Pipeline Execution

### 1. Prerequisites & Installation
```bash
git clone https://github.com/mivishvajeet/indias_finance.git
cd indias_finance
pip install -r requirements.txt dbt-duckdb
```

### 2. Run the Full End-to-End Pipeline
```bash
# Ingest raw market data into Bronze Lakehouse
python scripts/run_phase1_ingestion.py

# Cleanse & deduplicate into Silver Staging
python scripts/run_phase2_staging.py

# Compile & run dbt star schema models + 67 automated tests
python scripts/run_phase3_pipeline.py

# Run Cross-Layer Lakehouse Reconciliation & Data Quality Suite
python scripts/run_phase4_dq_audit.py

# Execute full pytest suite (27 unit & integration tests)
pytest -v tests/
```

### 3. Launch the Bloomberg-Style Terminal UI
```bash
streamlit run ui/terminal_app.py
```

---

## 🧪 Testing & Verification Summary

| Test Category | Suite | Test Count | Pass Rate | Execution Time |
| :--- | :--- | :---: | :---: | :---: |
| **dbt Schema & Generic Tests** | `dbt test` | **67** | **100.0%** | **0.73s** |
| **Lakehouse & Partitioning** | `pytest` | 8 | 100.0% | 0.40s |
| **Trading Calendar & Staging** | `pytest` | 11 | 100.0% | 0.35s |
| **Pandas vs dbt Parity** | `pytest` | 1 | 100.0% | 0.05s |
| **Data Quality Suite & Alerts** | `pytest` | 7 | 100.0% | 0.30s |
| **Total Automated Tests** | **All Layers** | **94** | **100.0%** | **< 2s** |

---

## 💼 Recruiter & Tech-Lead Interview Cheat Sheet

### 1. "How do you ensure idempotency in the lakehouse ingestion layer?"
> *"Every ingestion batch writes partitioned Parquet files accompanied by a metadata manifest containing the SHA-256 hash of all records in the batch. If the extractor re-runs on the same date window with unchanged data, the system detects a fingerprint match and terminates early with zero disk I/O, preventing duplicate partitions."*

### 2. "Why calculate technical indicators directly in dbt rather than Python/Pandas?"
> *"Pushing indicators like RSI and Bollinger Bands into DuckDB SQL allows us to leverage columnar vectorized execution on the warehouse engine. It guarantees that any downstream consumer—whether an analyst running ad-hoc SQL, a BI dashboard, or an ML model—sees identical, governed metrics rather than recalculating them in client code."*

### 3. "How did you validate your custom dbt SQL against reference implementations?"
> *"We built an automated parity unit test (`test_dbt_pandas_indicator_parity.py`) that independently calculates RSI, SMA, and Bollinger Bands using Pandas and compares the values row-by-row with DuckDB's dbt mart output. Both match within 4 decimal places ($10^{-4}$ tolerance)."*

### 4. "How do you handle Indian market nuances like holidays and fiscal years?"
> *"Standard calendar tools assume standard Monday–Friday operations. We implemented an official NSE calendar validator loaded with Indian exchange holidays (Diwali, Holi, Republic Day) and modeled `dim_date` around the Indian Fiscal Year (April 1 to March 31). This prevents false data dropout alerts when the market is legitimately closed."*

---

## ⚖️ Disclaimer

*This terminal is strictly built for educational, data engineering, and portfolio demonstration purposes. It does not constitute financial, investment, or trading advice.*
