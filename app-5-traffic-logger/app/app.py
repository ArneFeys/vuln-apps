from flask import Flask, request, render_template
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Store requests in memory
requests_log = []
ip_counts = defaultdict(int)

@app.before_request
def log_request():
    """Log every incoming request"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.remote_addr or request.environ.get('REMOTE_ADDR', 'Unknown')
    
    request_data = {
        'timestamp': timestamp,
        'ip': ip_address,
        'method': request.method,
        'path': request.path,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referer': request.headers.get('Referer', 'None'),
        'query_string': request.query_string.decode('utf-8') if request.query_string else '',
    }
    
    requests_log.append(request_data)
    ip_counts[ip_address] += 1
    
    # Keep only last 1000 requests to avoid memory issues
    if len(requests_log) > 1000:
        requests_log.pop(0)
    
    print(f"[{timestamp}] {ip_address} - {request.method} {request.path}")

@app.route('/')
def index():
    """Main page with links to both views"""
    return render_template('index.html')

@app.route('/requests')
def all_requests():
    """Display all individual requests"""
    return render_template('requests.html', requests=reversed(requests_log), total=len(requests_log))

@app.route('/ips')
def unique_ips():
    """Display unique IPs and their request counts"""
    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
    return render_template('ips.html', ips=sorted_ips, total_unique=len(sorted_ips))

# Catch-all route to log any other requests
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    return f"Request logged: {request.method} /{path}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
