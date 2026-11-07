
    
    

select
    sector_name as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_sector"
where sector_name is not null
group by sector_name
having count(*) > 1


