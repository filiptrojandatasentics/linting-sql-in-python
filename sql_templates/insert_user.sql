INSERT INTO {{ table_name }} (username, email, status)
                VALUES 
                {% for user in users %}
                    ('{{ user.username }}', '{{ user.email }}', '{{ user.status }}')
                    {%- if not loop.last -%},{%- endif -%}
                {% endfor %};