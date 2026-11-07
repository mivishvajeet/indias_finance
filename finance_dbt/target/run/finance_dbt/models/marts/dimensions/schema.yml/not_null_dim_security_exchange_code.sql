
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select exchange_code
from "curated"."main_marts"."dim_security"
where exchange_code is null



  
  
      
    ) dbt_internal_test