# Vulnerable Web Application - SQL Injection Demo

⚠️ **WARNING: This application contains intentional security vulnerabilities for educational purposes only. DO NOT deploy this in a production environment!**

## Overview

This is a simple Flask web application with a PostgreSQL database that demonstrates a **SQL Injection vulnerability**. The application features a login form that improperly handles user input, making it vulnerable to SQL injection attacks.

**Two versions are available:**

- **`main` branch** - Vulnerable version with SQL injection and other security issues
- **`fix-sql-injection` branch** - Secured version with all vulnerabilities fixed ✅

## Branches

### Main Branch (Vulnerable)

The `main` branch contains the vulnerable application for educational purposes.

### Fix-SQL-Injection Branch (Secure)

The `fix-sql-injection` branch contains a fully secured version with the following fixes implemented:

✅ **SQL Injection Fixed** - Uses parameterized queries with prepared statements  
✅ **Password Hashing** - Implements bcrypt for secure password storage  
✅ **Input Validation** - Validates and sanitizes all user inputs  
✅ **Rate Limiting** - Prevents brute force attacks (10 login attempts per minute)  
✅ **Secure Secret Keys** - Uses environment variables and random generation  
✅ **Generic Error Messages** - Prevents user enumeration and information disclosure  
✅ **Debug Mode Control** - Configurable via environment variable

**To use the secure version:**

```bash
git checkout fix-sql-injection
docker-compose down -v  # Clear old database
docker-compose up --build
```

## Vulnerability: SQL Injection (Main Branch)

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

   - Open your browser and go to: http://vuln.feys-it.com:8002

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

### SQL Injection Attack (Main Branch Only)

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

4. **Time-based SQL injection:**
   ```
   Password field: x'; SELECT pg_sleep(5); --
   ```

## Application Structure

```
vuln-apps/
├── app/
│   ├── app.py              # Main Flask application
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

## Security Issues in Main Branch

1. **SQL Injection** - Main vulnerability, allows authentication bypass
2. **Plain text passwords** - Passwords stored without hashing
3. **Weak secret key** - Session secret key is hardcoded
4. **Debug mode enabled** - Flask debug mode reveals sensitive information
5. **No input validation** - User input not sanitized or validated
6. **Error message disclosure** - Detailed error messages reveal database structure
7. **No rate limiting** - Vulnerable to brute force attacks

## How It Was Fixed (Fix-SQL-Injection Branch)

### 1. SQL Injection Prevention

**Before (Vulnerable):**

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cur.execute(query)
```

**After (Secure):**

```python
cur.execute(
    "SELECT id, username, password_hash FROM users WHERE username = %s",
    (username,)
)
```

### 2. Password Hashing

**Before (Vulnerable):**

```sql
INSERT INTO users (username, password, email) VALUES ('admin', 'admin123', 'admin@vulnapp.local');
```

**After (Secure):**

```python
import bcrypt

# Storing passwords
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))

# Verifying passwords
if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    # Login successful
```

### 3. Input Validation

```python
def validate_username(username):
    """Validate username format - alphanumeric and underscore only, 3-50 chars"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
```

### 4. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app=app, key_func=get_remote_address)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    # ...
```

### 5. Secure Configuration

```python
# Use environment variable for secret key
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# Configurable debug mode
debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.run(host='0.0.0.0', port=5000, debug=debug_mode)
```

### 6. Generic Error Messages

```python
# Don't expose whether username exists or password is wrong
if not user or not password_matches:
    error = 'Invalid credentials'  # Generic message
```

## Comparison: Vulnerable vs Secure

| Feature          | Main Branch             | Fix-SQL-Injection Branch |
| ---------------- | ----------------------- | ------------------------ |
| SQL Queries      | String concatenation ❌ | Parameterized queries ✅ |
| Passwords        | Plain text ❌           | Bcrypt hashed ✅         |
| Input Validation | None ❌                 | Regex validation ✅      |
| Rate Limiting    | None ❌                 | 10/min on login ✅       |
| Secret Keys      | Hardcoded ❌            | Environment/random ✅    |
| Error Messages   | Detailed ❌             | Generic ✅               |
| Debug Mode       | Always on ❌            | Configurable ✅          |

## Educational Purpose

This application is designed for:

- Security training and education
- Penetration testing practice
- Understanding common web vulnerabilities
- Learning secure coding practices by comparing vulnerable and secure code
- Demonstrating the impact of SQL injection attacks

## Recommendations for Production

When building production applications:

1. **Always use parameterized queries or ORMs** (SQLAlchemy, Django ORM, etc.)
2. **Never store passwords in plain text** - use bcrypt, argon2, or PBKDF2
3. **Implement comprehensive input validation** on both client and server side
4. **Use rate limiting** to prevent brute force and DoS attacks
5. **Keep secrets in environment variables** or secret management systems
6. **Disable debug mode** in production environments
7. **Implement proper logging and monitoring** for security events
8. **Use HTTPS** for all production deployments
9. **Keep dependencies updated** and scan for vulnerabilities
10. **Follow OWASP Top 10** security guidelines

## License

This project is for educational purposes only. Use at your own risk.
