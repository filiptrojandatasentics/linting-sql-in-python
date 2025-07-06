select
    user_id
    , username
    , email
    , created_at
from users
where
    status = '{{ status }}'
    {% if user_id %} and user_id = {{ user_id }}
{% endif %}
{% if limit %}
limit {{ limit }}
{% endif %}
