{{ config(materialized='table') }}

WITH technicals AS (
    SELECT * FROM {{ ref('int_stock_technicals') }}
),

securities AS (
    SELECT * FROM {{ ref('dim_security') }}
),

calendar AS (
    SELECT * FROM {{ ref('dim_date') }}
),

joined AS (
    SELECT
        -- Surrogate Primary Key
        t.stock_price_id AS price_fact_id,

        -- Dimensional Foreign Keys
        s.security_id,
        c.date_id,
        
        -- Degenerate Dimensions
        t.symbol,
        t.trade_date,
        
        -- OHLCV Core Metrics
        t.open_price,
        t.high_price,
        t.low_price,
        t.close_price,
        t.adj_close_price,
        t.volume,

        -- Returns & Technicals
        t.prev_close_price,
        t.daily_return_pct,
        t.intraday_range_pct,
        t.sma_20,
        t.sma_50,
        t.sma_200,
        t.high_52w,
        t.low_52w,
        t.is_volume_spike,
        t.avg_prior_20_volume,
        t.is_split_adjusted,
        t.data_source

    FROM technicals t
    INNER JOIN securities s ON t.symbol = s.symbol
    INNER JOIN calendar c ON t.trade_date = c.calendar_date
)

SELECT * FROM joined
