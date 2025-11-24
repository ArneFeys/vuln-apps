-- Create users table with plain text password column
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Insert sample users with plain text passwords

-- admin / admin123
INSERT INTO users (username, password, email) VALUES
    ('admin', 'admin123', 'admin@vulnapp.local');

-- john / password123
INSERT INTO users (username, password, email) VALUES
    ('john', 'password123', 'john@vulnapp.local');

-- alice / alice2023
INSERT INTO users (username, password, email) VALUES
    ('alice', 'alice2023', 'alice@vulnapp.local');

-- bob / qwerty
INSERT INTO users (username, password, email) VALUES
    ('bob', 'qwerty', 'bob@vulnapp.local');

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE users TO vulnuser;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO vulnuser;
