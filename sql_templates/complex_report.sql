WITH user_stats AS (
                    SELECT 
                        u.user_id,
                        u.username,
                        u.status,
                        COUNT(o.order_id) as order_count,
                        SUM(o.total_amount) as total_spent
                    FROM {{ users_table }} u
                    LEFT JOIN {{ orders_table }} o ON u.user_id = o.user_id
                    {% if date_filter %}
                    WHERE o.created_at >= '{{ date_filter }}'
                    {% endif %}
                    GROUP BY u.user_id, u.username, u.status
                )
                SELECT 
                    username,
                    status,
                    order_count,
                    total_spent,
                    CASE 
                        WHEN total_spent > {{ high_value_threshold }} THEN 'High Value'
                        WHEN total_spent > {{ medium_value_threshold }} THEN 'Medium Value'
                        ELSE 'Low Value'
                    END as customer_tier
                FROM user_stats
                {% if min_orders %}
                WHERE order_count >= {{ min_orders }}
                {% endif %}
                ORDER BY total_spent DESC
                {% if limit %}
                LIMIT {{ limit }}
                {% endif %};