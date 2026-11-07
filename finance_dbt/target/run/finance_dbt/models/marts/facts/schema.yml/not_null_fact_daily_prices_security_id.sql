
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select security_id
from "curated"."main_marts"."fact_daily_prices"
where security_id is null



  
  
      
    ) dbt_internal_test