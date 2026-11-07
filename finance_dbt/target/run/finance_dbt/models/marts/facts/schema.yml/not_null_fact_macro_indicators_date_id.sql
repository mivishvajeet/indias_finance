
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_id
from "curated"."main_marts"."fact_macro_indicators"
where date_id is null



  
  
      
    ) dbt_internal_test