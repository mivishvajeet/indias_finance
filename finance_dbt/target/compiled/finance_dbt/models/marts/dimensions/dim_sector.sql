

WITH securities AS (
    SELECT * FROM "curated"."main_marts"."dim_security"
),

sector_rollup AS (
    SELECT
        MD5(UPPER(TRIM(sector_name))) AS sector_id,
        sector_name,
        COUNT(CASE WHEN security_type = 'EQUITY' THEN 1 END) AS total_equities_tracked,
        COUNT(CASE WHEN security_type = 'INDEX' THEN 1 END) AS total_indices_tracked
    FROM securities
    GROUP BY sector_name
)

SELECT * FROM sector_rollup