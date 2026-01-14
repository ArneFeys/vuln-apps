# HTTPS Traffic Logger

A Flask application that logs all incoming HTTP/HTTPS traffic with powerful filtering and analysis capabilities.

## Features

- HTTPS endpoint on port 443 with self-signed SSL certificate
- HTTP endpoint on port 8080
- **Python-based request logging** (unlimited, persisted to disk as JSONL)
- **Filter requests** by IP, User-Agent, Method, and Path
- View all individual requests with protocol information
- View unique IP addresses with request counts (click to filter)
- Real client IP addresses logged from nginx proxy headers

## Architecture

- **Nginx**: Reverse proxy handling HTTP (port 8080) and HTTPS (port 443)
- **Flask**: Backend application for logging and serving pages
- **JSONL Storage**: All requests persisted to `/captures/requests.jsonl` for unlimited history

## Setup

### 1. Generate SSL Certificates

First, generate the self-signed SSL certificates:

```bash
cd app-6-https-pcap-logger
chmod +x generate-certs.sh
./generate-certs.sh
```

This creates:
- `certs/server.crt` - SSL certificate
- `certs/server.key` - Private key

### 2. Create Captures Directory

```bash
mkdir -p captures
```

### 3. Start Services

```bash
docker-compose up --build
```

## Access

- HTTP: `http://localhost:8080`
- HTTPS: `https://localhost:443`

Note: Accept self-signed certificate warning in browser

## Pages

### Home Page
Landing page with navigation to all views

### All Requests
`/requests` - Displays all individual requests with powerful filters:
- Filter by IP address (partial match)
- Filter by User-Agent (partial match)
- Filter by HTTP method (GET, POST, etc.)
- Filter by path (partial match)
- Shows: Timestamp, Protocol (HTTP/HTTPS), IP, Method, Path, User-Agent

### Unique IPs
`/ips` - Displays unique IP addresses sorted by request count
- Click "View Requests" to filter all requests from that IP

## Request Log Storage

All requests are stored in `/captures/requests.jsonl`:
- JSONL format (one JSON object per line)
- Unlimited storage (no artificial limits)
- Persisted across container restarts
- Can be analyzed with standard tools

```bash
# View raw log file
tail -f captures/requests.jsonl

# Count requests by IP
cat captures/requests.jsonl | jq -r '.ip' | sort | uniq -c | sort -rn

# Find requests with specific user agent
cat captures/requests.jsonl | jq 'select(.user_agent | contains("bot"))'
```

## Notes

- Self-signed certificate will show browser warnings (this is expected)
- All requests are logged to `captures/requests.jsonl` with no limit
- Logs persist across container restarts
- Real client IP addresses are captured from nginx proxy headers
- All HTTP methods are supported and logged
- Filters support partial/case-insensitive matching