
    
    

select
    symbol as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_security"
where symbol is not null
group by symbol
having count(*) > 1


