#!/bin/bash
# Linux Build Script for Desktop Casting Receiver v2.0
# Updated for new refactored structure

cd "$(dirname "$0")/../.." || exit 1

echo "===================================="
echo " Desktop Casting Receiver v2.0"
echo " Linux Build Script"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Build with PyInstaller
echo ""
echo "Building executable with PyInstaller..."
pyinstaller build/desktop_caster.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================="
    echo "✓ Build Successful!"
    echo "===================================="
    echo ""
    echo "Executable location:"
    echo "  ./dist/DesktopCastingReceiver/DesktopCastingReceiver"
    echo ""
    echo "To run:"
    echo "  cd dist/DesktopCastingReceiver"
    echo "  ./DesktopCastingReceiver"
    echo ""

    # Prompt for SSL certificate generation
    echo "===================================="
    echo "Optional: SSL Certificate Setup"
    echo "===================================="
    echo ""
    read -p "Generate SSL certificates for HTTPS? (Y/n) " ssl_response
    ssl_response=${ssl_response:-Y}

    if [[ ! "$ssl_response" =~ ^[Nn]$ ]]; then
        echo "Generating SSL certificates..."
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        [ -z "$LOCAL_IP" ] && LOCAL_IP="127.0.0.1"

        openssl req -x509 -newkey rsa:2048 -nodes \
            -out ./dist/DesktopCastingReceiver/cert.pem \
            -keyout ./dist/DesktopCastingReceiver/key.pem \
            -days 365 \
            -subj "/C=US/ST=State/L=City/O=Desktop Casting/CN=$LOCAL_IP" \
            2>/dev/null

        if [ -f "./dist/DesktopCastingReceiver/cert.pem" ]; then
            echo "✓ SSL certificates created!"
            echo "  Local IP: $LOCAL_IP"
        else
            echo "⚠ SSL certificate generation failed"
        fi
    fi

    echo ""
    echo "===================================="
    echo "Feature Summary"
    echo "===================================="
    echo ""
    echo "✓ WebRTC screen casting (Chrome, Chromebook, Android)"
    echo "✓ mDNS discovery for Chrome devices"
    echo "✓ iOS support via camera streaming"

    if command -v uxplay &> /dev/null; then
        echo "✓ UxPlay installed - iOS screen mirroring available"
    else
        echo "  UxPlay not installed - iOS limited to camera"
        echo "  Install: sudo apt-get install uxplay"
    fi

    echo ""
else
    echo ""
    echo "===================================="
    echo "✗ Build Failed!"
    echo "===================================="
    exit 1
fi
