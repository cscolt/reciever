#!/bin/bash
# Generate self-signed SSL certificate for Desktop Casting Receiver

openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem \
  -keyout key.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "SSL certificates generated: cert.pem and key.pem"
echo "The server will now use HTTPS instead of HTTP"
