{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw_staging', 'stg_mf_nav') }}
),
renamed as (
    select
        md5(scheme_code || '_' || cast(nav_date as varchar)) as nav_price_id,
        cast(scheme_code as varchar) as scheme_code,
        trim(scheme_name) as scheme_name,
        cast(nav_date as date) as nav_date,
        cast(nav as double) as nav,
        trim(fund_family) as fund_family,
        trim(scheme_category) as scheme_category,
        trim(source) as source,
        cast(ingested_at as timestamp) as ingested_at
    from source
    where nav > 0
)
select * from renamed
