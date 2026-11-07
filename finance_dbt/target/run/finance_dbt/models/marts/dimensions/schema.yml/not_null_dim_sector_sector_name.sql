
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sector_name
from "curated"."main_marts"."dim_sector"
where sector_name is null



  
  
      
    ) dbt_internal_test