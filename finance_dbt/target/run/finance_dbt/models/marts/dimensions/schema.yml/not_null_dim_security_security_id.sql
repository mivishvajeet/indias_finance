
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select security_id
from "curated"."main_marts"."dim_security"
where security_id is null



  
  
      
    ) dbt_internal_test