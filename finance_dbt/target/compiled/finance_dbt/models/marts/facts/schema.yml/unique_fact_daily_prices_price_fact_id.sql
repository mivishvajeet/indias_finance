
    
    

select
    price_fact_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."fact_daily_prices"
where price_fact_id is not null
group by price_fact_id
having count(*) > 1


