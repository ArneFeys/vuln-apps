from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Plaintext credentials stored directly in the code
API_CREDENTIALS = {
    "admin": "admin123",
    "user": "password123",
    "service": "secretKey2024"
}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username not in API_CREDENTIALS or API_CREDENTIALS[auth.username] != auth.password:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return jsonify({
        "message": "API Credentials Service",
        "endpoints": [
            "/api/status",
            "/api/data",
            "/api/config"
        ]
    })

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "version": "1.0.0"})

@app.route('/api/data')
@require_auth
def get_data():
    return jsonify({
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    })

@app.route('/api/config')
@require_auth
def get_config():
    username = request.authorization.username
    return jsonify({
        "user": username,
        "permissions": ["read", "write"] if username == "admin" else ["read"],
        "database": "postgresql://db:5432/appdb",
        "api_key": "sk_live_1234567890abcdef"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

