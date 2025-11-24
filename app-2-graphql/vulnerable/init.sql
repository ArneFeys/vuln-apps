-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    salary DECIMAL(10, 2),
    ssn VARCHAR(11),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_published BOOLEAN DEFAULT false,
    is_private BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    to_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email, password, role, salary, ssn) VALUES
    ('admin', 'admin@example.com', 'admin123', 'admin', 150000.00, '123-45-6789'),
    ('alice', 'alice@example.com', 'alice123', 'user', 75000.00, '234-56-7890'),
    ('bob', 'bob@example.com', 'bob123', 'user', 65000.00, '345-67-8901'),
    ('charlie', 'charlie@example.com', 'charlie123', 'moderator', 85000.00, '456-78-9012'),
    ('david', 'david@example.com', 'david123', 'user', 55000.00, '567-89-0123');

INSERT INTO posts (title, content, author_id, is_published, is_private) VALUES
    ('Welcome to GraphQL', 'This is a public post about GraphQL basics.', 1, true, false),
    ('Secret Admin Notes', 'These are confidential admin notes. Should not be public.', 1, false, true),
    ('Alice''s First Post', 'Hello world from Alice!', 2, true, false),
    ('Bob''s Private Thoughts', 'Private thoughts that should be hidden.', 3, false, true),
    ('GraphQL Security Tips', 'Some tips on securing GraphQL APIs.', 4, true, false);

INSERT INTO comments (content, post_id, author_id) VALUES
    ('Great post!', 1, 2),
    ('Very informative', 1, 3),
    ('Thanks for sharing', 3, 1),
    ('Interesting perspective', 5, 2);

INSERT INTO products (name, description, price, stock) VALUES
    ('GraphQL Book', 'Comprehensive guide to GraphQL', 49.99, 100),
    ('API Security Course', 'Learn API security best practices', 99.99, 50),
    ('Docker Fundamentals', 'Master Docker and containerization', 39.99, 75),
    ('Premium Support', 'One year of premium support', 299.99, 10),
    ('Consultation Hour', 'One hour consultation with experts', 150.00, 20);

INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
    (2, 1, 1, 49.99, 'completed'),
    (2, 3, 2, 79.98, 'pending'),
    (3, 2, 1, 99.99, 'completed'),
    (4, 4, 1, 299.99, 'pending'),
    (5, 5, 1, 150.00, 'completed');

INSERT INTO messages (from_user_id, to_user_id, content) VALUES
    (1, 2, 'Welcome to the platform, Alice!'),
    (2, 3, 'Hey Bob, want to collaborate on a project?'),
    (3, 2, 'Sure, that sounds great!'),
    (1, 4, 'Charlie, can you review the latest posts?'),
    (4, 1, 'Will do, checking them now.');

