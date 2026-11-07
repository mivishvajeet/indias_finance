
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    calendar_date as unique_field,
    count(*) as n_records

from "curated"."main_marts"."dim_date"
where calendar_date is not null
group by calendar_date
having count(*) > 1



  
  
      
    ) dbt_internal_test