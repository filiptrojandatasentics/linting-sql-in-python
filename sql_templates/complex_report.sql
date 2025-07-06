with user_stats as (
    select
        u.user_id
        , u.username
        , u.status
        , count(o.order_id) as order_count
        , sum(o.total_amount) as total_spent
    from {{ users_table }} as u
    left join {{ orders_table }} as o on u.user_id = o.user_id
    {% if date_filter %}
    where o.created_at >= '{{ date_filter }}'
    {% endif %}
    group by u.user_id, u.username, u.status
)
select
    username
    , status
    , order_count
    , total_spent
    , case
        when total_spent > {{ high_value_threshold }} then 'High Value'
        when total_spent > {{ medium_value_threshold }} then 'Medium Value'
        else 'Low Value'
    end as customer_tier
from user_stats
{% if min_orders %}
where order_count >= {{ min_orders }}
{% endif %}
order by total_spent desc
{% if limit %}
limit {{ limit }}{% endif %};
