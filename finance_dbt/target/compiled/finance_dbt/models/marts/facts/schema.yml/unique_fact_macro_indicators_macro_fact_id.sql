
    
    

select
    macro_fact_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."fact_macro_indicators"
where macro_fact_id is not null
group by macro_fact_id
having count(*) > 1


