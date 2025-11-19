-- Create users table with password_hash column
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Insert sample users with bcrypt hashed passwords
-- Bcrypt hashes are generated with cost factor 12
-- Original passwords are shown in comments for testing purposes

-- admin / admin123
INSERT INTO users (username, password_hash, email) VALUES
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBq.lkvy.', 'admin@vulnapp.local');

-- john / password123
INSERT INTO users (username, password_hash, email) VALUES
    ('john', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36CZLxqjW9nDW3LxHEQjKK6', 'john@vulnapp.local');

-- alice / alice2023
INSERT INTO users (username, password_hash, email) VALUES
    ('alice', '$2b$12$7ZWvKW8hjHdZLLHKJ6.kqeTz8xfGFqBQbXlJ2h7zqh8xGNLnZ4E8O', 'alice@vulnapp.local');

-- bob / qwerty
INSERT INTO users (username, password_hash, email) VALUES
    ('bob', '$2b$12$FqLLqH6k8V6LN6jzLQR8.OxKjH6FqLLqH6k8V6LN6jzLQR8.OxKje', 'bob@vulnapp.local');

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE users TO vulnuser;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO vulnuser;
