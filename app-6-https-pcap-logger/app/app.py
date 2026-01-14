from flask import Flask, request, render_template
from datetime import datetime
from collections import defaultdict
import os
import json

app = Flask(__name__)

# Store requests in memory (no limit)
requests_log = []
ip_counts = defaultdict(int)

# Log file path
LOG_FILE = '/captures/requests.jsonl'

def save_request_to_file(request_data):
    """Save request to JSONL file"""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(request_data) + '\n')
    except Exception as e:
        print(f"Error saving to file: {e}")

def load_requests_from_file():
    """Load requests from JSONL file"""
    global requests_log, ip_counts
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        req = json.loads(line)
                        requests_log.append(req)
                        ip_counts[req['ip']] += 1
        except Exception as e:
            print(f"Error loading from file: {e}")

# Load existing requests on startup
load_requests_from_file()

@app.before_request
def log_request():
    """Log every incoming request"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Get real IP from nginx proxy headers
    ip_address = request.headers.get('X-Real-IP') or \
                 request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or \
                 request.remote_addr or \
                 request.environ.get('REMOTE_ADDR', 'Unknown')
    
    request_data = {
        'timestamp': timestamp,
        'ip': ip_address,
        'method': request.method,
        'path': request.path,
        'scheme': request.scheme,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referer': request.headers.get('Referer', 'None'),
        'query_string': request.query_string.decode('utf-8') if request.query_string else '',
        'content_length': request.headers.get('Content-Length', '0'),
    }
    
    requests_log.append(request_data)
    ip_counts[ip_address] += 1
    save_request_to_file(request_data)
    
    print(f"[{timestamp}] {ip_address} - {request.scheme.upper()} {request.method} {request.path}")

@app.route('/')
def index():
    """Main page with links to all views"""
    return render_template('index.html')

@app.route('/requests')
def all_requests():
    """Display all individual requests with filters"""
    # Get filter parameters
    filter_ip = request.args.get('ip', '').strip()
    filter_ua = request.args.get('ua', '').strip().lower()
    filter_method = request.args.get('method', '').strip().upper()
    filter_path = request.args.get('path', '').strip().lower()
    
    # Filter requests
    filtered = requests_log
    if filter_ip:
        filtered = [r for r in filtered if filter_ip in r['ip']]
    if filter_ua:
        filtered = [r for r in filtered if filter_ua in r['user_agent'].lower()]
    if filter_method:
        filtered = [r for r in filtered if r['method'] == filter_method]
    if filter_path:
        filtered = [r for r in filtered if filter_path in r['path'].lower()]
    
    return render_template('requests.html', 
                         requests=reversed(filtered), 
                         total=len(requests_log),
                         filtered_count=len(filtered),
                         filter_ip=filter_ip,
                         filter_ua=filter_ua,
                         filter_method=filter_method,
                         filter_path=filter_path)

@app.route('/ips')
def unique_ips():
    """Display unique IPs and their request counts"""
    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
    return render_template('ips.html', ips=sorted_ips, total_unique=len(sorted_ips))

# Catch-all route to log any other requests (must be last)
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    return f"Request logged: {request.method} /{path}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
