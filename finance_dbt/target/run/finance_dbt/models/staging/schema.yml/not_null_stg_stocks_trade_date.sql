
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select trade_date
from "curated"."main_staging"."stg_stocks"
where trade_date is null



  
  
      
    ) dbt_internal_test