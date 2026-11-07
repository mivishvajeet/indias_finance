
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select macro_indicator_id
from "curated"."main_staging"."stg_macro"
where macro_indicator_id is null



  
  
      
    ) dbt_internal_test