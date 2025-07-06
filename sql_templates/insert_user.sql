insert into {{ table_name }} (username, email, status)
values
{% for user in users %}
('{{ user.username }}', '{{ user.email }}', '{{ user.status }}')
{%- if not loop.last -%},{%- endif -%}
{% endfor %};
