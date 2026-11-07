
    
    

select
    security_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_security"
where security_id is not null
group by security_id
having count(*) > 1


