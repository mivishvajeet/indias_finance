
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select volume
from "curated"."main_staging"."stg_stocks"
where volume is null



  
  
      
    ) dbt_internal_test