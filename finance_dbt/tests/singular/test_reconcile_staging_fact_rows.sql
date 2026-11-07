-- Singular Test: Cross-Layer Row Count Reconciliation
-- Asserts that the number of unique records in stg_stocks matches fact_daily_prices.
-- In dbt, a test passes if it returns ZERO rows. If counts diverge, this query returns the delta.

WITH staging_counts AS (
    SELECT 
        COUNT(DISTINCT stock_price_id) AS staging_count
    FROM {{ ref('stg_stocks') }}
),

fact_counts AS (
    SELECT 
        COUNT(DISTINCT price_fact_id) AS fact_count
    FROM {{ ref('fact_daily_prices') }}
)

SELECT 
    s.staging_count,
    f.fact_count,
    ABS(s.staging_count - f.fact_count) AS row_divergence
FROM staging_counts s
CROSS JOIN fact_counts f
WHERE s.staging_count != f.fact_count
