{{ config(materialized='table') }}

WITH date_spine AS (
    -- Generates calendar dates for 2024, 2025, and 2026 using DuckDB generate_series
    SELECT 
        CAST(d AS DATE) AS calendar_date
    FROM generate_series(DATE '2024-01-01', DATE '2026-12-31', INTERVAL '1 day') AS t(d)
),

holidays AS (
    SELECT 
        CAST(holiday_date AS DATE) AS holiday_date,
        TRIM(description) AS holiday_description
    FROM {{ ref('nse_trading_holidays') }}
),

enriched_calendar AS (
    SELECT
        -- Surrogate Key (YYYYMMDD integer format for Kimball dimensional modeling)
        CAST(strftime(calendar_date, '%Y%m%d') AS INTEGER) AS date_id,
        calendar_date,
        
        -- Calendar breakdown
        EXTRACT(YEAR FROM calendar_date) AS calendar_year,
        EXTRACT(MONTH FROM calendar_date) AS calendar_month,
        strftime(calendar_date, '%B') AS month_name,
        EXTRACT(QUARTER FROM calendar_date) AS calendar_quarter,
        EXTRACT(WEEK FROM calendar_date) AS calendar_week,
        EXTRACT(DOW FROM calendar_date) AS day_of_week_num, -- 0=Sunday, 6=Saturday
        strftime(calendar_date, '%A') AS day_name,
        
        -- Indian Fiscal Year (April 1 to March 31)
        CASE 
            WHEN EXTRACT(MONTH FROM calendar_date) >= 4 
            THEN CONCAT('FY', CAST(EXTRACT(YEAR FROM calendar_date) + 1 AS VARCHAR))
            ELSE CONCAT('FY', CAST(EXTRACT(YEAR FROM calendar_date) AS VARCHAR))
        END AS indian_fiscal_year,

        -- Trading vs Non-Trading Day Logic
        CASE 
            WHEN EXTRACT(DOW FROM calendar_date) IN (0, 6) THEN TRUE 
            ELSE FALSE 
        END AS is_weekend,

        CASE 
            WHEN h.holiday_date IS NOT NULL THEN TRUE 
            ELSE FALSE 
        END AS is_holiday,

        COALESCE(h.holiday_description, 'None') AS holiday_description,

        -- Critical Exchange Session Flag
        CASE 
            WHEN EXTRACT(DOW FROM calendar_date) IN (0, 6) THEN FALSE
            WHEN h.holiday_date IS NOT NULL THEN FALSE
            ELSE TRUE
        END AS is_trading_day

    FROM date_spine d
    LEFT JOIN holidays h ON d.calendar_date = h.holiday_date
)

SELECT * FROM enriched_calendar
