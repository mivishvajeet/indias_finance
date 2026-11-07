{{ config(materialized='table') }}

with distinct_funds as (
    select distinct
        md5(scheme_code) as fund_id,
        scheme_code,
        scheme_name,
        fund_family,
        scheme_category,
        source
    from {{ ref('stg_mf_nav') }}
)
select
    fund_id,
    scheme_code,
    scheme_name,
    fund_family,
    scheme_category,
    source,
    current_timestamp as created_at
from distinct_funds
