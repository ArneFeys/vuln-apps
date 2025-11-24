# Vulnerable Web Application - SQL Injection Demo

⚠️ **WARNING: This application contains intentional security vulnerabilities for educational purposes only. DO NOT deploy this in a production environment!**

## Overview

This is a simple Flask web application with a PostgreSQL database that demonstrates a **SQL Injection vulnerability**. The application features a login form that improperly handles user input, making it vulnerable to SQL injection attacks.

## Vulnerability: SQL Injection

The application contains a classic SQL injection vulnerability in the login functionality. The vulnerable code directly concatenates user input into SQL queries without proper sanitization or parameterized queries.

### Vulnerable Code

```python
# In app.py - DO NOT USE IN PRODUCTION
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cur.execute(query)
```

### How to Exploit

You can bypass authentication by entering the following in the username field:
```
' OR '1'='1' --
```

This works because it transforms the SQL query to:
```sql
SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = ''
```

The `--` comments out the rest of the query, and `'1'='1'` is always true, bypassing authentication.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone or navigate to the repository**

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Open your browser and go to: http://localhost:5000

4. **Stop the application**
   ```bash
   docker-compose down
   ```

   To remove all data including the database:
   ```bash
   docker-compose down -v
   ```

## Testing the Application

### Legitimate Login

Use these valid credentials:
- **Username:** `admin`
- **Password:** `admin123`

Other valid users: `john/password123`, `alice/alice2023`, `bob/qwerty`

### SQL Injection Attack

Try these in the **username** field (password can be anything):

1. **Basic authentication bypass:**
   ```
   ' OR '1'='1' --
   ```

2. **Login as admin specifically:**
   ```
   admin' --
   ```

3. **Alternative bypass:**
   ```
   ' OR 1=1 --
   ```

## Application Structure

```
vuln-apps/
├── app/
│   ├── app.py              # Main Flask application (contains vulnerability)
│   ├── requirements.txt    # Python dependencies
│   └── templates/
│       ├── index.html      # Home page
│       ├── login.html      # Login form
│       └── dashboard.html  # Protected dashboard
├── Dockerfile              # Container definition for Flask app
├── docker-compose.yml      # Orchestrates web app and database
├── init.sql               # Database initialization with sample data
└── README.md              # This file
```

## Security Issues in This Application

1. **SQL Injection** - Main vulnerability, allows authentication bypass
2. **Plain text passwords** - Passwords stored without hashing
3. **Weak secret key** - Session secret key is hardcoded
4. **Debug mode enabled** - Flask debug mode reveals sensitive information
5. **No input validation** - User input not sanitized or validated
6. **Error message disclosure** - Detailed error messages reveal database structure

## How to Fix

To make this application secure, you should:

1. **Use parameterized queries:**
   ```python
   cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
   ```

2. **Hash passwords:**
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   ```

3. **Use environment variables for secrets**
4. **Disable debug mode in production**
5. **Implement input validation and sanitization**
6. **Use proper error handling**
7. **Implement rate limiting and account lockout**
8. **Use HTTPS in production**

## Educational Purpose

This application is designed for:
- Security training and education
- Penetration testing practice
- Understanding common web vulnerabilities
- Learning secure coding practices by seeing what NOT to do

## License

This project is for educational purposes only. Use at your own risk.