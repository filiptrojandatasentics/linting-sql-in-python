# linting-sql-in-python
I do have a Python code which creates SQL queries (both DDL and DML) using f-strings. I want to lint those SQL queries using something like sqlfluff. How to make this work?

Result of https://claude.ai/share/50cd4e81-05a0-48cb-9ed7-9e5cd435086d.

# Demo

Run
```shell
uv run sqlfluff lint --templater jinja sql_templates/
```
On `main` branch to see all the linting issues.

Run the same on the `fix_sql` branch to demo all the issues resolved for postgres.

Run the same on the `fix_bigquery` branch to demo that no changes are needed for bigquery.

Run
```shell
uv run sqlfluff lint dataform/
```
on `fix_bigquery` and then on `fix_dataform` to demo the change.