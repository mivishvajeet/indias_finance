
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select macro_fact_id
from "curated"."main_marts"."fact_macro_indicators"
where macro_fact_id is null



  
  
      
    ) dbt_internal_test