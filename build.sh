#!/bin/bash
# Build script for Desktop Casting Receiver

echo "=================================="
echo "Desktop Casting Receiver Builder"
echo "=================================="
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
echo "Building executable..."
pyinstaller desktop_caster.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✓ Build successful!"
    echo "=================================="
    echo ""
    echo "Executable location:"
    echo "  ./dist/DesktopCastingReceiver/DesktopCastingReceiver"
    echo ""
    echo "To run:"
    echo "  cd dist/DesktopCastingReceiver"
    echo "  ./DesktopCastingReceiver"
    echo ""
    echo "=================================="
    echo "NEW: Chrome/Chromebook Discovery"
    echo "=================================="
    echo ""
    echo "✓ mDNS service advertisement included!"
    echo ""
    echo "Chrome and Chromebook devices can now:"
    echo "  - Automatically discover this receiver"
    echo "  - Find it in Chrome Cast menu"
    echo "  - Or manually visit: http://<your-ip>:8080"
    echo ""
    echo "=================================="
    echo "iOS Screen Mirroring Support"
    echo "=================================="
    echo ""
    echo "Two methods available:"
    echo ""
    echo "1. UxPlay (RECOMMENDED - Real video capture)"
    if command -v uxplay &> /dev/null; then
        echo "   ✓ UxPlay is installed"
        if command -v gst-launch-1.0 &> /dev/null; then
            echo "   ✓ GStreamer is installed - REAL video will work!"
        else
            echo "   ✗ GStreamer NOT installed - only placeholder frames"
            echo "   Install: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base"
        fi
    else
        echo "   ✗ UxPlay is NOT installed"
        echo "   Install from: https://github.com/FDH2/UxPlay"
        echo "   Or run: ./install_uxplay.sh"
    fi
    echo ""
    echo "2. Python AirPlay (Built-in fallback)"
    echo "   ✓ Included with full crypto support"
    echo "   - SRP-6a authentication"
    echo "   - Ed25519 key exchange"
    echo "   - ChaCha20-Poly1305 encryption"
    echo "   - H.264 video decoding"
    echo ""
    echo "iOS devices will discover 'Desktop Casting Receiver'"
    echo "in Control Center > Screen Mirroring"
    echo ""

    # Prompt for SSL certificate generation
    echo "=================================="
    echo "Optional: SSL Certificate Setup"
    echo "=================================="
    echo ""
    echo "SSL certificates enable HTTPS connections, which are required for:"
    echo "  - Screen sharing on many browsers"
    echo "  - Camera access on mobile devices"
    echo "  - AirPlay screen mirroring from iOS devices"
    echo ""
    read -p "Would you like to generate SSL certificates now? (Y/n) " ssl_response
    ssl_response=${ssl_response:-Y}

    if [[ ! "$ssl_response" =~ ^[Nn]$ ]]; then
        echo ""
        echo "Generating SSL certificates..."

        # Get local IP
        LOCAL_IP=$(hostname -I | awk '{print $1}')
        if [ -z "$LOCAL_IP" ]; then
            LOCAL_IP="127.0.0.1"
        fi

        # Generate certificates directly in dist folder
        openssl req -x509 -newkey rsa:2048 -nodes \
            -out ./dist/DesktopCastingReceiver/cert.pem \
            -keyout ./dist/DesktopCastingReceiver/key.pem \
            -days 365 \
            -subj "/C=US/ST=State/L=City/O=Desktop Casting/CN=$LOCAL_IP" \
            2>/dev/null

        if [ -f "./dist/DesktopCastingReceiver/cert.pem" ] && [ -f "./dist/DesktopCastingReceiver/key.pem" ]; then
            echo ""
            echo "✓ SSL certificates created successfully!"
            echo "  cert.pem and key.pem in ./dist/DesktopCastingReceiver/"
            echo ""
            echo "Your local IP: $LOCAL_IP"
            echo ""
            echo "Devices can connect via:"
            echo "  https://$LOCAL_IP:8080"
            echo ""
        else
            echo ""
            echo "⚠ SSL certificate generation failed"
            echo "You can generate them later using: ./setup_ssl_for_exe.sh"
            echo ""
        fi
    fi

    echo ""
    echo "To run the application:"
    echo "  cd dist/DesktopCastingReceiver"
    echo "  ./DesktopCastingReceiver"
    echo ""
else
    echo ""
    echo "=================================="
    echo "✗ Build failed!"
    echo "=================================="
    exit 1
fi
