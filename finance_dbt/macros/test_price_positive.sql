{% test price_positive(model, column_name) %}

-- Returns records where price is non-positive or null
SELECT 
    *
FROM {{ model }}
WHERE {{ column_name }} <= 0 OR {{ column_name }} IS NULL

{% endtest %}
