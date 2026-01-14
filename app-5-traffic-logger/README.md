# Traffic Logger

A simple Flask application that logs all incoming HTTP traffic and displays it on two separate pages.

## Features

- Logs all incoming HTTP requests (method, path, IP, timestamp, headers)
- View all individual requests with full details
- View unique IP addresses with request counts
- Real-time traffic monitoring
- Clean, modern UI

## Setup

Build and run with Docker:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5005`

## Pages

### Home Page
`http://localhost:5005/` - Landing page with navigation to both views

### All Requests
`http://localhost:5005/requests` - Displays all individual requests in reverse chronological order, showing:
- Timestamp
- IP address
- HTTP method
- Request path
- User agent
- Referer

### Unique IPs
`http://localhost:5005/ips` - Displays unique IP addresses sorted by request count, showing:
- IP address
- Number of requests from that IP

## Notes

- Requests are stored in memory (up to 1000 most recent)
- All requests are logged to console output
- Any path will be logged (including 404s)
- Supports all HTTP methods (GET, POST, PUT, DELETE, etc.)
