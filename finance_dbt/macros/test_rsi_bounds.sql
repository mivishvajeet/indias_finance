{% test rsi_bounds(model, column_name='rsi_14') %}

-- Returns records where RSI is outside the theoretical bounds of [0, 100]
SELECT 
    *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL 
  AND ({{ column_name }} < 0.0 OR {{ column_name }} > 100.0)

{% endtest %}
