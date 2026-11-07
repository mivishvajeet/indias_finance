

WITH macro AS (
    SELECT * FROM "curated"."main_staging"."stg_macro"
),

calendar AS (
    SELECT * FROM "curated"."main_marts"."dim_date"
),

joined AS (
    SELECT
        m.macro_indicator_id AS macro_fact_id,
        c.date_id,
        m.indicator_code,
        m.observation_date,
        m.indicator_value,
        m.frequency,
        m.unit_of_measure,
        m.data_source
    FROM macro m
    INNER JOIN calendar c ON m.observation_date = c.calendar_date
)

SELECT * FROM joined