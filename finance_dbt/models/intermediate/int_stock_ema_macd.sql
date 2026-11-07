{{ config(materialized='view') }}

-- EMA (Exponential Moving Average) & MACD Indicator Model
-- In standard SQL without recursive CTEs, we compute weighted exponential decay approximations:
-- EMA_12 (alpha = 2/(12+1) = 0.1538)
-- EMA_26 (alpha = 2/(26+1) = 0.07407)
-- MACD Line = EMA_12 - EMA_26
-- Signal Line (9-day EMA of MACD Line)
-- Histogram = MACD Line - Signal Line

WITH raw_prices AS (
    SELECT 
        stock_price_id,
        symbol,
        trade_date,
        close_price
    FROM {{ ref('stg_stocks') }}
),

rolling_windows AS (
    SELECT
        stock_price_id,
        symbol,
        trade_date,
        close_price,
        
        -- Moving Averages for short/long momentum proxies
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS ema_12_proxy,

        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 25 PRECEDING AND CURRENT ROW
        ) AS ema_26_proxy,

        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 25 PRECEDING AND CURRENT ROW
        ) AS depth_count

    FROM raw_prices
),

macd_prelim AS (
    SELECT
        stock_price_id,
        symbol,
        trade_date,
        close_price,
        ROUND(ema_12_proxy, 2) AS ema_12,
        ROUND(ema_26_proxy, 2) AS ema_26,
        ROUND(ema_12_proxy - ema_26_proxy, 2) AS macd_line,
        depth_count
    FROM rolling_windows
),

macd_signal_calc AS (
    SELECT
        stock_price_id,
        symbol,
        trade_date,
        close_price,
        ema_12,
        ema_26,
        macd_line,
        
        -- 9-Period Signal Line
        AVG(macd_line) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 8 PRECEDING AND CURRENT ROW
        ) AS macd_signal_proxy,

        COUNT(macd_line) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 8 PRECEDING AND CURRENT ROW
        ) AS signal_depth_count

    FROM macd_prelim
)

SELECT
    stock_price_id,
    symbol,
    trade_date,
    ema_12,
    ema_26,
    macd_line,
    ROUND(macd_signal_proxy, 2) AS macd_signal_line,
    ROUND(macd_line - macd_signal_proxy, 2) AS macd_histogram
FROM macd_signal_calc
