#!/bin/bash
# Generate self-signed SSL certificate for Desktop Casting Receiver

echo "========================================"
echo "SSL Certificate Generator"
echo "========================================"
echo ""

# Detect local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo "Your local IP: $LOCAL_IP"
echo ""

# Ask where to save certificates
echo "Where would you like to save the certificates?"
echo "1) Current directory (for development)"
echo "2) dist/DesktopCastingReceiver (for built executable)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        CERT_PATH="./cert.pem"
        KEY_PATH="./key.pem"
        ;;
    2)
        if [ ! -d "./dist/DesktopCastingReceiver" ]; then
            echo ""
            echo "ERROR: ./dist/DesktopCastingReceiver directory not found!"
            echo "Please build the executable first using: ./build.sh"
            echo ""
            exit 1
        fi
        CERT_PATH="./dist/DesktopCastingReceiver/cert.pem"
        KEY_PATH="./dist/DesktopCastingReceiver/key.pem"
        ;;
    *)
        echo "Invalid choice. Defaulting to current directory."
        CERT_PATH="./cert.pem"
        KEY_PATH="./key.pem"
        ;;
esac

echo ""
echo "Generating SSL certificates..."

openssl req -x509 -newkey rsa:2048 -nodes \
  -out "$CERT_PATH" \
  -keyout "$KEY_PATH" \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Desktop Casting/CN=$LOCAL_IP" \
  -addext "subjectAltName=IP:$LOCAL_IP,DNS:localhost" \
  2>/dev/null

if [ -f "$CERT_PATH" ] && [ -f "$KEY_PATH" ]; then
    echo ""
    echo "========================================"
    echo "✓ Certificates Generated Successfully!"
    echo "========================================"
    echo ""
    echo "Files created:"
    echo "  $CERT_PATH - SSL certificate"
    echo "  $KEY_PATH  - Private key"
    echo ""
    echo "Certificate details:"
    echo "  IP Address: $LOCAL_IP"
    echo "  Valid for: 365 days"
    echo ""
    echo "IMPORTANT: Browsers will show a security warning!"
    echo "To connect:"
    echo "  1. Visit https://$LOCAL_IP:8080"
    echo "  2. Click 'Advanced' or 'Show details'"
    echo "  3. Click 'Proceed to $LOCAL_IP' or 'Accept the risk'"
    echo ""
    echo "The server will now use HTTPS instead of HTTP"
else
    echo ""
    echo "ERROR: Failed to generate certificates"
    echo "Check if OpenSSL is properly installed"
    exit 1
fi
