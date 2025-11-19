from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-123'

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

@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in', False), username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABLE CODE: SQL Injection vulnerability
        # Never do this in production!
        conn = get_db_connection()
        cur = conn.cursor()
        
        # This query is vulnerable to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cur.execute(query)
            user = cur.fetchone()
            
            if user:
                session['logged_in'] = True
                session['username'] = user[1]  # username column
                cur.close()
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
        except Exception as e:
            error = f'Error: {str(e)}'
        finally:
            cur.close()
            conn.close()
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', username=session.get('username'), users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

