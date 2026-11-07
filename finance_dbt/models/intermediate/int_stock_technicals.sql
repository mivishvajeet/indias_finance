{{ config(materialized='view') }}

WITH daily_returns AS (
    SELECT * FROM {{ ref('int_stock_daily_returns') }}
),

price_deltas AS (
    SELECT
        *,
        -- Price change relative to previous session
        CASE 
            WHEN prev_close_price IS NOT NULL 
            THEN close_price - prev_close_price 
            ELSE 0.0 
        END AS price_change,
        -- Positive Gain
        CASE 
            WHEN prev_close_price IS NOT NULL AND close_price > prev_close_price 
            THEN close_price - prev_close_price 
            ELSE 0.0 
        END AS price_gain,
        -- Negative Loss (absolute magnitude)
        CASE 
            WHEN prev_close_price IS NOT NULL AND close_price < prev_close_price 
            THEN prev_close_price - close_price 
            ELSE 0.0 
        END AS price_loss
    FROM daily_returns
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
        -- 1. Simple Moving Averages (SMA 20, 50, 200)
        -- -------------------------------------------------------------
        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS sma_20_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS sma_20_raw,

        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS sma_50_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS sma_50_raw,

        COUNT(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS sma_200_count,
        AVG(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS sma_200_raw,

        -- -------------------------------------------------------------
        -- 2. 52-Week High & Low (252 Trading Days)
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
        -- 3. Volume Spike Detection
        -- -------------------------------------------------------------
        AVG(volume) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
        ) AS avg_prior_20_volume,

        -- -------------------------------------------------------------
        -- 4. Bollinger Bands (20-Day Standard Deviation)
        -- -------------------------------------------------------------
        STDDEV_SAMP(close_price) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS stddev_20_raw,

        -- -------------------------------------------------------------
        -- 5. RSI 14 (14-Session Average Gain and Loss)
        -- -------------------------------------------------------------
        COUNT(price_gain) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) AS rsi_14_count,
        AVG(price_gain) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) AS avg_gain_14,
        AVG(price_loss) OVER (
            PARTITION BY symbol ORDER BY trade_date ASC 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) AS avg_loss_14

    FROM price_deltas
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

        -- Warm-up handling: return NULL if history < N sessions
        CASE WHEN sma_20_count >= 20 THEN ROUND(sma_20_raw, 2) ELSE NULL END AS sma_20,
        CASE WHEN sma_50_count >= 50 THEN ROUND(sma_50_raw, 2) ELSE NULL END AS sma_50,
        CASE WHEN sma_200_count >= 200 THEN ROUND(sma_200_raw, 2) ELSE NULL END AS sma_200,

        ROUND(high_52w, 2) AS high_52w,
        ROUND(low_52w, 2) AS low_52w,

        -- Volume Spike Flag
        CASE 
            WHEN avg_prior_20_volume IS NOT NULL AND avg_prior_20_volume > 0 
                 AND (volume / avg_prior_20_volume) > 2.0 
            THEN TRUE 
            ELSE FALSE 
        END AS is_volume_spike,
        ROUND(COALESCE(avg_prior_20_volume, 0), 0) AS avg_prior_20_volume,

        -- Bollinger Bands
        CASE WHEN sma_20_count >= 20 THEN ROUND(sma_20_raw, 2) ELSE NULL END AS bollinger_middle,
        CASE 
            WHEN sma_20_count >= 20 AND stddev_20_raw IS NOT NULL 
            THEN ROUND(sma_20_raw + (2.0 * stddev_20_raw), 2) 
            ELSE NULL 
        END AS bollinger_upper,
        CASE 
            WHEN sma_20_count >= 20 AND stddev_20_raw IS NOT NULL 
            THEN ROUND(sma_20_raw - (2.0 * stddev_20_raw), 2) 
            ELSE NULL 
        END AS bollinger_lower,
        CASE 
            WHEN sma_20_count >= 20 AND stddev_20_raw IS NOT NULL AND sma_20_raw > 0
            THEN ROUND((4.0 * stddev_20_raw) / sma_20_raw, 4)
            ELSE NULL 
        END AS bollinger_bandwidth,

        -- RSI 14 Formula: 100 - (100 / (1 + (avg_gain / avg_loss)))
        CASE 
            WHEN rsi_14_count < 14 THEN NULL
            WHEN avg_loss_14 = 0 AND avg_gain_14 > 0 THEN 100.0
            WHEN avg_gain_14 = 0 THEN 0.0
            ELSE ROUND(100.0 - (100.0 / (1.0 + (avg_gain_14 / avg_loss_14))), 2)
        END AS rsi_14

    FROM window_aggregates
)

SELECT * FROM final_technicals
