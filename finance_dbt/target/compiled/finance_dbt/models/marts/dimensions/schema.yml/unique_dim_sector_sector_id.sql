
    
    

select
    sector_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_sector"
where sector_id is not null
group by sector_id
having count(*) > 1


