
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    macro_fact_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."fact_macro_indicators"
where macro_fact_id is not null
group by macro_fact_id
having count(*) > 1



  
  
      
    ) dbt_internal_test