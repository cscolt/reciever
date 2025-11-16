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
    echo "iOS Screen Mirroring Support"
    echo "=================================="
    echo ""
    echo "✓ Built-in Python AirPlay receiver included!"
    echo ""
    echo "Features:"
    echo "  - Native AirPlay protocol support"
    echo "  - Real cryptography (SRP-6a, Ed25519, ChaCha20)"
    echo "  - H.264 video decoding"
    echo "  - No external dependencies required"
    echo ""
    echo "iOS devices will automatically discover this receiver"
    echo "in Control Center > Screen Mirroring"
    echo ""
else
    echo ""
    echo "=================================="
    echo "✗ Build failed!"
    echo "=================================="
    exit 1
fi
