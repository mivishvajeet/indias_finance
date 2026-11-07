
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select indicator_value
from "curated"."main_staging"."stg_macro"
where indicator_value is null



  
  
      
    ) dbt_internal_test