# 🇮🇳 India Finance Lakehouse Data Quality Scorecard

**Audit Timestamp:** `2026-11-07 12:10:17 UTC`  
**Overall Status:** `🟢 PASSED`  
**Composite Data Quality Score:** `100.0%`  

## 1. Cross-Layer Lakehouse Reconciliation

### 🛡️ Cross-Layer Lakehouse Reconciliation Audit (🟢 VERIFIED)

| Lakehouse Layer | Target Entity | Row Count | Layer Retention / Yield | Deduplication Delta |
| :--- | :--- | :---: | :---: | :---: |
| **Bronze (Raw Lakehouse)** | `data/lakehouse/raw/stocks_daily/*.parquet` | `163` | 100.0% (Baseline) | — |
| **Silver (Cleaned Staging)** | `main_staging.stg_stocks` | `133` | `81.60%` | `-30` rows |
| **Gold (Curated Star Marts)** | `main_marts.fact_daily_prices` | `133` | `100.00%` | `-0` rows |

**Audit Trace Findings:**
- Bronze Raw Parquet records discovered: 163
- Silver Staging records validated: 133
- Gold Fact Daily Prices records compiled: 133
- Deduplication delta: 30 duplicate/overlapping raw bars removed during Silver idempotency deduplication.
- Zero dropout between Silver and Gold; 100% of staged records successfully joined into star schema marts.


## 2. Layer-by-Layer Rule Audit Matrix

| Rule Name | Lakehouse Layer | Category | Records Scanned | Failures | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `not_null_price_fact_id` | `main_marts.fact_daily_prices` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `not_null_security_id` | `main_marts.fact_daily_prices` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `not_null_date_id` | `main_marts.fact_daily_prices` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `not_null_close_price` | `main_marts.fact_daily_prices` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `positive_close_price` | `main_marts.fact_daily_prices` | VALIDITY | 133 | 0 | 🟢 PASS |
| `high_gte_low` | `main_marts.fact_daily_prices` | VALIDITY | 133 | 0 | 🟢 PASS |
| `close_within_high_low` | `main_marts.fact_daily_prices` | VALIDITY | 133 | 0 | 🟢 PASS |
| `rsi_bounds_0_to_100` | `main_marts.fact_daily_prices` | VALIDITY | 133 | 0 | 🟢 PASS |
| `bollinger_band_hierarchy` | `main_marts.fact_daily_prices` | CONSISTENCY | 133 | 0 | 🟢 PASS |
| `extreme_daily_return_anomaly` | `main_marts.fact_daily_prices` | ANOMALY | 133 | 0 | 🟢 PASS |
| `zero_volume_trading_day` | `main_marts.fact_daily_prices` | ANOMALY | 133 | 0 | 🟢 PASS |
| `data_freshness_latency` | `main_marts.fact_daily_prices` | TIMELINESS | 133 | 0 | 🟢 PASS |
| `unique_stock_price_id` | `main_staging.stg_stocks` | CONSISTENCY | 133 | 0 | 🟢 PASS |
| `staging_not_null_symbol` | `main_staging.stg_stocks` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `staging_not_null_trade_date` | `main_staging.stg_stocks` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `staging_not_null_close_price` | `main_staging.stg_stocks` | COMPLETENESS | 133 | 0 | 🟢 PASS |
| `staging_not_null_volume` | `main_staging.stg_stocks` | COMPLETENESS | 133 | 0 | 🟢 PASS |


## 3. Remediation Guidelines


---
*India Finance Intelligence Terminal — Enterprise QA & Data Quality Gate*
