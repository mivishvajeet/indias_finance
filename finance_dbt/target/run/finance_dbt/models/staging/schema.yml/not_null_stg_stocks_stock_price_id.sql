
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stock_price_id
from "curated"."main_staging"."stg_stocks"
where stock_price_id is null



  
  
      
    ) dbt_internal_test