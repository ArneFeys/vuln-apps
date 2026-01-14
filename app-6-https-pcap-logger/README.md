# HTTPS Traffic Logger with PCAP Capture

A Flask application that logs all incoming HTTP/HTTPS traffic and captures network packets to PCAP files for analysis.

## Features

- HTTPS endpoint on port 443 with self-signed SSL certificate
- HTTP endpoint on port 80
- Logs all incoming requests (method, path, IP, timestamp, headers)
- Captures all network traffic to PCAP files using tcpdump
- View all individual requests with protocol information
- View unique IP addresses with request counts
- Download PCAP files for analysis in Wireshark

## Architecture

- **Nginx**: Reverse proxy handling HTTP (port 6080) and HTTPS (port 6443)
- **Flask**: Backend application for logging and serving pages
- **Packet Capture**: tcpdump container capturing all traffic to PCAP files

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

- HTTP: `http://localhost:6080`
- HTTPS: `https://localhost:6443` (accept self-signed certificate warning)

## Pages

### Home Page
Landing page with navigation to all views

### All Requests
`/requests` - Displays all individual requests showing:
- Timestamp
- Protocol (HTTP/HTTPS)
- IP address
- HTTP method
- Request path
- User agent

### Unique IPs
`/ips` - Displays unique IP addresses sorted by request count

### PCAP Files
`/pcap` - List and download captured PCAP files for analysis

## PCAP Analysis

Download PCAP files and analyze with:

```bash
# View with tcpdump
tcpdump -r traffic-20260114-120000.pcap

# Analyze with tshark
tshark -r traffic-20260114-120000.pcap

# Open in Wireshark
wireshark traffic-20260114-120000.pcap
```

## Notes

- Self-signed certificate will show browser warnings (this is expected)
- PCAP files are timestamped and stored in the `captures/` directory
- Requests are stored in memory (up to 1000 most recent)
- Packet capture runs continuously while services are up
- All HTTP methods are supported and logged
