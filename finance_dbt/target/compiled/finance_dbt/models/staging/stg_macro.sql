

WITH source_data AS (
    SELECT * FROM "curated"."main"."stg_macro_indicators"
),

standardized AS (
    SELECT
        -- Surrogate Primary Key
        MD5(CONCAT(TRIM(indicator_code), '_', CAST(trade_date AS VARCHAR))) AS macro_indicator_id,
        
        -- Business Keys
        UPPER(TRIM(indicator_code)) AS indicator_code,
        CAST(trade_date AS DATE) AS observation_date,
        
        -- Value & Measurement
        CAST(ROUND(value, 4) AS DOUBLE) AS indicator_value,
        LOWER(TRIM(frequency)) AS frequency,
        TRIM(unit) AS unit_of_measure,
        
        -- Audit
        TRIM(source) AS data_source,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at_utc,
        TRIM(payload_hash) AS raw_payload_hash

    FROM source_data
    WHERE indicator_code IS NOT NULL 
      AND trade_date IS NOT NULL
      AND value IS NOT NULL
)

SELECT * FROM standardized