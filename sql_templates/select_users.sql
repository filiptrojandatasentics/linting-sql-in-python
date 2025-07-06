SELECT 
                    user_id,
                    username,
                    email,
                    created_at
                FROM users 
                WHERE status = '{{ status }}'
                {% if user_id %}
                    AND user_id = {{ user_id }}
                {% endif %}
                {% if limit %}
                    LIMIT {{ limit }}
                {% endif %}