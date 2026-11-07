{{ config(materialized='view') }}

WITH base_prices AS (
    SELECT * FROM {{ ref('stg_stocks') }}
),

lagged AS (
    SELECT
        stock_price_id,
        symbol,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        adj_close_price,
        volume,
        is_split_adjusted,
        data_source,

        -- Previous Trading Session Close (Ordering strictly by trade_date per symbol)
        LAG(close_price, 1) OVER (
            PARTITION BY symbol 
            ORDER BY trade_date ASC
        ) AS prev_close_price

    FROM base_prices
),

returns_computed AS (
    SELECT
        stock_price_id,
        symbol,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        adj_close_price,
        volume,
        is_split_adjusted,
        data_source,
        prev_close_price,

        -- Daily Percentage Return: (Close - Prev_Close) / Prev_Close
        CASE 
            WHEN prev_close_price IS NOT NULL AND prev_close_price > 0
            THEN ROUND((close_price - prev_close_price) / prev_close_price, 6)
            ELSE NULL 
        END AS daily_return_pct,

        -- Daily Intraday Volatility Range: (High - Low) / Close
        CASE 
            WHEN close_price > 0 
            THEN ROUND((high_price - low_price) / close_price, 6)
            ELSE 0.0 
        END AS intraday_range_pct

    FROM lagged
)

SELECT * FROM returns_computed
