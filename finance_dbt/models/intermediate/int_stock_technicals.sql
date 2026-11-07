{{ config(materialized='view') }}

WITH daily_returns AS (
    SELECT * FROM {{ ref('int_stock_daily_returns') }}
),

window_aggregates AS (
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
        daily_return_pct,
        intraday_range_pct,

        -- -------------------------------------------------------------
        -- 1. Simple Moving Averages (SMA 20, 50, 200) with Warm-Up Guards
        -- -------------------------------------------------------------
        -- SMA 20: 19 preceding rows + current row = 20 trading sessions
        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS sma_20_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS sma_20_raw,

        -- SMA 50: 49 preceding rows + current row = 50 trading sessions
        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS sma_50_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS sma_50_raw,

        -- SMA 200: 199 preceding rows + current row = 200 trading sessions
        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS sma_200_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS sma_200_raw,

        -- -------------------------------------------------------------
        -- 2. 52-Week High & Low (252 Indian Trading Days in 1 Year)
        -- -------------------------------------------------------------
        MAX(high_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS high_52w,

        MIN(low_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS low_52w,

        -- -------------------------------------------------------------
        -- 3. Volume Spike Detection (Current Volume vs Prior 20-Day Avg)
        -- -------------------------------------------------------------
        AVG(volume) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
        ) AS avg_prior_20_volume

    FROM daily_returns
),

final_technicals AS (
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
        daily_return_pct,
        intraday_range_pct,

        -- Warm-up handling: return NULL if history is fewer than N sessions
        CASE WHEN sma_20_count >= 20 THEN ROUND(sma_20_raw, 2) ELSE NULL END AS sma_20,
        CASE WHEN sma_50_count >= 50 THEN ROUND(sma_50_raw, 2) ELSE NULL END AS sma_50,
        CASE WHEN sma_200_count >= 200 THEN ROUND(sma_200_raw, 2) ELSE NULL END AS sma_200,

        ROUND(high_52w, 2) AS high_52w,
        ROUND(low_52w, 2) AS low_52w,

        -- Volume Spike Flag (> 2.0x average of prior 20 sessions)
        CASE 
            WHEN avg_prior_20_volume IS NOT NULL AND avg_prior_20_volume > 0 
                 AND (volume / avg_prior_20_volume) > 2.0 
            THEN TRUE 
            ELSE FALSE 
        END AS is_volume_spike,

        ROUND(COALESCE(avg_prior_20_volume, 0), 0) AS avg_prior_20_volume

    FROM window_aggregates
)

SELECT * FROM final_technicals
