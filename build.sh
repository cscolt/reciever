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
else
    echo ""
    echo "=================================="
    echo "✗ Build failed!"
    echo "=================================="
    exit 1
fi
