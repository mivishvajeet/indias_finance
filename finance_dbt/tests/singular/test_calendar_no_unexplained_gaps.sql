-- Singular Test: Trading Calendar Integrity
-- Returns any price fact records that fall on declared weekend or exchange holiday dates.
-- In a validated pipeline, 0 rows should be returned.

SELECT 
    f.price_fact_id,
    f.symbol,
    f.trade_date,
    d.is_trading_day,
    d.holiday_description
FROM {{ ref('fact_daily_prices') }} f
INNER JOIN {{ ref('dim_date') }} d ON f.date_id = d.date_id
WHERE d.is_trading_day = FALSE
