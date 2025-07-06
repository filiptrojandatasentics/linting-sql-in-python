import os
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class SQLQueryBuilder:
    def __init__(self, templates_dir='sql_templates'):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment with file system loader
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create template files if they don't exist
        self._create_template_files()
    
    def _create_template_files(self):
        """Create SQL template files"""
        templates = {
            'select_users.sql': """
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
            """,
            
            'create_user_table.sql': """
                CREATE TABLE IF NOT EXISTS {{ table_name }} (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR({{ username_length }}) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            'insert_user.sql': """
                INSERT INTO {{ table_name }} (username, email, status)
                VALUES 
                {% for user in users %}
                    ('{{ user.username }}', '{{ user.email }}', '{{ user.status }}')
                    {%- if not loop.last -%},{%- endif -%}
                {% endfor %};
            """,
            
            'update_user_status.sql': """
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
            """,
            
            'complex_report.sql': """
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
            """
        }
        
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    f.write(content.strip())
                print(f"Created template: {template_path}")
    
    def list_templates(self):
        """List all available SQL templates"""
        templates = list(self.templates_dir.glob('*.sql'))
        return [t.stem for t in templates]
    
    def render_query(self, template_name, **kwargs):
        """Render a Jinja2 template with provided parameters"""
        template_file = f"{template_name}.sql"
        
        try:
            template = self.jinja_env.get_template(template_file)
            return template.render(**kwargs)
        except Exception as e:
            raise ValueError(f"Error rendering template '{template_name}': {str(e)}")
    
    def lint_template(self, template_name):
        """Lint a template file using sqlfluff with jinja templater"""
        template_path = self.templates_dir / f"{template_name}.sql"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found at {template_path}")
        
        # Run sqlfluff with jinja templater on the actual file
        result = subprocess.run([
            'sqlfluff', 'lint', 
            '--templater', 'jinja',
            '--dialect', 'postgres',  # Change to your dialect
            str(template_path)
        ], capture_output=True, text=True)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr,
            'template_path': str(template_path)
        }
    
    def lint_all_templates(self):
        """Lint all template files"""
        templates = self.list_templates()
        results = {}
        
        for template in templates:
            results[template] = self.lint_template(template)
        
        return results
    
    def format_template(self, template_name):
        """Format a template file using sqlfluff"""
        template_path = self.templates_dir / f"{template_name}.sql"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found at {template_path}")
        
        # Run sqlfluff format on the actual file
        result = subprocess.run([
            'sqlfluff', 'format', 
            '--templater', 'jinja',
            '--dialect', 'postgres',
            str(template_path)
        ], capture_output=True, text=True)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr,
            'template_path': str(template_path)
        }
    
    def create_sqlfluff_config(self):
        """Create a .sqlfluff configuration file"""
        config_content = """[sqlfluff]
templater = jinja
dialect = postgres
exclude_rules = L034

[sqlfluff:indentation]
tab_space_size = 4

[sqlfluff:templater:jinja]
apply_dbt_builtins = True

[sqlfluff:rules:L010]
capitalisation_policy = upper

[sqlfluff:rules:L030]
capitalisation_policy = upper
"""
        
        config_path = Path('.sqlfluff')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"Created sqlfluff config at {config_path}")
        return config_path

# Example usage and testing
if __name__ == "__main__":
    # Initialize the builder (this will create template files)
    builder = SQLQueryBuilder()
    
    # Create sqlfluff config
    builder.create_sqlfluff_config()
    
    # List available templates
    print("=== Available Templates ===")
    templates = builder.list_templates()
    for template in templates:
        print(f"- {template}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 1: Render and use a SELECT query
    print("=== SELECT Query Example ===")
    select_params = {
        'status': 'active',
        'user_id': 123,
        'limit': 10
    }
    
    sql = builder.render_query('select_users', **select_params)
    print("Rendered SQL:")
    print(sql)
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Render a complex report
    print("=== Complex Report Example ===")
    report_params = {
        'users_table': 'users',
        'orders_table': 'orders',
        'date_filter': '2024-01-01',
        'high_value_threshold': 1000,
        'medium_value_threshold': 500,
        'min_orders': 5,
        'limit': 50
    }
    
    sql = builder.render_query('complex_report', **report_params)
    print("Rendered SQL:")
    print(sql)
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Lint individual template
    print("=== Linting Individual Template ===")
    lint_result = builder.lint_template('select_users')
    print(f"Template: select_users")
    print(f"Lint Success: {lint_result['success']}")
    if lint_result['output']:
        print(f"Output:\n{lint_result['output']}")
    if lint_result['errors']:
        print(f"Errors:\n{lint_result['errors']}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Lint all templates
    print("=== Linting All Templates ===")
    all_results = builder.lint_all_templates()
    for template_name, result in all_results.items():
        print(f"Template: {template_name}")
        print(f"  Success: {result['success']}")
        if not result['success'] and result['errors']:
            print(f"  Errors: {result['errors']}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Batch insert example
    print("=== INSERT Query Example ===")
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'status': 'active'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'status': 'pending'},
        {'username': 'bob_wilson', 'email': 'bob@example.com', 'status': 'active'}
    ]
    
    insert_params = {
        'table_name': 'users',
        'users': users_data
    }
    
    sql = builder.render_query('insert_user', **insert_params)
    print("Rendered SQL:")
    print(sql)
    
    print("\n" + "="*50 + "\n")
    print("Template files created in 'sql_templates' directory")
    print("You can now run: sqlfluff lint sql_templates/")
