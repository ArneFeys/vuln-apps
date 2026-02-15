# Broker Localhost Test Application

Simple test application for validating broker URL rewriting with absolute localhost URLs.

## Purpose

Tests if the broker correctly handles absolute testbroker.pentest URLs:
- `http://testbroker.pentest:5001/path` links
- Redirects with absolute testbroker.pentest URLs
- POST requests to absolute testbroker.pentest URLs
- Form submissions to absolute testbroker.pentest URLs

## Setup

```bash
cd app-broker-test
docker-compose up
```

Access at `http://testbroker.pentest:5001`

## Testing with Proxy

1. Configure mitm-proxy with scope that has `broker_enabled: true`
2. Set `broker_url` to your broker instance
3. Point your browser through the proxy
4. Visit `http://testbroker.pentest:5001`
5. Click through the test links and forms
6. Monitor proxy logs to verify testbroker.pentest URLs are correctly rewritten

## Test Routes

- `/` - Main test page with absolute localhost links
- `/page1` - Simple page with navigation
- `/page2` - Simple page with navigation
- `/api/data` - GET/POST endpoint
- `/redirect-relative` - Redirects to `/page1`
- `/redirect-absolute` - Redirects to `http://testbroker.pentest:5001/page2`
- `/form-submit` - POST form handler
