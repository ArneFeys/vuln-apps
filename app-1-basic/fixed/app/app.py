from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
import os
import re

app = Flask(__name__)

# Use environment variable for secret key, with a secure random fallback
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'vulnapp')
DB_USER = os.environ.get('DB_USER', 'vulnuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'vulnpass')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def validate_username(username):
    """Validate username format - alphanumeric and underscore only, 3-50 chars"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

def validate_password(password):
    """Basic password validation - at least 6 characters"""
    if not password or len(password) < 6:
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in', False), username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not validate_username(username):
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
        
        if not validate_password(password):
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
        
        conn = None
        cur = None
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # SECURE: Use parameterized query to prevent SQL injection
            cur.execute(
                "SELECT id, username, password FROM users WHERE username = %s",
                (username,)
            )
            user = cur.fetchone()
            
            if user:
                user_id, db_username, stored_password = user
                
                # Simple plain text password comparison
                if password == stored_password:
                    session['logged_in'] = True
                    session['username'] = db_username
                    session['user_id'] = user_id
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid credentials'
            else:
                # Generic error message to prevent user enumeration
                error = 'Invalid credentials'
                
        except Exception as e:
            # Don't expose internal errors to users
            app.logger.error(f"Login error: {str(e)}")
            error = 'An error occurred. Please try again later.'
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = None
    cur = None
    users = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Only select necessary columns, not password hash
        cur.execute('SELECT id, username, email FROM users ORDER BY id')
        users = cur.fetchall()
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return render_template('dashboard.html', username=session.get('username'), users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Debug mode should be disabled in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
