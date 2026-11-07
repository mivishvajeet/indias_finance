{{ config(materialized='view') }}

WITH source_data AS (
    SELECT * FROM {{ source('raw_staging', 'stg_stocks_daily') }}
),

standardized AS (
    SELECT
        -- Surrogate Primary Key
        MD5(CONCAT(TRIM(symbol), '_', CAST(trade_date AS VARCHAR))) AS stock_price_id,
        
        -- Dimensions & Ticker normalization
        UPPER(TRIM(symbol)) AS symbol,
        CAST(trade_date AS DATE) AS trade_date,
        
        -- Numeric OHLCV metrics
        CAST(ROUND(open, 2) AS DOUBLE) AS open_price,
        CAST(ROUND(high, 2) AS DOUBLE) AS high_price,
        CAST(ROUND(low, 2) AS DOUBLE) AS low_price,
        CAST(ROUND(close, 2) AS DOUBLE) AS close_price,
        CAST(ROUND(adj_close, 2) AS DOUBLE) AS adj_close_price,
        CAST(volume AS BIGINT) AS volume,
        
        -- Lineage, Audit & Flags
        CAST(is_split_adjusted AS BOOLEAN) AS is_split_adjusted,
        TRIM(source) AS data_source,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at_utc,
        TRIM(payload_hash) AS raw_payload_hash

    FROM source_data
    WHERE symbol IS NOT NULL 
      AND trade_date IS NOT NULL
      AND close IS NOT NULL
      AND close > 0
)

SELECT * FROM standardized
