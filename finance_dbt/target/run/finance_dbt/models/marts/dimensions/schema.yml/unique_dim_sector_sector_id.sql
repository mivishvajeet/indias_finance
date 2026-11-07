
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sector_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_sector"
where sector_id is not null
group by sector_id
having count(*) > 1



  
  
      
    ) dbt_internal_test