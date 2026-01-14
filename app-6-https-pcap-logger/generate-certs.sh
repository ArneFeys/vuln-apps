#!/bin/bash

# Create certs directory if it doesn't exist
mkdir -p certs

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/server.key \
    -out certs/server.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=localhost"

echo "SSL certificates generated in ./certs/"
echo "  - server.crt (certificate)"
echo "  - server.key (private key)"
