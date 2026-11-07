
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select symbol
from "curated"."main_staging"."stg_stocks"
where symbol is null



  
  
      
    ) dbt_internal_test