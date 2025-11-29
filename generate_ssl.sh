#!/bin/bash
# All-in-one script to generate SSL certificates and set up the executable

echo "========================================"
echo "SSL Setup for Desktop Casting Receiver"
echo "========================================"
echo ""

# Step 1: Check if executable exists
EXE_PATH="./dist/DesktopCastingReceiver/DesktopCastingReceiver"
if [ ! -f "$EXE_PATH" ]; then
    echo "ERROR: Executable not found at:"
    echo "  $EXE_PATH"
    echo ""
    echo "Please build the executable first:"
    echo "  ./build.sh"
    echo ""
    exit 1
fi

echo "✓ Executable found!"
echo ""

# Step 2: Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo "ERROR: OpenSSL not found!"
    echo ""
    echo "Please install OpenSSL:"
    echo "  Ubuntu/Debian: sudo apt-get install openssl"
    echo "  Fedora/RHEL:   sudo dnf install openssl"
    echo "  Arch:          sudo pacman -S openssl"
    echo ""
    exit 1
fi

echo "✓ OpenSSL found"
echo ""

# Step 3: Get local IP
echo "Detecting local IP address..."
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
    echo "⚠ Could not detect local IP, using localhost"
else
    echo "✓ Local IP: $LOCAL_IP"
fi
echo ""

# Step 4: Generate certificates
echo "Generating SSL certificates..."
echo ""

# Generate certificates directly in dist folder
openssl req -x509 -newkey rsa:2048 -nodes \
    -out ./dist/DesktopCastingReceiver/cert.pem \
    -keyout ./dist/DesktopCastingReceiver/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Desktop Casting/CN=$LOCAL_IP" \
    -addext "subjectAltName=IP:$LOCAL_IP,DNS:localhost" \
    2>/dev/null

if [ -f "./dist/DesktopCastingReceiver/cert.pem" ] && [ -f "./dist/DesktopCastingReceiver/key.pem" ]; then
    echo ""
    echo "========================================"
    echo "✓ Setup Complete!"
    echo "========================================"
    echo ""
    echo "SSL certificates created and placed in:"
    echo "  ./dist/DesktopCastingReceiver/cert.pem"
    echo "  ./dist/DesktopCastingReceiver/key.pem"
    echo ""
    echo "Your local IP: $LOCAL_IP"
    echo ""
    echo "To run the application:"
    echo "  cd ./dist/DesktopCastingReceiver"
    echo "  ./DesktopCastingReceiver"
    echo ""
    echo "Devices can connect via:"
    echo "  https://$LOCAL_IP:8080"
    echo ""
    echo "IMPORTANT:"
    echo "  When you first visit the URL, you'll see a security warning."
    echo "  Click 'Advanced' then 'Proceed to $LOCAL_IP' to continue."
    echo ""

    read -p "Would you like to start the application now? (y/N) " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Starting Desktop Casting Receiver..."
        echo ""
        cd ./dist/DesktopCastingReceiver
        ./DesktopCastingReceiver
    fi
else
    echo ""
    echo "========================================"
    echo "ERROR: Failed to generate certificates"
    echo "========================================"
    echo ""
    echo "Please check that:"
    echo "  - OpenSSL is properly installed"
    echo "  - You have write permissions to ./dist/DesktopCastingReceiver/"
    echo ""
    exit 1
fi
