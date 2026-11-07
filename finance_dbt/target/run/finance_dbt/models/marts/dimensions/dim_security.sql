
    

    create  table
      "curated"."main_marts"."dim_security__dbt_tmp"
  
    
    as (
      

WITH raw_securities AS (
    SELECT * FROM "curated"."main"."nse_securities"
),

formatted AS (
    SELECT
        -- Primary Surrogate Key
        MD5(UPPER(TRIM(symbol))) AS security_id,
        UPPER(TRIM(symbol)) AS symbol,
        TRIM(name) AS company_name,
        UPPER(TRIM(isin)) AS isin,
        TRIM(sector) AS sector_name,
        TRIM(industry) AS industry_name,
        UPPER(TRIM(security_type)) AS security_type,
        'INR' AS currency_code,
        'NSE' AS exchange_code
    FROM raw_securities
)

SELECT * FROM formatted
    );
    
  