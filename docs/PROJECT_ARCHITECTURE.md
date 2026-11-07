# 🏛️ India Finance Intelligence Terminal — Complete System Architecture & Engineering Blueprints

> **System**: India Finance Intelligence Terminal  
> **Document Purpose**: Authoritative system architecture, data flow diagrams, dimensional data models, and component dependency graphs.  
> **Audience**: Data Architects, Principal Data Engineers, Technical Interviewers, and Analytics Leaders.  

---

## 📑 Table of Architectural Blueprints

1. [Blueprint A: End-to-End System Architecture](#1-blueprint-a-end-to-end-system-architecture)
2. [Blueprint B: Medallion Lakehouse Architecture](#2-blueprint-b-medallion-lakehouse-architecture)
3. [Blueprint C: Resilient Ingestion & Idempotency Architecture](#3-blueprint-c-resilient-ingestion--idempotency-architecture)
4. [Blueprint D: dbt Transformation Directed Acyclic Graph (DAG)](#4-blueprint-d-dbt-transformation-directed-acyclic-graph-dag)
5. [Blueprint E: Data Quality Gates & Circuit Breaker Architecture](#5-blueprint-e-data-quality-gates--circuit-breaker-architecture)
6. [Blueprint F: Financial Terminal Serving & Analytical Architecture](#6-blueprint-f-financial-terminal-serving--analytical-architecture)
7. [Blueprint G: Repository Code & Module Dependency Graph](#7-blueprint-g-repository-code--module-dependency-graph)
8. [Blueprint H: Chronological Pipeline Execution Sequence](#8-blueprint-h-chronological-pipeline-execution-sequence)
9. [Blueprint I: Star Schema Dimensional Entity-Relationship Model (ERD)](#9-blueprint-i-star-schema-dimensional-entity-relationship-model-erd)

---

## 1. Blueprint A: End-to-End System Architecture

This blueprint illustrates the entire journey of financial data from primary Indian market sources to institutional research dashboards and local AI:

```mermaid
flowchart TB
    subgraph SOURCES ["1. Primary External Sources"]
        NSE["National Stock Exchange (NSE) / yfinance<br/>• Daily OHLCV Price Bars<br/>• Nifty 50 Constituents & Indices"]
        AMFI["AMFI India Mutual Fund Portal<br/>• Daily Scheme NAV Series<br/>• Equity & Large-Cap Funds"]
        RBI["Reserve Bank of India (RBI)<br/>• Monetary Policy Repo Rate<br/>• Banking System Liquidity"]
        MOSPI["MOSPI India Economic Database<br/>• Consumer Price Index (CPI)<br/>• Wholesale Price Index (WPI)"]
    end

    subgraph INGESTION ["2. Resilient Ingestion & Storage"]
        CLIENTS["Ingestion Connectors (src/ingestion/)<br/>• Exponential Backoff & Retry<br/>• Random User-Agent Pool<br/>• Pydantic/DataClass Contracts"]
        BRONZE[("Bronze Raw Lakehouse<br/>data/lakehouse/raw/<br/>• Hive Partitioning: year/month/day<br/>• Apache Parquet (Snappy)<br/>• SHA-256 Batch Manifests<br/>• Idempotent Write Skipping")]
    end

    subgraph STAGING ["3. Silver Staging & Cleansing"]
        STG_MGR["Staging Manager (src/storage/staging_manager.py)<br/>• Natural Key Deduplication: (symbol, date)<br/>• Price Boundary Clamping: close > 0<br/>• Type Casting & Timestamp Normalization"]
        CAL_VAL["Trading Calendar Validator (src/quality/calendar_validator.py)<br/>• NSE Trading Holidays Alignment<br/>• Market Holiday vs Dropout Discrimination"]
        SILVER[("Silver Cleaned DuckDB Staging<br/>main_staging views<br/>• stg_stocks (133 rows)<br/>• stg_macro (98 rows)<br/>• stg_mf_nav (500 rows)")]
    end

    subgraph TRANSFORMATION ["4. Gold Marts & dbt Transformations"]
        DBT["dbt-duckdb Transformation Engine (finance_dbt/)<br/>• 3 Intermediate Views: SQL Technicals, RSI, MACD<br/>• 4 Dimension Tables: dim_date (Indian FY), dim_sec, dim_sector, dim_fund<br/>• 3 Fact Tables: fact_daily_prices, fact_mf_nav, fact_macro"]
        GOLD[("Gold Analytical Lakehouse<br/>data/warehouse/curated.duckdb<br/>• Columnar Vectorized Execution<br/>• Star Schema Dimensional Marts<br/>• Read-Only Connection Pool")]
    end

    subgraph QUALITY ["5. Observability & Circuit Breakers"]
        DBT_TEST["dbt Test Engine<br/>• 67 Automated Assertions<br/>• Unique, Not Null, Price > 0, RSI Clamps"]
        PY_DQ["Python DQ Suite (src/quality/dq_suite.py)<br/>• 17 Statistical Assertions<br/>• Cross-Layer Reconciliation Waterfall<br/>• Automated Circuit Breaker"]
        INCIDENTS["Data Incident Store<br/>data/warehouse/operational_metadata.duckdb<br/>• Lifecycle: DETECTED ➔ RESOLVED<br/>• Blast-Radius Impact Analysis"]
    end

    subgraph SERVING ["6. Serving & Terminal Workspaces"]
        SERVICES["Platform Service Layer (services/)<br/>• Market, Equity, Stock, Fund, Macro, Risk Services"]
        UI["Bloomberg Terminal UI (ui/terminal_app.py)<br/>• 11 Dedicated Financial Workspaces<br/>• JetBrains Mono & Dark Financial Tokens<br/>• Interactive Plotly Technical Subplots"]
        AI["Ask Finance AI (ai/)<br/>• Guardrailed Text-to-SQL<br/>• AST SELECT-Only Enforcement<br/>• SQL & Data Provenance Citations"]
    end

    SOURCES --> CLIENTS --> BRONZE
    BRONZE --> STG_MGR
    CAL_VAL -.-> STG_MGR
    STG_MGR --> SILVER
    SILVER --> DBT --> GOLD
    GOLD --> DBT_TEST & PY_DQ
    PY_DQ --> INCIDENTS
    GOLD --> SERVICES --> UI
    GOLD --> AI --> UI
    INCIDENTS --> UI
```

---

## 2. Blueprint B: Medallion Lakehouse Architecture

The platform strictly adheres to the Medallion Lakehouse pattern (Databricks standard adapted for local-first DuckDB columnar execution):

```mermaid
flowchart LR
    subgraph Bronze ["BRONZE (Raw Immutability)"]
        direction TB
        B1["Format: Apache Parquet (Snappy)"]
        B2["Structure: Hive Partitioning<br/>year=YYYY/month=MM/day=DD/"]
        B3["Audit: SHA-256 Batch Manifests"]
        B4["State: Raw external extracts<br/>including duplicates and retries"]
    end

    subgraph Silver ["SILVER (Cleaned & Conformed)"]
        direction TB
        S1["Engine: DuckDB In-Process Engine"]
        S2["Deduplication: Natural Key Hash<br/>(symbol, trade_date)"]
        S3["Calendar: NSE Official Holiday Validation"]
        S4["Sanitization: Positive Bounds<br/>close > 0, nav > 0, high >= low"]
    end

    subgraph Gold ["GOLD (Curated Star Schema Marts)"]
        direction TB
        G1["Modeling: Kimball Star Schema"]
        G2["Calendar: Indian Fiscal Year (April-March)"]
        G3["Technicals: RSI 14, Bollinger, MACD in SQL"]
        G4["Risk Engine: CAGR, Sharpe, Sortino, Drawdown"]
    end

    Bronze -->|"Incremental Deduplication & Cleanse"| Silver
    Silver -->|"dbt-duckdb SQL Transformations"| Gold
```

---

## 3. Blueprint C: Resilient Ingestion & Idempotency Architecture

This diagram details the SHA-256 fingerprinting and idempotency mechanism guaranteeing that re-ingestion never creates duplicate files or duplicate rows:

```mermaid
sequenceDiagram
    autonumber
    participant Source as External Market Source (NSE / AMFI / RBI)
    participant Client as Ingestion Connector (src/ingestion/)
    participant Storage as Lakehouse Storage (src/storage/lakehouse.py)
    participant Manifest as Partition Manifest JSON
    participant Disk as Bronze Lakehouse Disk

    Client->>Source: HTTP GET with Exponential Backoff & User-Agent Pool
    Source-->>Client: Raw Financial Payload (JSON / CSV / Parquet)
    Client->>Client: Validate Schema (Pydantic / Dataclass Models)
    Client->>Storage: Submit Batch DataFrame & Target Partition Date
    Storage->>Storage: Compute Canonical SHA-256 Hash of Sorted Row Tuples
    Storage->>Manifest: Check If {dataset}_manifest.json Exists in Partition Directory
    alt Manifest Exists AND Manifest SHA-256 Matches Current Hash
        Manifest-->>Storage: Fingerprint Match Confirmed
        Storage-->>Client: Skip Write (Idempotent Hit: 0 Disk I/O, Return Early)
    else No Manifest OR Fingerprint Differs
        Storage->>Disk: Write Partition: {dataset}_{fingerprint}.parquet
        Storage->>Manifest: Write Manifest JSON (Hash, Batch ID, Timestamp, Record Count)
        Storage-->>Client: Partition Committed Successfully
    end
```

---

## 4. Blueprint D: dbt Transformation Directed Acyclic Graph (DAG)

The dbt project (`finance_dbt/`) orchestrates 13 modular SQL transformations with explicit lineage:

```mermaid
flowchart TD
    subgraph Staging_Layer ["1. Staging Views (schema: main_staging)"]
        STG_S["stg_stocks<br/>• Selects from main.stg_stocks_daily<br/>• Type casts: trade_date to DATE, prices to DOUBLE"]
        STG_M["stg_macro<br/>• Selects from main.stg_macro_indicators<br/>• Casts observation_date, indicator_value"]
        STG_F["stg_mf_nav<br/>• Selects from main.stg_mf_nav<br/>• Normalizes scheme codes, casts nav"]
    end

    subgraph Seeds ["Seeds (schema: main)"]
        SEED_SEC["nse_securities.csv<br/>• 22 Tracked Symbols & Company Names"]
        SEED_HOL["nse_trading_holidays.csv<br/>• Official 2024-2026 NSE Holidays"]
    end

    subgraph Intermediate_Layer ["2. Intermediate Business Logic (schema: main_intermediate)"]
        INT_RET["int_stock_daily_returns<br/>• LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date)<br/>• Computes daily_return_pct"]
        INT_EMA["int_stock_ema_macd<br/>• Computes EMA 12 and EMA 26<br/>• MACD Line = EMA_12 - EMA_26<br/>• Signal Line = 9-Day EMA of MACD"]
        INT_TECH["int_stock_technicals<br/>• RSI 14 (Smoothed U/D price deltas)<br/>• Bollinger Bands (20-day SMA +/- 2*sigma)<br/>• 52-Week High & Low (Windowed 252 sessions)"]
    end

    subgraph Dimensions ["3. Dimension Tables (schema: main_marts)"]
        DIM_DATE["dim_date<br/>• 1096 Days (Indian FY Calendar)<br/>• fiscal_year (Apr-Mar), fiscal_quarter<br/>• is_trading_day (joined with holidays)"]
        DIM_SEC["dim_security<br/>• 22 Tracked NSE Equities<br/>• Natural key: symbol, Surrogate: security_id"]
        DIM_SECT["dim_sector<br/>• 13 Indian Market Sectors"]
        DIM_FUND["dim_fund<br/>• 5 AMFI Equity Schemes"]
    end

    subgraph Facts ["4. Fact Tables (schema: main_marts)"]
        FACT_STK["fact_daily_prices<br/>• Grain: (security_id, date_id)<br/>• Prices, Technical Indicators, Moving Averages"]
        FACT_MAC["fact_macro_indicators<br/>• Grain: (indicator_code, date_id)<br/>• Repo Rate, CPI, WPI, USD/INR"]
        FACT_NAV["fact_mf_nav<br/>• Grain: (fund_id, date_id)<br/>• Daily NAV, Daily Return, 52W Bounds"]
    end

    STG_S --> INT_RET --> INT_EMA --> INT_TECH
    INT_TECH --> FACT_STK
    DIM_DATE --> FACT_STK
    DIM_SEC --> FACT_STK
    DIM_SECT --> DIM_SEC
    SEED_SEC --> DIM_SEC
    SEED_HOL --> DIM_DATE

    STG_M --> FACT_MAC
    DIM_DATE --> FACT_MAC

    STG_F --> FACT_NAV
    DIM_DATE --> FACT_NAV
    DIM_FUND --> FACT_NAV
```

---

## 5. Blueprint E: Data Quality Gates & Circuit Breaker Architecture

This diagram illustrates how data quality is verified across multiple validation lines before analytics certification:

```mermaid
flowchart TD
    subgraph DataArrival ["Data Processing Pipeline"]
        SILVER_READY["Silver Staging Populated"]
        DBT_BUILD["dbt Models Compiled & Run"]
    end

    subgraph Gate1 ["Gate 1: dbt Automated Tests (67 Assertions)"]
        T_UNIQUE["Unique Primary Keys<br/>(price_fact_id, nav_fact_id, macro_fact_id)"]
        T_NOTNULL["Not Null Columns<br/>(trade_date, close_price, nav, indicator_value)"]
        T_BOUNDS["Custom Macros<br/>• price_positive (price > 0)<br/>• rsi_bounds (0 <= rsi <= 100)<br/>• high_gte_low (high >= low)"]
        T_SINGULAR["Singular Tests<br/>• test_calendar_no_unexplained_gaps<br/>• test_reconcile_staging_fact_rows"]
    end

    subgraph Gate2 ["Gate 2: Python Data Quality Suite (17 Rules)"]
        RULE_EVAL["DataQualitySuite (src/quality/dq_suite.py)<br/>• Evaluates Completeness, Validity, Anomaly Thresholds<br/>• Calculates Composite Quality Score"]
        RECON_EVAL["LakehouseReconciliationAuditor<br/>• Verifies Bronze (163) ➔ Silver (133) ➔ Gold (133)<br/>• Asserts 100.0% Fact Retention Rate"]
    end

    subgraph CircuitBreakerDecision ["Circuit Breaker Evaluation"]
        TEST_PASS{"Did ALL Tests Pass<br/>AND Quality Score >= 95%?"}
    end

    subgraph PassOutcome ["Certified Production State"]
        PROD_SUCCESS["✅ Certify Gold Marts for Analytics<br/>Update Quality Scorecard to 100.0%<br/>Log Successful Pipeline Run"]
    end

    subgraph FailOutcome ["Incident Dispatch & Circuit Trip"]
        TRIP_BREAKER["🛑 TRIP CIRCUIT BREAKER<br/>Halt Downstream Serving Sync"]
        DISPATCH_ALERT["IncidentAlertDispatcher<br/>• Write incident_alerts.jsonl<br/>• Insert into operational_metadata.duckdb<br/>• State: DETECTED"]
    end

    SILVER_READY --> DBT_BUILD
    DBT_BUILD --> Gate1
    Gate1 --> Gate2
    Gate2 --> TEST_PASS
    TEST_PASS -->|YES| PROD_SUCCESS
    TEST_PASS -->|NO| TRIP_BREAKER --> DISPATCH_ALERT
```

---

## 6. Blueprint F: Financial Terminal Serving & Analytical Architecture

This blueprint shows how the presentation layer decouples UI rendering from database execution:

```mermaid
flowchart TB
    subgraph Presentation ["Presentation Layer (Streamlit 8502)"]
        UI_MAIN["ui/terminal_app.py (Controller)"]
        UI_TOP["ui/components/topbar.py (Live Indices Ticker & Calendar Status)"]
        UI_SIDE["ui/components/sidebar.py (11 Module Navigation & Telemetry)"]
        UI_THEME["ui/components/theme.py (Bloomberg Dark CSS Tokens)"]
        
        subgraph Workspaces ["11 Terminal Workspaces"]
            W1["1. Market Overview"]
            W2["2. Equity Screener"]
            W3["3. Stock Analytics"]
            W4["4. Mutual Fund Intel"]
            W5["5. Macro Intelligence"]
            W6["6. Risk Analytics"]
            W7["7. Data Operations"]
            W8["8. Data Quality Center"]
            W9["9. Data Lineage Explorer"]
            W10["10. Data Incident Center"]
            W11["11. Ask Finance AI"]
        end
    end

    subgraph Services ["Service Layer (services/)"]
        S_MKT["MarketService"]
        S_EQ["EquityService"]
        S_STK["StockService"]
        S_MF["MutualFundService"]
        S_MAC["MacroService"]
        S_RSK["RiskService"]
        S_OPS["PipelineMonitorService"]
        S_LIN["LineageService"]
        S_INC["IncidentService"]
    end

    subgraph Quantitative ["Financial Analytics (src/analytics/)"]
        RISK_ENG["FinancialRiskEngine<br/>• Vectorized CAGR, Volatility, Sharpe, Sortino, Drawdowns"]
    end

    subgraph SafeAI ["AI Engine (ai/)"]
        AI_SAFE["SQLSafetyValidator (AST SELECT-Only Parser)"]
        AI_GEN["LocalSQLGenerator (Schema Translation)"]
        AI_RAG["FinanceAIAssistant (Orchestrator)"]
    end

    subgraph DataAccess ["Data Access Layer (data_access/)"]
        DB_CLIENT["DuckDBClient (Singleton Pool)"]
        INC_REPO["IncidentRepository"]
    end

    subgraph StorageEngine ["DuckDB Storage Engines"]
        CURATED[("curated.duckdb<br/>(read_only=True)<br/>Gold Dimensional Marts")]
        OPS_DB[("operational_metadata.duckdb<br/>(read_only=False)<br/>Incidents & Pipeline Logs")]
    end

    UI_MAIN --> UI_TOP & UI_SIDE & UI_THEME
    UI_SIDE --> Workspaces
    W1 --> S_MKT
    W2 --> S_EQ
    W3 --> S_STK
    W4 --> S_MF
    W5 --> S_MAC
    W6 --> S_RSK
    W7 --> S_OPS
    W8 --> S_OPS
    W9 --> S_LIN
    W10 --> S_INC
    W11 --> AI_RAG

    S_MF & S_RSK --> RISK_ENG
    AI_RAG --> AI_SAFE --> AI_GEN --> DB_CLIENT

    S_MKT & S_EQ & S_STK & S_MF & S_MAC & S_RSK & S_OPS & S_LIN --> DB_CLIENT
    S_INC --> INC_REPO --> DB_CLIENT

    DB_CLIENT -->|Analytical Reads| CURATED
    DB_CLIENT -->|Operational Writes| OPS_DB
```

---

## 7. Blueprint G: Repository Code & Module Dependency Graph

```mermaid
graph TD
    subgraph Core_Storage ["Storage & Quality Base"]
        models_py["src/ingestion/models.py"]
        lakehouse_py["src/storage/lakehouse.py"]
        calendar_py["src/quality/calendar_validator.py"]
        staging_mgr["src/storage/staging_manager.py"]
        dq_rules["src/quality/dq_rules.py"]
        dq_suite["src/quality/dq_suite.py"]
        recon["src/quality/reconciliation_auditor.py"]
        alerts["src/alerts/alert_dispatcher.py"]
        risk_eng["src/analytics/risk_engine.py"]
    end

    subgraph Data_Access ["Data Access Layer"]
        duckdb_client["data_access/duckdb_client.py"]
        incident_repo["data_access/repositories/incident_repository.py"]
    end

    subgraph Service_Tier ["Service Tier"]
        mkt_svc["services/market_service.py"]
        eq_svc["services/equity_service.py"]
        stk_svc["services/stock_service.py"]
        mf_svc["services/mutual_fund_service.py"]
        mac_svc["services/macro_service.py"]
        rsk_svc["services/risk_service.py"]
        ops_svc["services/pipeline_monitor_service.py"]
        lin_svc["services/lineage_service.py"]
        inc_svc["services/incident_service.py"]
    end

    subgraph AI_Tier ["AI Assistant Tier"]
        ai_safe["ai/sql_safety.py"]
        ai_gen["ai/sql_generator.py"]
        ai_rag["ai/rag_assistant.py"]
    end

    subgraph UI_Tier ["User Interface"]
        terminal_app["ui/terminal_app.py"]
        pages["ui/pages/*.py"]
    end

    models_py --> lakehouse_py
    lakehouse_py --> staging_mgr
    calendar_py --> staging_mgr
    staging_mgr --> duckdb_client
    dq_rules --> dq_suite
    lakehouse_py --> recon
    dq_suite & recon --> alerts
    alerts --> incident_repo

    duckdb_client --> incident_repo
    duckdb_client --> mkt_svc & eq_svc & stk_svc & mac_svc & ops_svc & lin_svc
    duckdb_client & risk_eng --> mf_svc & rsk_svc
    incident_repo & lin_svc --> inc_svc

    ai_safe & ai_gen & duckdb_client --> ai_rag

    mkt_svc & eq_svc & stk_svc & mf_svc & mac_svc & rsk_svc & ops_svc & lin_svc & inc_svc & ai_rag --> pages
    pages --> terminal_app
```

---

## 8. Blueprint H: Chronological Pipeline Execution Sequence

This sequence diagram depicts the chronological step-by-step execution flow of the daily batch data engineering cycle:

```mermaid
sequenceDiagram
    autonumber
    actor Engineer as Data Engineer / Airflow Scheduler
    participant P1 as Phase 1: Bronze Ingestion<br/>(scripts/run_phase1_ingestion.py)
    participant P2 as Phase 2: Silver Staging<br/>(scripts/run_phase2_staging.py)
    participant P3 as Phase 3: dbt Pipeline<br/>(scripts/run_phase3_pipeline.py)
    participant P4 as Phase 4: DQ Audit<br/>(scripts/run_phase4_dq_audit.py)
    participant Tests as Test Suite Verification<br/>(pytest -v tests/)
    participant UI as Financial Terminal<br/>(streamlit run ui/terminal_app.py)

    Engineer->>P1: Execute Phase 1 Ingestion
    P1->>P1: Ingest NSE Stocks, AMFI NAVs, RBI Macro
    P1->>P1: Compute SHA-256 batch fingerprints
    P1->>P1: Commit Hive-partitioned Parquet files & manifests
    P1-->>Engineer: ✅ Bronze Layer Committed (163 raw records)

    Engineer->>P2: Execute Phase 2 Staging
    P2->>P2: Read Bronze Parquet partitions
    P2->>P2: Deduplicate ticks on natural keys (symbol, trade_date)
    P2->>P2: Audit NSE trading calendar & validate holidays
    P2->>P2: Load cleaned staging tables into DuckDB
    P2-->>Engineer: ✅ Silver Staging Committed (133 records, 30 dups pruned)

    Engineer->>P3: Execute Phase 3 dbt Pipeline
    P3->>P3: Compile 13 dbt models (Staging ➔ Intermediate ➔ Facts)
    P3->>P3: Execute 67 automated dbt tests (uniqueness, boundaries, parity)
    alt Any dbt Test Fails
        P3->>Engineer: 🛑 Circuit Breaker Tripped! Execution Halted
    else 67/67 Tests Pass
        P3-->>Engineer: ✅ Gold Star Schema Marts Certified (0.65s)
    end

    Engineer->>P4: Execute Phase 4 Data Quality Audit
    P4->>P4: Run 17 Python data contracts & statistical anomaly checks
    P4->>P4: Perform cross-layer reconciliation (Bronze 163 ➔ Silver 133 ➔ Gold 133)
    P4->>P4: Generate data/quality/dq_scorecard.md (100.0% Verified)
    P4-->>Engineer: ✅ Data Quality Scorecard Published

    Engineer->>Tests: Run Pytest Test Suite
    Tests->>Tests: Execute 45 unit, AI safety, DQ, risk, and service tests
    Tests-->>Engineer: ✅ 45/45 Passed (1.25s)

    Engineer->>UI: Launch Streamlit Terminal App (Port 8502)
    UI-->>Engineer: 🚀 Financial Terminal Online across 11 Workspaces
```

---

## 9. Blueprint I: Star Schema Dimensional Entity-Relationship Model (ERD)

The Gold layer models financial assets according to Ralph Kimball's dimensional modeling principles:

```mermaid
erDiagram
    dim_date ||--o{ fact_daily_prices : "has observation date"
    dim_date ||--o{ fact_macro_indicators : "has observation date"
    dim_date ||--o{ fact_mf_nav : "has observation date"
    dim_security ||--o{ fact_daily_prices : "trades asset"
    dim_sector ||--o{ dim_security : "classifies industry"
    dim_fund ||--o{ fact_mf_nav : "declares NAV"

    dim_date {
        integer date_id PK "YYYYMMDD surrogate integer key"
        date calendar_date "Standard ISO calendar date"
        varchar indian_fiscal_year "Indian fiscal year: FY2025-26"
        integer fiscal_quarter "Quarter: Q1 (Apr-Jun) to Q4 (Jan-Mar)"
        boolean is_trading_day "TRUE if active NSE trading session"
        varchar holiday_name "Official holiday name or NULL"
    }

    dim_security {
        varchar security_id PK "Surrogate key: SEC_RELIANCE"
        varchar symbol "NSE ticker symbol (e.g., RELIANCE)"
        varchar company_name "Full registered corporate name"
        varchar sector_id FK "Reference to dim_sector"
        varchar sector_name "Sector classification"
        boolean is_nifty50 "TRUE if constituent of Nifty 50 index"
    }

    dim_sector {
        varchar sector_id PK "Surrogate key: SECT_IT"
        varchar sector_name "Sector name (Information Technology)"
        varchar benchmark_index "Sectoral index (e.g., NIFTY IT)"
    }

    dim_fund {
        varchar fund_id PK "Surrogate key: FUND_122639"
        varchar scheme_code "Official AMFI scheme code"
        varchar scheme_name "Parag Parikh Flexi Cap Fund"
        varchar fund_category "Flexi Cap / Large Cap / Small Cap"
        varchar benchmark_name "Nifty 500 TRI / Nifty 50 TRI"
    }

    fact_daily_prices {
        varchar price_fact_id PK "Surrogate key: PRF_symbol_date"
        varchar security_id FK "Foreign key to dim_security"
        integer date_id FK "Foreign key to dim_date"
        date trade_date "Market session date"
        double open_price "Opening traded price in INR"
        double high_price "Session maximum price in INR"
        double low_price "Session minimum price in INR"
        double close_price "Official closing traded price in INR"
        bigint volume "Total share volume traded"
        double daily_return_pct "Percentage change from prior close"
        double sma_20 "20-day Simple Moving Average"
        double sma_50 "50-day Simple Moving Average"
        double ema_12 "12-day Exponential Moving Average"
        double ema_26 "26-day Exponential Moving Average"
        double macd_line "EMA_12 minus EMA_26"
        double macd_signal_line "9-day EMA of MACD Line"
        double macd_histogram "MACD Line minus Signal Line"
        double rsi_14 "14-day Relative Strength Index (0 to 100)"
        double bollinger_upper "SMA_20 plus 2 standard deviations"
        double bollinger_middle "20-day Simple Moving Average"
        double bollinger_lower "SMA_20 minus 2 standard deviations"
        double high_52w "Windowed 252-day peak price"
        double low_52w "Windowed 252-day trough price"
    }

    fact_macro_indicators {
        varchar macro_fact_id PK "Surrogate key: MAC_code_date"
        varchar indicator_code "Indicator identifier: RBI_REPO_RATE"
        integer date_id FK "Foreign key to dim_date"
        date observation_date "Observation date"
        double indicator_value "Value (e.g., 6.50 for repo rate)"
        varchar frequency "Daily / Monthly / Bi-Monthly"
        varchar unit "Percentage / INR per USD"
    }

    fact_mf_nav {
        varchar nav_fact_id PK "Surrogate key: NAV_scheme_date"
        varchar fund_id FK "Foreign key to dim_fund"
        integer date_id FK "Foreign key to dim_date"
        varchar scheme_code "AMFI scheme code"
        date nav_date "Official declaration date"
        double nav "Net Asset Value per unit in INR"
        double daily_return_pct "Percentage change from prior NAV"
        double nav_high_52w "52-week rolling peak NAV"
        double nav_low_52w "52-week rolling trough NAV"
    }
```
