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

    # Check if UxPlay is installed
    if ! command -v uxplay &> /dev/null; then
        echo ""
        echo "=================================="
        echo "Optional: iOS Screen Mirroring"
        echo "=================================="
        echo ""
        echo "For iOS screen mirroring support, UxPlay needs to be installed."
        echo ""
        echo "UxPlay enables:"
        echo "  - True iOS screen mirroring via AirPlay"
        echo "  - Native protocol support (no browser needed)"
        echo "  - Better quality than camera fallback"
        echo ""
        echo "Without UxPlay:"
        echo "  - iOS devices can still use camera streaming via browser"
        echo "  - Connect at http://<your-ip>:8080"
        echo ""
        read -p "Would you like to install UxPlay now? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "Running UxPlay installation script..."
            chmod +x install_uxplay.sh
            ./install_uxplay.sh
        else
            echo ""
            echo "You can install UxPlay later by running:"
            echo "  ./install_uxplay.sh"
            echo ""
        fi
    else
        echo ""
        echo "✓ UxPlay is already installed - iOS screen mirroring enabled!"
        echo ""
    fi
else
    echo ""
    echo "=================================="
    echo "✗ Build failed!"
    echo "=================================="
    exit 1
fi
