CREATE TABLE IF NOT EXISTS {{ table_name }} (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR({{ username_length }}) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );