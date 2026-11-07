
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    macro_indicator_id as unique_field,
    count(*) as n_records

from "curated"."main_staging"."stg_macro"
where macro_indicator_id is not null
group by macro_indicator_id
having count(*) > 1



  
  
      
    ) dbt_internal_test