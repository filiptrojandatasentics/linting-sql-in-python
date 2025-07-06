UPDATE {{ table_name }}
                SET 
                    status = '{{ new_status }}',
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id IN (
                    {% for user_id in user_ids %}
                        {{ user_id }}
                        {%- if not loop.last -%},{%- endif -%}
                    {% endfor %}
                );