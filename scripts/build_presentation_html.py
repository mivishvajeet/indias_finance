import os
import json
from pathlib import Path

out_path = Path("docs/India_Finance_Intelligence_Presentation.html")

slides = [
    {
        "id": 1,
        "badge": "PLATFORM LAUNCH & ARCHITECTURAL KEYNOTE",
        "title": "INDIA FINANCE INTELLIGENCE TERMINAL",
        "subtitle": "Institutional Financial Research × Data Engineering Observability × Local AI",
        "content": """
        <div class="hero-center">
            <div class="terminal-badge-hero">🇮🇳 INDIAN CAPITAL MARKETS LAKEHOUSE</div>
            <p class="hero-desc">An end-to-end Medallion Lakehouse platform for NSE Equities, AMFI Mutual Funds, and RBI/MOSPI Macroeconomic Indicators engineered with automated circuit breakers, 100% data quality, and safe local AI.</p>
            <div class="metric-grid-4">
                <div class="stat-card">
                    <span class="stat-val color-green">112 / 112</span>
                    <span class="stat-lbl">Automated Tests PASS</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-green">100.0%</span>
                    <span class="stat-lbl">Verified Data Quality</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-blue">11</span>
                    <span class="stat-lbl">Institutional Workspaces</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-yellow">₹0.00</span>
                    <span class="stat-lbl">Cloud Execution Cost</span>
                </div>
            </div>
            <div class="tech-tag-row">
                <span class="tech-tag">DuckDB (In-Process OLAP)</span>
                <span class="tech-tag">dbt-duckdb</span>
                <span class="tech-tag">Apache Parquet</span>
                <span class="tech-tag">Python 3.12</span>
                <span class="tech-tag">Streamlit</span>
                <span class="tech-tag">Pytest</span>
                <span class="tech-tag">Local AST Text-to-SQL</span>
            </div>
        </div>
        """,
        "notes": "Introduce the India Finance Intelligence Terminal as an institutional-grade Medallion Lakehouse platform built for Indian capital markets. Emphasize that it's not a superficial dashboard over static CSVs, but a complete data engineering system with raw Parquet partitioning, SHA-256 idempotency, automated circuit breakers, and explainable local AI."
    },
    {
        "id": 2,
        "badge": "EXECUTIVE SUMMARY",
        "title": "The Project At A Glance",
        "subtitle": "Three Interconnected Capabilities Delivering Institutional Rigor",
        "content": """
        <div class="cards-grid-3">
            <div class="feature-card border-green">
                <div class="card-icon">📈</div>
                <h3>1. Financial Intelligence</h3>
                <p>Institutional equity and fund research for Indian capital markets.</p>
                <ul>
                    <li>Nifty 50 constituents & sector benchmarks</li>
                    <li>Multi-factor equity screener (RSI, SMA, MACD)</li>
                    <li>AMFI mutual fund NAV historical tracking</li>
                    <li>RBI repo rate & MOSPI inflation indicators</li>
                    <li>Quantitative risk scorecard (Sharpe vs 6.5% G-Sec)</li>
                </ul>
            </div>
            <div class="feature-card border-blue">
                <div class="card-icon">🛡️</div>
                <h3>2. Data Trust & Observability</h3>
                <p>Medallion Lakehouse with automated circuit breakers and lineage.</p>
                <ul>
                    <li>Bronze Hive-partitioned Parquet with SHA-256 manifests</li>
                    <li>Silver conformed deduplication on natural keys</li>
                    <li>NSE Trading Calendar Validator (Diwali/Holi holidays)</li>
                    <li>67 dbt tests + 17 Python data contracts (100% Verified)</li>
                    <li>Interactive Lineage DAG & incident blast-radius analysis</li>
                </ul>
            </div>
            <div class="feature-card border-yellow">
                <div class="card-icon">🤖</div>
                <h3>3. Safe Local AI</h3>
                <p>Deterministic analytical assistant operating offline at ₹0 cost.</p>
                <ul>
                    <li>Local schema-aware text-to-SQL translation</li>
                    <li>AST-based SELECT-only safety enforcement</li>
                    <li>Zero mutating queries (DROP/DELETE/UPDATE blocked)</li>
                    <li>Execution against read-only DuckDB connection</li>
                    <li>Answers returned with exact SQL & data provenance</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Walk through the three pillars: Financial Intelligence, Data Trust, and Local AI. Explain that every metric shown in the research terminal is backed by rigorous upstream lakehouse engineering."
    },
    {
        "id": 3,
        "badge": "PROBLEM STATEMENT",
        "title": "The Real-World Financial Data Challenge",
        "subtitle": "Why Downloading CSVs and Plotting Charts Fails in Enterprise Fintech",
        "content": """
        <div class="compare-container">
            <div class="compare-box box-bad">
                <h4 class="color-red">❌ The Naive Dashboard Approach</h4>
                <ul>
                    <li><b>Network Fragility:</b> Calling public APIs in UI code leads to HTTP 429 rate limit crashes.</li>
                    <li><b>Duplicate Ingestion:</b> Retrying failed jobs duplicates ticks, corrupting VWAP and volume.</li>
                    <li><b>Calendar Blindness:</b> Western calendars misclassify Indian holidays (Diwali, Holi) as dropouts.</li>
                    <li><b>Formula Drift:</b> Different teams calculate divergent RSI or Sharpe values in spreadsheets.</li>
                    <li><b>Database Locks:</b> Concurrent analytical reads lock embedded engines.</li>
                </ul>
            </div>
            <div class="compare-box box-good">
                <h4 class="color-green">✅ Our Medallion Lakehouse Solution</h4>
                <ul>
                    <li><b>Resilient Extraction:</b> Exponential backoff, jitter, and browser User-Agent rotation.</li>
                    <li><b>Idempotent Bronze:</b> SHA-256 batch fingerprints skip duplicate writes with 0 disk I/O.</li>
                    <li><b>NSE Calendar Validator:</b> Accurately discriminates official exchange closures from true gaps.</li>
                    <li><b>Governed SQL Technicals:</b> Standardized dbt marts verified via Pandas parity tests.</li>
                    <li><b>Decoupled Concurrency:</b> Read-only analytics connection pool prevents all lock contention.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Discuss real-world failure modes in financial data engineering. Explain why commercial-grade systems require idempotency, calendar validation, and automated quality gates."
    },
    {
        "id": 4,
        "badge": "INGESTION LAYER",
        "title": "Multi-Source Market Data Acquisition",
        "subtitle": "Aggregating Equities, Mutual Funds, and Macroeconomic Indicators",
        "content": """
        <div class="sources-grid-4">
            <div class="source-card">
                <div class="source-header">NSE Equities</div>
                <div class="source-meta">via yfinance</div>
                <p>22 Nifty 50 constituents + ^NSEI index daily OHLCV bars in INR.</p>
                <span class="freq-tag">Daily at 15:30 IST</span>
            </div>
            <div class="source-card">
                <div class="source-header">AMFI Mutual Funds</div>
                <div class="source-meta">Official AMFI Portal</div>
                <p>Historical Net Asset Value (NAV) declarations for top equity schemes.</p>
                <span class="freq-tag">Daily at 21:00 IST</span>
            </div>
            <div class="source-card">
                <div class="source-header">RBI Monetary Policy</div>
                <div class="source-meta">Reserve Bank of India</div>
                <p>Official Policy Repo Rate time-series and banking liquidity indicators.</p>
                <span class="freq-tag">Bi-Monthly MPC</span>
            </div>
            <div class="source-card">
                <div class="source-header">MOSPI Macro Data</div>
                <div class="source-meta">Central Statistics Office</div>
                <p>Consumer Price Index (CPI) Combined Inflation and WPI series.</p>
                <span class="freq-tag">Monthly (12th)</span>
            </div>
        </div>
        <div class="callout-box">
            <b>Resilient Network Base Client:</b> All connectors inherit from <code>src/ingestion/base_client.py</code>, enforcing exponential backoff ($T = \text{delay} \times 2^{\text{attempt}-1}$) and rotating across 6 modern browser User-Agent headers.
        </div>
        """,
        "notes": "Detail the 4 primary data sources and explain how the abstract base client handles rate limiting and network failures."
    },
    {
        "id": 5,
        "badge": "SCHEMA CONTRACTS",
        "title": "Raw Data Formats & Ingestion Contracts",
        "subtitle": "Defensive Pydantic DataClass Enforcement at the Ingestion Boundary",
        "content": """
        <div class="code-and-table-layout">
            <div class="layout-left">
                <h4>Raw Payload Inconsistencies</h4>
                <p>External sources return wildly divergent structures: AMFI uses semicolon-separated strings; macro endpoints return flat observation series; equity feeds return multi-level column indexes.</p>
                <div class="code-snippet">
<span class="c-comment"># AMFI Raw String Extract:</span>
122639;Parag Parikh Flexi Cap Fund;72.4512;;;26-Jun-2026

<span class="c-comment"># Ingestion Contract Enforcement:</span>
@dataclass(frozen=True)
class DailyStockBar:
    symbol: str
    trade_date: datetime.date
    close_price: float  <span class="c-comment"># asserted > 0</span>
    volume: int         <span class="c-comment"># asserted >= 0</span>
                </div>
            </div>
            <div class="layout-right">
                <h4>Schema Assertion Matrix</h4>
                <table class="data-table">
                    <tr><th>Entity</th><th>Natural Key</th><th>Key Constraint</th></tr>
                    <tr><td>DailyStockBar</td><td><code>(symbol, trade_date)</code></td><td><code>close > 0, high >= low</code></td></tr>
                    <tr><td>MacroRecord</td><td><code>(code, observation_date)</code></td><td><code>value is not null</code></td></tr>
                    <tr><td>MutualFundNAV</td><td><code>(scheme_code, nav_date)</code></td><td><code>nav > 0</code></td></tr>
                </table>
            </div>
        </div>
        """,
        "notes": "Demonstrate data contract discipline. Explain that malformed or negative prices are caught by Pydantic dataclasses before touching disk."
    },
    {
        "id": 6,
        "badge": "SYSTEM ARCHITECTURE",
        "title": "End-to-End System Blueprint",
        "subtitle": "Complete Data Lifecycle from External Extraction to Serving Terminal",
        "content": """
        <div class="arch-flow-diagram">
            <div class="flow-step step-source">
                <span class="step-num">1</span>
                <b>Data Sources</b>
                <span>NSE • AMFI • RBI • MOSPI</span>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step step-bronze">
                <span class="step-num">2</span>
                <b>Bronze Lakehouse</b>
                <span>Parquet + SHA-256 Manifests</span>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step step-silver">
                <span class="step-num">3</span>
                <b>Silver Staging</b>
                <span>Deduplication & Calendar Audit</span>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step step-gold">
                <span class="step-num">4</span>
                <b>Gold Marts</b>
                <span>13 dbt Star Schema Models</span>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step step-quality">
                <span class="step-num">5</span>
                <b>Quality Gates</b>
                <span>112 Automated Tests (100%)</span>
            </div>
            <div class="flow-arrow">➔</div>
            <div class="flow-step step-serving">
                <span class="step-num">6</span>
                <b>Terminal UI</b>
                <span>11 Workspaces + Local AI</span>
            </div>
        </div>
        <div class="arch-bullets">
            <p>• <b>Storage-Compute Decoupling:</b> Apache Parquet raw partitions decoupled from DuckDB in-process vectorized execution.</p>
            <p>• <b>Zero Lock Contention:</b> Analytical queries access <code>curated.duckdb</code> in read-only mode; stateful logs write to <code>operational_metadata.duckdb</code>.</p>
        </div>
        """,
        "notes": "Walk through the high-level 6-step flow. Point out the decoupling of storage and compute, and how concurrency is solved by separating read-only marts from operational logs."
    },
    {
        "id": 7,
        "badge": "LAKEHOUSE DESIGN",
        "title": "Medallion Lakehouse Architecture",
        "subtitle": "Bronze (Raw Immutability) ➔ Silver (Conformed) ➔ Gold (Dimensional Marts)",
        "content": """
        <div class="cards-grid-3">
            <div class="medallion-card med-bronze">
                <div class="med-badge">BRONZE LAYER</div>
                <h4>Raw Lakehouse Storage</h4>
                <ul>
                    <li>Format: Apache Parquet (Snappy compressed)</li>
                    <li>Hive Partitioning: <code>year/month/day/</code></li>
                    <li>SHA-256 batch cryptographic manifests</li>
                    <li>Immutable append-only history preserving raw ticks</li>
                    <li>Physical Row Count: <b>163 records</b></li>
                </ul>
            </div>
            <div class="medallion-card med-silver">
                <div class="med-badge">SILVER LAYER</div>
                <h4>Cleaned & Conformed Staging</h4>
                <ul>
                    <li>Engine: DuckDB In-Process Columnar Views</li>
                    <li>Deduplication: Natural keys <code>(symbol, date)</code></li>
                    <li>Calendar Audit: NSE official holiday validation</li>
                    <li>Boundary Clamping: <code>close > 0, nav > 0</code></li>
                    <li>Physical Row Count: <b>133 records (-30 dups)</b></li>
                </ul>
            </div>
            <div class="medallion-card med-gold">
                <div class="med-badge">GOLD LAYER</div>
                <h4>Curated Star Schema Marts</h4>
                <ul>
                    <li>Modeling: Ralph Kimball Dimensional Star Schema</li>
                    <li>Calendar: Indian Fiscal Year (April to March)</li>
                    <li>SQL Technicals: RSI 14, Bollinger Bands, MACD</li>
                    <li>Risk Engine: CAGR, Sharpe, Sortino, Drawdowns</li>
                    <li>Physical Row Count: <b>133 records (100% retention)</b></li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Explain why each Medallion tier exists. Emphasize that Bronze preserves raw data for auditability, Silver conformed staging cleanses ticks, and Gold dimensional marts serve fast analytics."
    },
    {
        "id": 8,
        "badge": "PHYSICAL STORAGE",
        "title": "Bronze Layer: Raw Partitioned Ingestion",
        "subtitle": "Hive-Style Directory Partitioning with Companion Batch Metadata",
        "content": """
        <div class="code-and-table-layout">
            <div class="layout-left">
                <h4>Hive Partition Tree on Disk</h4>
                <div class="code-snippet">
data/lakehouse/raw/
├── stocks_daily/
│   └── year=2026/month=06/day=25/
│       ├── stocks_daily_9a4f2c1b.parquet
│       └── stocks_daily_manifest.json
├── mf_nav/
│   └── year=2026/month=06/day=25/
│       ├── mf_nav_8e3c1d9a.parquet
│       └── mf_nav_manifest.json
└── macro_indicators/
    └── year=2026/month=06/day=25/
        ├── macro_indicators_2c8a2e42.parquet
        └── macro_indicators_manifest.json
                </div>
            </div>
            <div class="layout-right">
                <h4>Why Hive Partitioning & Parquet?</h4>
                <ul>
                    <li><b>Partition Pruning:</b> DuckDB skips scanning non-matching year/month directories entirely during date filters.</li>
                    <li><b>Column Projection:</b> Queries requesting only <code>close_price</code> never read other column bytes off disk.</li>
                    <li><b>Dictionary Compression:</b> Ticker strings and exchange codes compress down by 75-80% using Snappy.</li>
                    <li><b>Embedded Statistics:</b> Parquet row groups store min/max values for rapid range skipping.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Show the exact directory structure on disk. Explain how Hive partitioning enables partition pruning and how Parquet columnar projection accelerates analytical queries."
    },
    {
        "id": 9,
        "badge": "DATA INTEGRITY",
        "title": "Mathematical Idempotency Deep Dive",
        "subtitle": "Cryptographic SHA-256 Batch Fingerprinting Guarantees Zero Duplicate Writes",
        "content": """
        <div class="idempotency-box">
            <div class="idemp-step">
                <div class="idemp-icon">1️⃣</div>
                <b>Sort & Canonicalize</b>
                <p>Incoming DataFrame rows are deterministically sorted by primary keys: <code>(symbol, trade_date)</code>.</p>
            </div>
            <div class="idemp-arrow">➔</div>
            <div class="idemp-step">
                <div class="idemp-icon">2️⃣</div>
                <b>SHA-256 Digest</b>
                <p>Canonical row bytes are hashed into a 12-char SHA-256 digest: <code>hashlib.sha256(bytes).hexdigest()</code>.</p>
            </div>
            <div class="idemp-arrow">➔</div>
            <div class="idemp-step">
                <div class="idemp-icon">3️⃣</div>
                <b>Manifest Check</b>
                <p>Storage manager reads <code>{dataset}_manifest.json</code> in the target partition directory.</p>
            </div>
            <div class="idemp-arrow">➔</div>
            <div class="idemp-step">
                <div class="idemp-icon">4️⃣</div>
                <b>Decision Gate</b>
                <p><b>Match:</b> Skip write (0 Disk I/O).<br/><b>Mismatch:</b> Write new Parquet batch & update manifest.</p>
            </div>
        </div>
        <div class="test-evidence-box">
            <b>Automated Test Evidence:</b> <code>tests/unit/test_phase1_ingestion.py::test_idempotent_skip_on_identical_payload</code> verifies that re-running identical batch ingestion yields <code>commit_status = 'SKIPPED_DUPLICATE'</code> and 0 byte disk writes.
        </div>
        """,
        "notes": "Walk through the 4-step idempotency algorithm. Mention that this prevents partition explosion and duplicate tick corruption during pipeline retries."
    },
    {
        "id": 10,
        "badge": "SILVER STAGING",
        "title": "Silver Layer: Cleansing & Deduplication",
        "subtitle": "Pruning Overlapping Ticks & Enforcing Positive Boundary Contracts",
        "content": """
        <div class="compare-container">
            <div class="compare-box">
                <h4>Bronze Raw Payload (163 records)</h4>
                <p>Contains network retry overlap (30 duplicate tick bars):</p>
                <div class="code-snippet">
{"symbol": "RELIANCE", "date": "2026-06-25", "close": 2978.20, "vol": 5421900}
{"symbol": "RELIANCE", "date": "2026-06-25", "close": 2978.20, "vol": 5421900} <span class="c-comment"># DUP</span>
{"symbol": "TCS",      "date": "2026-06-25", "close": 3840.50, "vol": 2100400}
{"symbol": "TCS",      "date": "2026-06-25", "close": -10.00,  "vol": 100}     <span class="c-comment"># DEFECT</span>
                </div>
            </div>
            <div class="compare-box">
                <h4>Silver Conformed Staging (133 records)</h4>
                <p>Deduplicated on <code>(symbol, date)</code>; defective ticks clamped:</p>
                <div class="code-snippet">
{"stock_price_id": "STK_RELIANCE_20260625", "close": 2978.20, "vol": 5421900}
{"stock_price_id": "STK_TCS_20260625",      "close": 3840.50, "vol": 2100400}
<span class="c-comment"># Result: 30 duplicate ticks pruned; negative prices rejected.</span>
                </div>
            </div>
        </div>
        <div class="metrics-summary-strip">
            <span>Raw Bronze Rows: <b>163</b></span> | 
            <span>Deduplication Delta: <b class="color-yellow">-30</b></span> | 
            <span>Cleaned Silver Rows: <b class="color-green">133</b></span> | 
            <span>Surrogate Key: <code>SHA256(symbol + date)</code></span>
        </div>
        """,
        "notes": "Explain how Silver conformed staging works. Cite the exact verified numbers: 163 raw records in Bronze, 30 duplicate ticks removed by deduplication, 133 cleaned records in Silver."
    },
    {
        "id": 11,
        "badge": "DOMAIN ENGINEERING",
        "title": "Indian Trading Calendar Validation",
        "subtitle": "Accurately Discriminating Official Exchange Holidays from Critical Dropouts",
        "content": """
        <div class="calendar-layout">
            <div class="cal-left">
                <h4>The Indian Market Nuance</h4>
                <p>Standard Monday-to-Friday calendars trigger false data loss alarms on official Indian holidays. Our <code>TradingCalendarValidator</code> loads official NSE circular dates:</p>
                <ul>
                    <li>Republic Day (Jan 26)</li>
                    <li>Mahashivratri & Holi</li>
                    <li>Independence Day (Aug 15)</li>
                    <li>Diwali Laxmi Pujan (Muhurat session)</li>
                    <li>Christmas (Dec 25)</li>
                </ul>
            </div>
            <div class="cal-right">
                <h4>Audit Logic & Test Verification</h4>
                <div class="code-snippet">
def audit_trading_coverage(df, date_col):
    for dt in date_range(min_date, max_date):
        if dt not in df_dates:
            if dt in nse_holidays:
                <span class="c-comment"># Official Holiday: PASS (No alert)</span>
                continue
            else:
                <span class="c-comment"># Critical Data Dropout: TRIP CIRCUIT BREAKER</span>
                dispatch_alert("DATA_DROPOUT_DETECTED", dt)
                </div>
            </div>
        </div>
        <div class="callout-box">
            <b>Test Evidence:</b> <code>tests/unit/test_phase2_staging.py::test_official_nse_holiday_detection</code> proves Diwali sessions are correctly marked closed without tripping alerts.
        </div>
        """,
        "notes": "Discuss the Indian trading calendar validator. Explain that standard Western calendars generate alert fatigue on Indian national holidays, and show how our custom validator solves this."
    },
    {
        "id": 12,
        "badge": "ANALYTICS ENGINEERING",
        "title": "Gold Layer: dbt Transformations",
        "subtitle": "13 Modular SQL Models Compiled into DuckDB Star Schema Marts",
        "content": """
        <div class="dbt-grid-3">
            <div class="dbt-card">
                <div class="dbt-badge">STAGING (3 Views)</div>
                <p>Casts types and validates non-null constraints:</p>
                <ul>
                    <li><code>stg_stocks.sql</code></li>
                    <li><code>stg_macro.sql</code></li>
                    <li><code>stg_mf_nav.sql</code></li>
                </ul>
            </div>
            <div class="dbt-card">
                <div class="dbt-badge">INTERMEDIATE (3 Views)</div>
                <p>Vectorized SQL technical calculations:</p>
                <ul>
                    <li><code>int_stock_daily_returns.sql</code></li>
                    <li><code>int_stock_ema_macd.sql</code></li>
                    <li><code>int_stock_technicals.sql</code></li>
                </ul>
            </div>
            <div class="dbt-card">
                <div class="dbt-badge">MARTS (7 Tables)</div>
                <p>Kimball star schema dimensions and facts:</p>
                <ul>
                    <li><code>dim_date.sql</code> (Indian FY)</li>
                    <li><code>dim_security.sql</code> / <code>dim_sector.sql</code></li>
                    <li><code>dim_fund.sql</code> (AMFI schemes)</li>
                    <li><code>fact_daily_prices.sql</code></li>
                    <li><code>fact_macro_indicators.sql</code></li>
                    <li><code>fact_mf_nav.sql</code></li>
                </ul>
            </div>
        </div>
        <div class="metrics-summary-strip">
            <span>Materialization: Views (Staging/Intermediate) ➔ Base Tables (Marts)</span> | 
            <span>Execution Time: <b>0.65s</b></span>
        </div>
        """,
        "notes": "Walk through the 13 dbt models across staging, intermediate, and marts layers. Emphasize that intermediate models calculate indicators in SQL for vectorized efficiency."
    },
    {
        "id": 13,
        "badge": "DATA MODELING",
        "title": "Dimensional Star Schema Modeling",
        "subtitle": "Ralph Kimball Dimensional Design Tailored for Financial Analytics",
        "content": """
        <div class="erd-visual-container">
            <div class="erd-center-box">
                <b>fact_daily_prices</b>
                <span>Grain: (security_id, date_id)</span>
                <span class="erd-fields">price_fact_id [PK] • security_id [FK] • date_id [FK] • close_price • daily_return_pct • sma_20 • sma_50 • rsi_14 • macd_line • bollinger_upper • bollinger_lower • high_52w</span>
            </div>
            <div class="erd-surround-grid">
                <div class="erd-card">
                    <b>dim_date (Indian FY)</b>
                    <span>date_id [PK] • calendar_date • fiscal_year (FY2025-26) • fiscal_quarter (Q1-Q4) • is_trading_day</span>
                </div>
                <div class="erd-card">
                    <b>dim_security</b>
                    <span>security_id [PK] • symbol • company_name • sector_id [FK] • is_nifty50</span>
                </div>
                <div class="erd-card">
                    <b>dim_sector</b>
                    <span>sector_id [PK] • sector_name • benchmark_index (NIFTY IT, BANK)</span>
                </div>
                <div class="erd-card">
                    <b>dim_fund</b>
                    <span>fund_id [PK] • scheme_code • scheme_name • category</span>
                </div>
            </div>
        </div>
        """,
        "notes": "Walk through the star schema ERD. Highlight the conformed dimensions (dim_date, dim_security, dim_fund) and explain the grain of fact_daily_prices."
    },
    {
        "id": 14,
        "badge": "QUANTITATIVE FINANCE",
        "title": "Financial Calculations & Quantitative Risk Engine",
        "subtitle": "High-Precision Vectorized Indicator Mathematics & G-Sec Risk Benchmarking",
        "content": """
        <div class="cards-grid-2">
            <div class="quant-card">
                <h4>SQL Technical Indicators (dbt)</h4>
                <ul>
                    <li><b>RSI 14:</b> Smoothed price gains/losses: $100 - \frac{100}{1 + RS}$ clamped between 0 and 100.</li>
                    <li><b>Bollinger Bands:</b> 20-day SMA $\pm 2\sigma_{20}$ standard deviation bounds.</li>
                    <li><b>EMA 12 / 26 & MACD:</b> Exponential smoothing approximations with 9-day signal crossovers.</li>
                    <li><b>52-Week Bounds:</b> <code>MAX(high) OVER (ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)</code>.</li>
                </ul>
            </div>
            <div class="quant-card">
                <h4>Python Risk Engine (src/analytics/risk_engine.py)</h4>
                <ul>
                    <li><b>CAGR:</b> Exact fractional year compounding: $(V_n / V_0)^{(365.25 / \text{days})} - 1$.</li>
                    <li><b>Annualized Volatility:</b> $\sigma_{\text{daily}} \times \sqrt{252}$ (Indian 252-day market year).</li>
                    <li><b>Sharpe Ratio:</b> Excess return over official <b>6.50% Indian 10Y G-Sec</b> benchmark.</li>
                    <li><b>Sortino Ratio:</b> Penalizes strictly downside variance below risk-free rate.</li>
                    <li><b>Max Drawdown:</b> Peak-to-trough capital impairment series: $\min((P_t - P_{\text{peak}}) / P_{\text{peak}})$.</li>
                </ul>
            </div>
        </div>
        <div class="callout-box">
            <b>Automated Parity Proof:</b> <code>tests/unit/test_dbt_pandas_indicator_parity.py</code> asserts $|dbt - Pandas| < 10^{-4}$ row-by-row.
        </div>
        """,
        "notes": "Explain both the SQL technicals in dbt and the Python vectorized risk engine. Highlight the 6.5% G-Sec risk-free rate and the 252 trading day annualization factor."
    },
    {
        "id": 15,
        "badge": "DATA QUALITY",
        "title": "Enterprise Data Quality & Circuit Breakers",
        "subtitle": "Two-Tier Quality Defense: 67 dbt Assertions + 17 Python Data Contracts",
        "content": """
        <div class="cards-grid-2">
            <div class="dq-card">
                <h4>Tier 1: dbt Automated Tests (67 Assertions)</h4>
                <ul>
                    <li><b>Uniqueness:</b> PKs on all dimensions and facts (0 duplicates allowed).</li>
                    <li><b>Referential Integrity:</b> Foreign keys join seamlessly to parent dimensions.</li>
                    <li><b>Positive Bounds:</b> <code>price_positive</code> macro ensures close > 0 and nav > 0.</li>
                    <li><b>RSI Bounds:</b> <code>rsi_bounds</code> macro enforces $0 \le RSI \le 100$.</li>
                    <li><b>Singular Reconcile:</b> <code>test_reconcile_staging_fact_rows.sql</code>.</li>
                </ul>
            </div>
            <div class="dq-card">
                <h4>Tier 2: Python DQ Suite (17 Rules)</h4>
                <ul>
                    <li><b>Statistical Anomaly:</b> Audits z-score outliers and volatility bounds.</li>
                    <li><b>Temporal Continuity:</b> Flags unlisted market day gaps.</li>
                    <li><b>Composite Score:</b> Calculated dynamically from test outcomes: <b>100.0%</b>.</li>
                    <li><b>Automated Circuit Breaker:</b> Tripping any critical test immediately halts downstream publication and alerts engineers.</li>
                </ul>
            </div>
        </div>
        <div class="metrics-summary-strip">
            <span>dbt Tests: <b class="color-green">67 / 67 PASS</b></span> | 
            <span>Python DQ Rules: <b class="color-green">17 / 17 PASS</b></span> | 
            <span>Quality Score: <b class="color-green">100.0% Verified</b></span>
        </div>
        """,
        "notes": "Detail the two-tier data quality framework: 67 dbt tests plus 17 Python statistical rules. Explain that tests act as blocking circuit breakers."
    },
    {
        "id": 16,
        "badge": "DATA OBSERVABILITY",
        "title": "Cross-Layer Lakehouse Reconciliation",
        "subtitle": "Proving Zero Unexplained Data Loss from Raw Files to Analytics Marts",
        "content": """
        <div class="waterfall-layout">
            <div class="waterfall-step wf-bronze">
                <span class="wf-val">163</span>
                <b>Bronze Raw</b>
                <span class="wf-note">Raw ingested ticks</span>
            </div>
            <div class="waterfall-delta wf-neg">
                <span class="wf-val">-30</span>
                <b>Deduplication Delta</b>
                <span class="wf-note">Pruned duplicate raw ticks</span>
            </div>
            <div class="waterfall-step wf-silver">
                <span class="wf-val">133</span>
                <b>Silver Cleaned</b>
                <span class="wf-note">Unique conformed ticks</span>
            </div>
            <div class="waterfall-delta wf-zero">
                <span class="wf-val">0</span>
                <b>Transformation Loss</b>
                <span class="wf-note">0 unexplained dropouts</span>
            </div>
            <div class="waterfall-step wf-gold">
                <span class="wf-val">133</span>
                <b>Gold Fact Marts</b>
                <span class="wf-note">Certified fact rows</span>
            </div>
        </div>
        <div class="reconcile-card">
            <h4>Mathematical Retention Formula</h4>
            <p>$$\text{Fact Retention Rate} = \frac{\text{Gold Fact Records}}{\text{Silver Conformed Records}} = \frac{133}{133} = \mathbf{100.0\%}$$</p>
            <p>Audited by <code>LakehouseReconciliationAuditor</code> in <code>src/quality/reconciliation_auditor.py</code>.</p>
        </div>
        """,
        "notes": "Walk through the reconciliation waterfall: 163 Bronze rows, minus 30 duplicate ticks in Silver, equals 133 rows in Gold, proving 100% retention and zero unexplained data loss."
    },
    {
        "id": 17,
        "badge": "TESTING ARCHITECTURE",
        "title": "Automated Testing & Parity Verification",
        "subtitle": "112 Passing Tests Verifying Ingestion, Calendar, Indicators, AI, and Services",
        "content": """
        <div class="test-table-container">
            <table class="data-table">
                <thead>
                    <tr><th>Test Suite</th><th>Engine</th><th>Tests</th><th>Pass Rate</th><th>Execution Time</th></tr>
                </thead>
                <tbody>
                    <tr><td><b>dbt Schema, Generic & Singular Tests</b></td><td>dbt-duckdb</td><td><b>67</b></td><td><b>100.0%</b></td><td>0.65s</td></tr>
                    <tr><td><b>Platform Services & Analytics</b></td><td>pytest</td><td>8</td><td>100.0%</td><td>0.35s</td></tr>
                    <tr><td><b>SQL Safety & AI Guardrails</b></td><td>pytest</td><td>3</td><td>100.0%</td><td>0.05s</td></tr>
                    <tr><td><b>Lakehouse Storage & Partitioning</b></td><td>pytest</td><td>9</td><td>100.0%</td><td>0.40s</td></tr>
                    <tr><td><b>Trading Calendar & Staging</b></td><td>pytest</td><td>6</td><td>100.0%</td><td>0.35s</td></tr>
                    <tr><td><b>Boundary Stress & Reconciliation</b></td><td>pytest</td><td>3</td><td>100.0%</td><td>0.15s</td></tr>
                    <tr><td><b>Data Quality Suite & Alerts</b></td><td>pytest</td><td>8</td><td>100.0%</td><td>0.30s</td></tr>
                    <tr><td><b>Mutual Fund & Risk Engine</b></td><td>pytest</td><td>7</td><td>100.0%</td><td>0.25s</td></tr>
                    <tr><td><b>dbt-Pandas Indicator Parity</b></td><td>pytest</td><td>1</td><td>100.0%</td><td>0.05s</td></tr>
                    <tr class="tr-total"><td><b>TOTAL AUTOMATED VERIFICATION</b></td><td><b>All Suites</b></td><td><b>112</b></td><td><b>100.0%</b></td><td><b>&lt; 3s</b></td></tr>
                </tbody>
            </table>
        </div>
        """,
        "notes": "Point out the 112 automated test count and show that tests execute in under 3 seconds across both dbt and pytest."
    },
    {
        "id": 18,
        "badge": "FINANCIAL TERMINAL",
        "title": "Workspaces 1 & 2: Market Overview & Screener",
        "subtitle": "Institutional Indian Equity Research & Multi-Factor Filtering",
        "content": """
        <div class="screenshot-layout">
            <div class="ss-left">
                <img src="assets/page_1_market_intelligence_rendered_1794054266869.png" class="terminal-img" alt="Market Intelligence Overview"/>
            </div>
            <div class="ss-right">
                <h4>Workspace 1: Market Overview</h4>
                <ul>
                    <li>Real-time quotes for NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT.</li>
                    <li>Visual market breadth advances/declines ratio gauge.</li>
                    <li>Top gainers and losers ranked by session volume.</li>
                    <li>Deterministic educational technical observations.</li>
                </ul>
                <h4 style="margin-top: 15px;">Workspace 2: Equity Screener</h4>
                <ul>
                    <li>Multi-factor filtering across RSI 14, SMA 20/50, and MACD.</li>
                    <li>52-week high proximity slider (e.g., stocks within 5% of peak).</li>
                    <li>1-click instant CSV export of filtered institutional universes.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Show the live Market Overview and Equity Screener screenshots. Highlight the Bloomberg dark theme and tabular typography."
    },
    {
        "id": 19,
        "badge": "FINANCIAL TERMINAL",
        "title": "Workspaces 3 & 4: Stock Analytics & Mutual Funds",
        "subtitle": "3-Tier Candlestick Subplots & AMFI Relative Trajectory Benchmarking",
        "content": """
        <div class="screenshot-layout">
            <div class="ss-left">
                <img src="assets/page_2_mutual_fund_risk_engine_1794054287354.png" class="terminal-img" alt="Mutual Fund Trajectory"/>
            </div>
            <div class="ss-right">
                <h4>Workspace 3: Stock Analytics</h4>
                <ul>
                    <li>3-Tier Interactive Subplots: Candlestick OHLCV, RSI 14 with 70/30 bands, MACD signal line and histogram.</li>
                    <li>Bollinger Bands (20, 2σ) overlaid on price trajectory.</li>
                    <li>Historical daily return distribution histogram with normal fit.</li>
                </ul>
                <h4 style="margin-top: 15px;">Workspace 4: Mutual Fund Intelligence</h4>
                <ul>
                    <li>Rebased relative NAV comparison curves (all schemes rebased to 100).</li>
                    <li>Underwater drawdown curves across market cycles.</li>
                    <li>Institutional scorecard: CAGR, Volatility, Sharpe, Sortino vs 6.5% G-Sec.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Present the 3-tier stock analytics subplots and mutual fund rebased performance charts. Note the 6.5% G-Sec risk-free rate disclosure."
    },
    {
        "id": 20,
        "badge": "QUANTITATIVE RESEARCH",
        "title": "Workspaces 5 & 6: Macro & Risk Analytics",
        "subtitle": "Monetary Policy Indicators & Cross-Asset Risk-Return Frontier",
        "content": """
        <div class="screenshot-layout">
            <div class="ss-left">
                <img src="assets/page_4_macroeconomic_indicators_1794054304336.png" class="terminal-img" alt="Macro Trends"/>
            </div>
            <div class="ss-right">
                <h4>Workspace 5: Macro Intelligence</h4>
                <ul>
                    <li>Official RBI Monetary Policy Repo Rate trajectory tracking.</li>
                    <li>MOSPI Consumer Price Index (CPI) and WPI inflation series.</li>
                    <li>USD/INR foreign exchange daily spot rates.</li>
                </ul>
                <h4 style="margin-top: 15px;">Workspace 6: Risk Analytics</h4>
                <ul>
                    <li>Cross-asset Risk-Return Frontier (Plotly scatter bubble plot).</li>
                    <li>X-axis: Annualized Volatility; Y-axis: CAGR; Bubble Size: Sharpe Ratio.</li>
                    <li>Pearson correlation matrix across equities, mutual funds, and FX.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Demonstrate how macro indicators connect with the risk-return frontier and Pearson correlation heatmap."
    },
    {
        "id": 21,
        "badge": "DATA OBSERVABILITY",
        "title": "Workspace 7: Data Operations Center",
        "subtitle": "Physical Partition Inspection & Ingestion Pipeline Execution Telemetry",
        "content": """
        <div class="ops-telemetry-container">
            <div class="pipeline-status-flow">
                <div class="pipe-node status-success">BRONZE INGESTION<br/><span>✅ 5.2s • 163 rows</span></div>
                <div class="pipe-arrow">➔</div>
                <div class="pipe-node status-success">SILVER STAGING<br/><span>✅ 2.1s • 133 rows</span></div>
                <div class="pipe-arrow">➔</div>
                <div class="pipe-node status-success">GOLD DBT RUN<br/><span>✅ 0.8s • 13 models</span></div>
                <div class="pipe-arrow">➔</div>
                <div class="pipe-node status-success">QUALITY AUDIT<br/><span>✅ 1.2s • 112 tests</span></div>
            </div>
            <div class="cards-grid-3" style="margin-top: 20px;">
                <div class="stat-card">
                    <span class="stat-val color-blue">Hive Partition Monitor</span>
                    <p>Scans disk partitions: <code>stocks_daily</code>, <code>mf_nav</code>, <code>macro_indicators</code> with companion SHA-256 manifests.</p>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-green">Idempotency Status</span>
                    <p><b>ACTIVE:</b> Duplicate batches detected and skipped automatically. Zero disk write bloat.</p>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-yellow">Run Log Repository</span>
                    <p>Searchable audit trail queried dynamically from DuckDB's <code>pipeline_execution_runs</code>.</p>
                </div>
            </div>
        </div>
        """,
        "notes": "Show the Data Operations Center. Explain that physical partition counts and execution durations are queried dynamically from lakehouse manifests and DuckDB tables."
    },
    {
        "id": 22,
        "badge": "DATA OBSERVABILITY",
        "title": "Workspace 8: Data Quality Center",
        "subtitle": "Continuous Quality Auditing, Failure Drill-Down, and Scorecards",
        "content": """
        <div class="screenshot-layout">
            <div class="ss-left">
                <img src="assets/page_3_data_quality_center_1794054341660.png" class="terminal-img" alt="Data Quality Center"/>
            </div>
            <div class="ss-right">
                <h4>Data Quality Observability Highlights</h4>
                <ul>
                    <li><b>Composite Quality Score:</b> Real-time calculated score: <b>100.0% Verified</b>.</li>
                    <li><b>Rule Assertions Matrix:</b> Inspects all 17 rules across completeness, uniqueness, boundaries, and temporal continuity.</li>
                    <li><b>Reconciliation Waterfall:</b> Renders Bronze ➔ Silver ➔ Gold physical record yields.</li>
                    <li><b>Downloadable Reports:</b> Exports verified Markdown and JSON quality scorecards for enterprise compliance audits.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Explain the Data Quality Center. Emphasize that the 100% score is computed dynamically from actual test executions, not hardcoded."
    },
    {
        "id": 23,
        "badge": "METADATA LINEAGE",
        "title": "Workspace 9: Data Lineage Explorer",
        "subtitle": "Interactive Directed Acyclic Graph (DAG) Tracing Asset Provenance",
        "content": """
        <div class="lineage-container">
            <div class="lineage-dag-mini">
                <div class="dag-layer">
                    <span class="layer-title">Sources</span>
                    <div class="dag-node node-source">NSE yfinance</div>
                    <div class="dag-node node-source">AMFI Portal</div>
                </div>
                <div class="dag-layer">
                    <span class="layer-title">Bronze</span>
                    <div class="dag-node node-bronze">stocks_daily.parquet</div>
                    <div class="dag-node node-bronze">mf_nav.parquet</div>
                </div>
                <div class="dag-layer">
                    <span class="layer-title">Silver</span>
                    <div class="dag-node node-silver">stg_stocks</div>
                    <div class="dag-node node-silver">stg_mf_nav</div>
                </div>
                <div class="dag-layer">
                    <span class="layer-title">Intermediate</span>
                    <div class="dag-node node-int">int_stock_technicals</div>
                    <div class="dag-node node-int">int_stock_ema_macd</div>
                </div>
                <div class="dag-layer">
                    <span class="layer-title">Gold Marts</span>
                    <div class="dag-node node-gold">fact_daily_prices</div>
                    <div class="dag-node node-gold">fact_mf_nav</div>
                </div>
                <div class="dag-layer">
                    <span class="layer-title">Serving</span>
                    <div class="dag-node node-ui">Stock Analytics UI</div>
                    <div class="dag-node node-ui">Risk Scorecard UI</div>
                </div>
            </div>
            <div class="callout-box">
                <b>Interactive Node Inspector:</b> Built by parsing dbt's <code>manifest.json</code> and DuckDB schemas. Clicking any node reveals materialization type, row count, column definitions, and immediate upstream/downstream dependencies.
            </div>
        </div>
        """,
        "notes": "Demonstrate the interactive Data Lineage Explorer. Show how a portfolio manager or auditor can trace any metric back to its source extract."
    },
    {
        "id": 24,
        "badge": "RELIABILITY ENGINEERING",
        "title": "Workspace 10: Data Incident Center",
        "subtitle": "State Machine Incident Tracking & Upstream/Downstream Blast-Radius Analysis",
        "content": """
        <div class="cards-grid-2">
            <div class="inc-card">
                <h4>Incident Lifecycle State Machine</h4>
                <div class="state-machine-row">
                    <span class="state-chip state-det">DETECTED</span> ➔ 
                    <span class="state-chip state-ack">ACKNOWLEDGED</span> ➔ 
                    <span class="state-chip state-inv">INVESTIGATING</span> ➔ 
                    <span class="state-chip state-res">RESOLVED</span>
                </div>
                <p style="margin-top: 15px;">Persisted in <code>operational_metadata.duckdb</code>. Allows engineers to log remediation notes, change severity levels, and track mean-time-to-resolution (MTTR).</p>
            </div>
            <div class="inc-card">
                <h4>Lineage Blast-Radius Impact Analysis</h4>
                <p>When an incident occurs on a table or model, the Incident Service queries the Lineage DAG:</p>
                <ul>
                    <li><b>Upstream Root Cause:</b> Traces back to source files and extraction batches.</li>
                    <li><b>Downstream Blast Radius:</b> Instantly highlights all affected marts and analytical dashboards.</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Discuss the Data Incident Center. Explain the state machine and emphasize the blast-radius analysis feature that connects incidents with data lineage."
    },
    {
        "id": 25,
        "badge": "APPLIED AI",
        "title": "Workspace 11: Ask Finance AI",
        "subtitle": "Safe Local Text-to-SQL Assistant with AST-Enforced Read-Only Guardrails",
        "content": """
        <div class="cards-grid-2">
            <div class="ai-card">
                <h4>Natural Language Query Flow</h4>
                <div class="flow-mini">
                    <span>1. User Question: <i>"Which funds have the highest Sharpe ratio?"</i></span><br/>
                    <span>2. Local Schema Translation ➔ DuckDB SQL</span><br/>
                    <span>3. AST Security Gate: Enforces SELECT-Only</span><br/>
                    <span>4. Execution against <code>curated.duckdb</code> (read-only)</span><br/>
                    <span>5. Direct Answer + SQL Code + Data Provenance Citations</span>
                </div>
            </div>
            <div class="ai-card">
                <h4>AST SQL Safety Guardrails</h4>
                <table class="data-table">
                    <tr><th>Security Assertion</th><th>Status</th></tr>
                    <tr><td>Enforce SELECT / WITH starting keyword</td><td><b class="color-green">ENFORCED</b></td></tr>
                    <tr><td>Block DROP, DELETE, UPDATE, ALTER, TRUNCATE</td><td><b class="color-green">BLOCKED</b></td></tr>
                    <tr><td>Reject semicolon multi-statement injection</td><td><b class="color-green">BLOCKED</b></td></tr>
                    <tr><td>Restrict execution to whitelisted tables</td><td><b class="color-green">ENFORCED</b></td></tr>
                </table>
            </div>
        </div>
        <div class="metrics-summary-strip">
            <span>Operating Cost: <b>₹0.00 (Zero paid cloud APIs)</b></span> | 
            <span>Safety Test Coverage: <b>tests/ai/test_sql_safety.py (100% PASS)</b></span>
        </div>
        """,
        "notes": "Demonstrate Ask Finance AI. Highlight the AST safety layer that blocks mutations, and note that answers always include SQL code and observation date citations."
    },
    {
        "id": 26,
        "badge": "SYSTEM DESIGN",
        "title": "Technology Decision Matrix",
        "subtitle": "Justifying Every Architectural Choice Against Production Trade-Offs",
        "content": """
        <table class="data-table">
            <thead>
                <tr><th>Technology</th><th>Chosen For</th><th>Replaced Alternative</th><th>Key Architectural Advantage</th></tr>
            </thead>
            <tbody>
                <tr><td><b>DuckDB</b></td><td>In-process columnar OLAP</td><td>PostgreSQL</td><td>Vectorized execution; zero server admin; 10-50x faster on analytical aggregations.</td></tr>
                <tr><td><b>Apache Parquet</b></td><td>Bronze raw storage</td><td>CSV / JSON</td><td>Snappy compression; column projection pruning; typed schemas.</td></tr>
                <tr><td><b>dbt-duckdb</b></td><td>Modular SQL modeling</td><td>Custom Python scripts</td><td>Dependency DAG management; automated testing; single source of indicator truth.</td></tr>
                <tr><td><b>Streamlit</b></td><td>Financial terminal UI</td><td>React / Power BI</td><td>Rapid analytical iteration; dark terminal styling; zero license costs.</td></tr>
                <tr><td><b>Pytest</b></td><td>Automated testing</td><td>Unittest</td><td>Rich assertions; fixture parameterization; 45 automated tests in 1.25s.</td></tr>
            </tbody>
        </table>
        """,
        "notes": "Review the technology decision matrix. Be ready to explain why DuckDB was chosen over Postgres and why dbt was chosen over Python transformations."
    },
    {
        "id": 27,
        "badge": "PROBLEM SOLVING",
        "title": "Five Core Engineering Challenges Solved",
        "subtitle": "Real-World Technical Difficulties Encountered and Overcome",
        "content": """
        <div class="challenges-grid">
            <div class="ch-box">
                <b>1. Idempotent Ingestion:</b> Solved duplicate partition explosion using SHA-256 batch manifests (0 disk I/O on re-runs).
            </div>
            <div class="ch-box">
                <b>2. Calendar Discrimination:</b> Built official NSE holiday validator, eliminating false alerts on Diwali and Holi.
            </div>
            <div class="ch-box">
                <b>3. DuckDB Lock Contention:</b> Decoupled read-only analytical connections from read-write operational stores.
            </div>
            <div class="ch-box">
                <b>4. Mathematical Indicator Parity:</b> Proved row-by-row parity between dbt SQL and Pandas indicators within $10^{-4}$.
            </div>
            <div class="ch-box">
                <b>5. Local AI SQL Security:</b> Implemented AST-level parser enforcing SELECT-only syntax and blocking mutations.
            </div>
        </div>
        """,
        "notes": "Summarize the 5 major engineering challenges solved. This shows senior problem-solving and architectural maturity."
    },
    {
        "id": 28,
        "badge": "ROADMAP",
        "title": "Production Readiness & Enterprise Cloud Roadmap",
        "subtitle": "Direct Mapping from Local In-Process Platform to Multi-Terabyte AWS Scale",
        "content": """
        <div class="compare-container">
            <div class="compare-box">
                <h4>Local In-Process Architecture (Current ₹0)</h4>
                <ul>
                    <li>Storage: Local disk partitioned Parquet files</li>
                    <li>Compute: DuckDB in-process columnar engine</li>
                    <li>Orchestration: Local Python runners & test scripts</li>
                    <li>Serving: Streamlit on local port 8502</li>
                    <li>Metadata: <code>operational_metadata.duckdb</code></li>
                </ul>
            </div>
            <div class="compare-box">
                <h4>Enterprise Cloud Target (AWS Scale)</h4>
                <ul>
                    <li>Storage: <b>Amazon S3</b> (<code>s3://india-finance-lakehouse/</code>)</li>
                    <li>Compute: <b>AWS EMR Spark / Databricks</b> (dbt-spark)</li>
                    <li>Orchestration: <b>Amazon MWAA</b> (Managed Airflow DAGs)</li>
                    <li>Serving: <b>AWS ECS Fargate</b> (Containerized Streamlit)</li>
                    <li>Metadata: <b>Amazon RDS PostgreSQL</b></li>
                </ul>
            </div>
        </div>
        <div class="callout-box">
            <b>Zero Rework Migration:</b> Because dbt models and Parquet partitions are open standards, moving compute from DuckDB to Spark/Databricks requires zero rewriting of dimensional business logic.
        </div>
        """,
        "notes": "Explain how the platform scales to AWS. Emphasize that because we use open standards (Parquet, dbt, SQL), business logic does not need to be rewritten."
    },
    {
        "id": 29,
        "badge": "PROFESSIONAL COMPETENCE",
        "title": "Demonstrated Technical Competencies",
        "subtitle": "End-to-End Capabilities Across Data Engineering, Analytics & AI",
        "content": """
        <div class="cards-grid-4">
            <div class="skill-card">
                <b>Data Engineering</b>
                <ul>
                    <li>Hive Partitioning</li>
                    <li>SHA-256 Idempotency</li>
                    <li>Resilient Connectors</li>
                    <li>Cross-Layer Recon</li>
                </ul>
            </div>
            <div class="skill-card">
                <b>Analytics Engineering</b>
                <ul>
                    <li>Kimball Star Schema</li>
                    <li>13 dbt-duckdb Models</li>
                    <li>SQL Window Indicator Math</li>
                    <li>Indian Fiscal Year Calendar</li>
                </ul>
            </div>
            <div class="skill-card">
                <b>Observability & SRE</b>
                <ul>
                    <li>112 Automated Tests</li>
                    <li>Circuit Breakers</li>
                    <li>Interactive Lineage DAG</li>
                    <li>Incident Blast Radius</li>
                </ul>
            </div>
            <div class="skill-card">
                <b>Applied AI</b>
                <ul>
                    <li>Safe Text-to-SQL</li>
                    <li>AST Syntax Parsing</li>
                    <li>Provenance Citations</li>
                    <li>Zero API Cost Local Ops</li>
                </ul>
            </div>
        </div>
        """,
        "notes": "Summarize the skills demonstrated across the four key data disciplines. This bridges technical execution with candidate qualifications."
    },
    {
        "id": 30,
        "badge": "CLOSING SUMMARY",
        "title": "INDIA FINANCE INTELLIGENCE TERMINAL",
        "subtitle": "Financial Intelligence. Data Integrity. Explainable Analytics.",
        "content": """
        <div class="hero-center">
            <div class="terminal-badge-hero">PROJECT COMPLETE & VERIFIED</div>
            <p class="hero-desc">An end-to-end institutional financial data platform proving that analytics are only as reliable as the data engineering foundation beneath them.</p>
            <div class="metric-grid-4">
                <div class="stat-card">
                    <span class="stat-val color-green">100%</span>
                    <span class="stat-lbl">Quality Scorecard</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-green">112 / 112</span>
                    <span class="stat-lbl">Tests Passing</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-blue">11</span>
                    <span class="stat-lbl">Workspaces Live</span>
                </div>
                <div class="stat-card">
                    <span class="stat-val color-yellow">0.00%</span>
                    <span class="stat-lbl">Unexplained Data Loss</span>
                </div>
            </div>
            <div class="footer-links">
                <p><b>GitHub:</b> github.com/mivishvajeet/indias_finance &nbsp;|&nbsp; <b>Terminal:</b> localhost:8502 &nbsp;|&nbsp; <b>Handbook:</b> docs/PROJECT_TECHNICAL_HANDBOOK.md</p>
            </div>
        </div>
        """,
        "notes": "Deliver the closing statement. Reiterate that 112/112 tests pass and invite questions."
    }
]

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>India Finance Intelligence Terminal — Institutional Presentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #080C12;
            --bg-secondary: #0D131D;
            --bg-panel: #111A26;
            --bg-elevated: #172231;
            --border: #253346;
            --text-primary: #E6EDF5;
            --text-secondary: #91A0B3;
            --text-muted: #64748B;
            --green: #00C087;
            --red: #FF5C65;
            --yellow: #F5B942;
            --blue: #45A3FF;
            --purple: #A78BFA;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            user-select: none;
        }

        /* Top Nav Bar */
        .topbar {
            height: 52px;
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 100;
            position: relative;
        }

        .brand-title {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-badge {
            background: rgba(0, 192, 135, 0.15);
            border: 1px solid var(--green);
            color: var(--green);
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }

        .top-controls {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .btn-ctrl {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'JetBrains Mono', monospace;
        }

        .btn-ctrl:hover {
            background: var(--bg-elevated);
            color: var(--text-primary);
            border-color: var(--blue);
        }

        .btn-ctrl.active {
            background: rgba(69, 163, 255, 0.2);
            border-color: var(--blue);
            color: var(--blue);
        }

        /* Slide Stage */
        .deck-container {
            height: calc(100vh - 52px - 36px);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px 48px;
        }

        .slide {
            position: absolute;
            width: calc(100% - 96px);
            max-width: 1400px;
            height: 100%;
            display: none;
            flex-direction: column;
            justify-content: flex-start;
            opacity: 0;
            transform: scale(0.98) translateY(10px);
            transition: opacity 0.35s ease, transform 0.35s ease;
            overflow-y: auto;
            padding-right: 8px;
        }

        .slide.active {
            display: flex;
            opacity: 1;
            transform: scale(1) translateY(0);
        }

        /* Slide Header */
        .slide-header {
            margin-bottom: 20px;
        }

        .slide-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            letter-spacing: 1.5px;
            color: var(--blue);
            text-transform: uppercase;
            margin-bottom: 6px;
            display: inline-block;
        }

        .slide-title {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.5px;
            line-height: 1.2;
        }

        .slide-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        /* Content Layout Components */
        .hero-center {
            text-align: center;
            margin: auto;
            max-width: 950px;
        }

        .terminal-badge-hero {
            display: inline-block;
            background: rgba(0, 192, 135, 0.1);
            border: 1px solid var(--green);
            color: var(--green);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 16px;
            border-radius: 20px;
            margin-bottom: 20px;
        }

        .hero-desc {
            font-size: 18px;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 30px;
        }

        .metric-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
            text-align: center;
        }

        .stat-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 26px;
            font-weight: 700;
            display: block;
            margin-bottom: 4px;
        }

        .stat-lbl {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .tech-tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }

        .tech-tag {
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 4px;
        }

        .cards-grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .cards-grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .cards-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }

        .feature-card, .medallion-card, .quant-card, .dq-card, .inc-card, .ai-card, .skill-card, .source-card, .ch-box {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 20px;
        }

        .border-green { border-top: 3px solid var(--green); }
        .border-blue { border-top: 3px solid var(--blue); }
        .border-yellow { border-top: 3px solid var(--yellow); }

        .feature-card h3, .quant-card h4, .dq-card h4, .inc-card h4, .ai-card h4 {
            font-size: 16px;
            margin-bottom: 12px;
            color: var(--text-primary);
        }

        .feature-card p, .card-desc {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 14px;
            line-height: 1.5;
        }

        .feature-card ul, .medallion-card ul, .quant-card ul, .dq-card ul, .inc-card ul, .ss-right ul, .compare-box ul, .cal-left ul, .skill-card ul {
            list-style: none;
            padding: 0;
        }

        .feature-card li, .medallion-card li, .quant-card li, .dq-card li, .inc-card li, .ss-right li, .compare-box li, .cal-left li, .skill-card li {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            position: relative;
            padding-left: 16px;
            line-height: 1.5;
        }

        .feature-card li::before, .medallion-card li::before, .quant-card li::before, .dq-card li::before, .inc-card li::before, .ss-right li::before, .compare-box li::before, .cal-left li::before, .skill-card li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--blue);
            font-weight: bold;
        }

        .color-green { color: var(--green); }
        .color-red { color: var(--red); }
        .color-blue { color: var(--blue); }
        .color-yellow { color: var(--yellow); }
        .color-purple { color: var(--purple); }

        /* Compare Box */
        .compare-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .compare-box {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 20px;
        }

        .box-bad { border-left: 4px solid var(--red); }
        .box-good { border-left: 4px solid var(--green); }

        .compare-box h4 {
            font-size: 15px;
            margin-bottom: 14px;
        }

        /* Sources Grid */
        .sources-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .source-card {
            text-align: center;
            border-top: 3px solid var(--blue);
        }

        .source-header {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .source-meta {
            font-size: 11px;
            color: var(--text-muted);
            margin-bottom: 10px;
            font-family: 'JetBrains Mono', monospace;
        }

        .source-card p {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 12px;
            line-height: 1.4;
        }

        .freq-tag {
            background: rgba(69, 163, 255, 0.15);
            color: var(--blue);
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: 'JetBrains Mono', monospace;
        }

        .callout-box {
            background: var(--bg-elevated);
            border-left: 3px solid var(--blue);
            padding: 12px 18px;
            font-size: 12px;
            color: var(--text-secondary);
            border-radius: 0 4px 4px 0;
            margin-top: 16px;
            line-height: 1.5;
        }

        /* Code & Layouts */
        .code-and-table-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        .code-snippet {
            background: #05080c;
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #d1d5db;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            margin-top: 10px;
        }

        .c-comment { color: #64748b; font-style: italic; }

        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            background: var(--bg-panel);
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid var(--border);
        }

        .data-table th, .data-table td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }

        .data-table th {
            background: var(--bg-secondary);
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            text-transform: uppercase;
        }

        .data-table td {
            color: var(--text-secondary);
        }

        .tr-total {
            background: var(--bg-elevated);
            font-weight: 700;
        }

        .tr-total td { color: var(--green); }

        /* Flow Diagrams */
        .arch-flow-diagram {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 6px;
            margin-bottom: 20px;
        }

        .flow-step {
            text-align: center;
            flex: 1;
        }

        .step-num {
            display: inline-block;
            width: 22px;
            height: 22px;
            background: var(--blue);
            color: #000;
            font-weight: bold;
            font-size: 11px;
            line-height: 22px;
            border-radius: 50%;
            margin-bottom: 6px;
        }

        .flow-step b {
            display: block;
            font-size: 13px;
            color: var(--text-primary);
            margin-bottom: 4px;
        }

        .flow-step span {
            font-size: 10px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }

        .flow-arrow {
            font-size: 18px;
            color: var(--text-muted);
            padding: 0 8px;
        }

        /* Idempotency Box */
        .idempotency-box {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 6px;
            margin-bottom: 20px;
        }

        .idemp-step {
            flex: 1;
            text-align: center;
            padding: 10px;
        }

        .idemp-icon { font-size: 24px; margin-bottom: 8px; }
        .idemp-step b { display: block; font-size: 14px; margin-bottom: 6px; color: var(--text-primary); }
        .idemp-step p { font-size: 11px; color: var(--text-secondary); line-height: 1.4; }
        .idemp-arrow { font-size: 20px; color: var(--blue); padding: 0 10px; }

        .test-evidence-box {
            background: rgba(0, 192, 135, 0.08);
            border: 1px solid var(--green);
            padding: 12px 18px;
            border-radius: 4px;
            font-size: 12px;
            color: var(--green);
            line-height: 1.5;
        }

        .metrics-summary-strip {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 12px 20px;
            border-radius: 4px;
            margin-top: 16px;
            font-size: 12px;
            color: var(--text-secondary);
            font-family: 'JetBrains Mono', monospace;
            display: flex;
            justify-content: space-around;
        }

        /* Screenshots */
        .screenshot-layout {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 24px;
            align-items: center;
        }

        .terminal-img {
            width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid var(--border);
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }

        /* Waterfall Layout */
        .waterfall-layout {
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 30px;
            border-radius: 6px;
            height: 220px;
            margin-bottom: 20px;
        }

        .waterfall-step, .waterfall-delta {
            text-align: center;
            width: 110px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
        }

        .wf-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .wf-bronze .wf-val { color: var(--blue); }
        .wf-neg .wf-val { color: var(--yellow); }
        .wf-silver .wf-val { color: var(--green); }
        .wf-zero .wf-val { color: var(--text-muted); }
        .wf-gold .wf-val { color: var(--green); }

        .waterfall-step b, .waterfall-delta b {
            font-size: 12px;
            color: var(--text-primary);
            margin-bottom: 4px;
        }

        .wf-note { font-size: 10px; color: var(--text-muted); }

        .reconcile-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 16px 24px;
            border-radius: 6px;
            text-align: center;
        }

        /* Lineage DAG Mini */
        .lineage-dag-mini {
            display: flex;
            justify-content: space-between;
            background: var(--bg-panel);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 6px;
            margin-bottom: 16px;
        }

        .dag-layer {
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
        }

        .layer-title {
            font-size: 10px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        .dag-node {
            padding: 8px 14px;
            border-radius: 4px;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border);
            background: var(--bg-elevated);
        }

        .node-source { border-left: 3px solid #E2E8F0; }
        .node-bronze { border-left: 3px solid #94A3B8; }
        .node-silver { border-left: 3px solid var(--yellow); }
        .node-int { border-left: 3px solid var(--purple); }
        .node-gold { border-left: 3px solid var(--green); }
        .node-ui { border-left: 3px solid var(--blue); }

        /* State Machine */
        .state-machine-row {
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }

        .state-chip {
            padding: 4px 10px;
            border-radius: 3px;
            font-weight: 600;
        }

        .state-det { background: rgba(255, 92, 101, 0.2); color: var(--red); border: 1px solid var(--red); }
        .state-ack { background: rgba(245, 185, 66, 0.2); color: var(--yellow); border: 1px solid var(--yellow); }
        .state-inv { background: rgba(69, 163, 255, 0.2); color: var(--blue); border: 1px solid var(--blue); }
        .state-res { background: rgba(0, 192, 135, 0.2); color: var(--green); border: 1px solid var(--green); }

        .challenges-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }

        .ch-box {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
            border-left: 3px solid var(--blue);
        }

        .ch-box b { color: var(--text-primary); }

        /* Bottom Controls Bar */
        .bottombar {
            height: 36px;
            background-color: var(--bg-secondary);
            border-top: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            font-size: 11px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }

        .progress-bar-container {
            width: 300px;
            height: 4px;
            background: var(--bg-panel);
            border-radius: 2px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: var(--blue);
            width: 3.33%;
            transition: width 0.3s ease;
        }

        /* Speaker Notes Drawer Modal */
        .notes-modal {
            position: fixed;
            bottom: 36px;
            right: 24px;
            width: 480px;
            max-height: 280px;
            background: rgba(17, 26, 38, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            z-index: 200;
            display: none;
            flex-direction: column;
            overflow-y: auto;
        }

        .notes-modal.active { display: flex; }

        .notes-header {
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--blue);
            text-transform: uppercase;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }

        .notes-content {
            font-size: 13px;
            color: #d1d5db;
            line-height: 1.6;
            font-style: italic;
        }

        /* Slide Drawer Overview */
        .overview-drawer {
            position: fixed;
            top: 52px;
            left: 0;
            width: 100vw;
            height: calc(100vh - 52px);
            background: rgba(8, 12, 18, 0.97);
            backdrop-filter: blur(8px);
            z-index: 300;
            display: none;
            padding: 30px 48px;
            overflow-y: auto;
        }

        .overview-drawer.active { display: block; }

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 16px;
        }

        .thumb-card {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.2s;
            height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .thumb-card:hover {
            border-color: var(--blue);
            transform: translateY(-2px);
        }

        .thumb-num {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: var(--blue);
        }

        .thumb-title {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.3;
        }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <div class="topbar">
        <div class="brand-title">
            <span>🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL</span>
            <span class="brand-badge">INSTITUTIONAL PRESENTATION</span>
        </div>
        <div class="top-controls">
            <button class="btn-ctrl" id="btnNotes" onclick="toggleNotes()">🎙️ Speaker Notes (S)</button>
            <button class="btn-ctrl" id="btnGrid" onclick="toggleOverview()">📑 Slide Grid (O)</button>
            <button class="btn-ctrl" onclick="toggleFullscreen()">⛶ Fullscreen (F)</button>
        </div>
    </div>

    <!-- Slide Deck Stage -->
    <div class="deck-container">
"""

for s in slides:
    html_template += f"""
        <!-- SLIDE {s['id']} -->
        <div class="slide {'active' if s['id'] == 1 else ''}" id="slide-{s['id']}" data-slide-num="{s['id']}">
            <div class="slide-header">
                <span class="slide-badge">{s['badge']}</span>
                <h2 class="slide-title">{s['title']}</h2>
                <div class="slide-subtitle">{s['subtitle']}</div>
            </div>
            <div class="slide-body">
                {s['content']}
            </div>
        </div>
    """

html_template += f"""
    </div>

    <!-- Speaker Notes Modal -->
    <div class="notes-modal" id="notesModal">
        <div class="notes-header">
            <span>🎙️ Presenter Script (Slide <span id="notesSlideNum">1</span>/30)</span>
            <span style="cursor: pointer;" onclick="toggleNotes()">✕</span>
        </div>
        <div class="notes-content" id="notesText">
            {slides[0]['notes']}
        </div>
    </div>

    <!-- Overview Grid Drawer -->
    <div class="overview-drawer" id="overviewDrawer">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="font-size: 18px; color: var(--text-primary);">Slide Deck Overview (30 Slides)</h3>
            <button class="btn-ctrl" onclick="toggleOverview()">✕ Close</button>
        </div>
        <div class="overview-grid">
"""

for s in slides:
    html_template += f"""
            <div class="thumb-card" onclick="goToSlide({s['id']})">
                <span class="thumb-num">SLIDE {s['id']:02d}</span>
                <div class="thumb-title">{s['title']}</div>
            </div>
    """

html_template += """
        </div>
    </div>

    <!-- Bottom Status Bar -->
    <div class="bottombar">
        <div>
            <span>Use [←] and [→] arrow keys to navigate &nbsp;|&nbsp; Press [S] for speaker notes</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div class="progress-bar-container">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <span id="slideIndicator">Slide 1 of 30</span>
            <button class="btn-ctrl" onclick="prevSlide()" style="padding: 2px 8px;">◀ Prev</button>
            <button class="btn-ctrl" onclick="nextSlide()" style="padding: 2px 8px;">Next ▶</button>
        </div>
    </div>

    <script>
        const totalSlides = 30;
        let currentSlide = 1;
        const notesMap = """ + json.dumps({s["id"]: s["notes"] for s in slides}) + """;

        function updateSlideView() {
            document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
            const activeSlide = document.getElementById(`slide-${currentSlide}`);
            if (activeSlide) {
                activeSlide.classList.add('active');
            }

            document.getElementById('slideIndicator').innerText = `Slide ${currentSlide} of ${totalSlides}`;
            const pct = (currentSlide / totalSlides) * 100;
            document.getElementById('progressFill').style.width = `${pct}%`;

            document.getElementById('notesSlideNum').innerText = currentSlide;
            document.getElementById('notesText').innerText = notesMap[currentSlide] || "No speaker notes for this slide.";
        }

        function nextSlide() {
            if (currentSlide < totalSlides) {
                currentSlide++;
                updateSlideView();
            }
        }

        function prevSlide() {
            if (currentSlide > 1) {
                currentSlide--;
                updateSlideView();
            }
        }

        function goToSlide(num) {
            currentSlide = num;
            updateSlideView();
            toggleOverview();
        }

        function toggleNotes() {
            const m = document.getElementById('notesModal');
            m.classList.toggle('active');
            document.getElementById('btnNotes').classList.toggle('active');
        }

        function toggleOverview() {
            const d = document.getElementById('overviewDrawer');
            d.classList.toggle('active');
            document.getElementById('btnGrid').classList.toggle('active');
        }

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(() => {});
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
                nextSlide();
            } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                prevSlide();
            } else if (e.key === 'Home') {
                currentSlide = 1;
                updateSlideView();
            } else if (e.key === 'End') {
                currentSlide = totalSlides;
                updateSlideView();
            } else if (e.key === 's' || e.key === 'S') {
                toggleNotes();
            } else if (e.key === 'o' || e.key === 'O' || e.key === 'g' || e.key === 'G') {
                toggleOverview();
            } else if (e.key === 'f' || e.key === 'F') {
                toggleFullscreen();
            }
        });

        updateSlideView();
    </script>
</body>
</html>
"""

with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Successfully generated presentation HTML at {out_path} ({out_path.stat().st_size:,} bytes)!")
