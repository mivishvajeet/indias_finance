{% test high_gte_low(model, high_column='high_price', low_column='low_price') %}

-- Returns records where High is strictly less than Low (sanity violation)
SELECT 
    *
FROM {{ model }}
WHERE {{ high_column }} < {{ low_column }}

{% endtest %}
