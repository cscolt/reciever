#!/bin/bash
# Install GStreamer Python bindings for video capture
# Required for iPhone screen mirroring with real video

echo "=========================================="
echo "GStreamer Python Bindings Installer"
echo "=========================================="
echo ""
echo "This installs python3-gi and python3-gst-1.0"
echo "Required for iPhone screen mirroring video capture"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Assuming Ubuntu/Debian."
    OS="ubuntu"
fi

echo "Detected OS: $OS"
echo ""

case $OS in
    ubuntu|debian|pop)
        echo "Installing for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
        sudo apt-get install -y python3-gst-1.0 gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good
        ;;
    fedora|rhel|centos)
        echo "Installing for Fedora/RHEL..."
        sudo dnf install -y python3-gobject gtk3
        sudo dnf install -y python3-gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good
        ;;
    arch|manjaro)
        echo "Installing for Arch..."
        sudo pacman -S --noconfirm python-gobject gtk3
        sudo pacman -S --noconfirm gst-python gstreamer gst-plugins-base gst-plugins-good
        ;;
    *)
        echo "Unknown OS: $OS"
        echo "Please manually install:"
        echo "  - python3-gi (PyGObject)"
        echo "  - python3-gst-1.0 (GStreamer Python bindings)"
        echo "  - gstreamer1.0-tools"
        echo "  - gstreamer1.0-plugins-base"
        exit 1
        ;;
esac

# Test installation
echo ""
echo "=========================================="
echo "Testing Installation..."
echo "=========================================="

python3 << 'EOF'
import sys

try:
    import gi
    print("✓ PyGObject (gi) installed")

    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib
    print("✓ GStreamer Python bindings installed")

    Gst.init(None)
    print("✓ GStreamer initialized successfully")

    print("")
    print("========================================")
    print("✓ Installation Successful!")
    print("========================================")
    print("")
    print("iPhone screen mirroring will now show real video")
    print("Restart the Desktop Casting Receiver to use it")
    sys.exit(0)

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("")
    print("Installation may have failed")
    print("Try manually: sudo apt-get install python3-gi python3-gst-1.0")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
EOF
