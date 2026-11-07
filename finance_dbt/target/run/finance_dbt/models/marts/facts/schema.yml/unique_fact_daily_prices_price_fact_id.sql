
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    price_fact_id as unique_field,
    count(*) as n_records

from "curated"."main_marts"."fact_daily_prices"
where price_fact_id is not null
group by price_fact_id
having count(*) > 1



  
  
      
    ) dbt_internal_test