from flask import Flask, request, render_template, send_file
from datetime import datetime
from collections import defaultdict
import os
import glob

app = Flask(__name__)

# Store requests in memory
requests_log = []
ip_counts = defaultdict(int)

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
    }
    
    requests_log.append(request_data)
    ip_counts[ip_address] += 1
    
    # Keep only last 1000 requests to avoid memory issues
    if len(requests_log) > 1000:
        requests_log.pop(0)
    
    print(f"[{timestamp}] {ip_address} - {request.scheme.upper()} {request.method} {request.path}")

@app.route('/')
def index():
    """Main page with links to all views"""
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

@app.route('/pcap')
def pcap_files():
    """Display and allow download of pcap files"""
    pcap_dir = '/captures'
    pcap_files = []
    
    if os.path.exists(pcap_dir):
        files = glob.glob(os.path.join(pcap_dir, '*.pcap'))
        for f in sorted(files, key=os.path.getmtime, reverse=True):
            stat = os.stat(f)
            pcap_files.append({
                'name': os.path.basename(f),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return render_template('pcap.html', pcap_files=pcap_files)

@app.route('/download/<filename>')
def download_pcap(filename):
    """Download a pcap file"""
    pcap_path = os.path.join('/captures', filename)
    if os.path.exists(pcap_path) and filename.endswith('.pcap'):
        return send_file(pcap_path, as_attachment=True)
    return "File not found", 404

# Catch-all route to log any other requests
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    return f"Request logged: {request.method} /{path}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
