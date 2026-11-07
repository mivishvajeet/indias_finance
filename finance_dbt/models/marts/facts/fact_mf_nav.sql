{{ config(materialized='table') }}

with stg as (
    select * from {{ ref('stg_mf_nav') }}
),
calculated as (
    select
        nav_price_id as nav_fact_id,
        md5(scheme_code) as fund_id,
        cast(strftime(nav_date, '%Y%m%d') as integer) as date_id,
        scheme_code,
        scheme_name,
        nav_date,
        nav,
        (nav - lag(nav, 1) over (partition by scheme_code order by nav_date)) /
            nullif(lag(nav, 1) over (partition by scheme_code order by nav_date), 0) as daily_return_pct,
        max(nav) over (partition by scheme_code order by nav_date rows between 251 preceding and current row) as nav_high_52w,
        min(nav) over (partition by scheme_code order by nav_date rows between 251 preceding and current row) as nav_low_52w
    from stg
)
select * from calculated
