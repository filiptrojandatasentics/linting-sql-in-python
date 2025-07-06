update {{ table_name }}
set
    status = '{{ new_status }}'
    , updated_at = current_timestamp
where user_id in (
    {% for user_id in user_ids %}
    {{ user_id }}
    {%- if not loop.last -%},{%- endif -%}
    {% endfor %}
);
