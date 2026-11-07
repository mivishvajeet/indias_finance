
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select indian_fiscal_year
from "curated"."main_marts"."dim_date"
where indian_fiscal_year is null



  
  
      
    ) dbt_internal_test