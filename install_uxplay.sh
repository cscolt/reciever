#!/bin/bash
# UxPlay Installation Script for Linux/macOS
# Automates the process of installing UxPlay for iOS screen mirroring

set -e  # Exit on error

echo "========================================"
echo "UxPlay Installation Script"
echo "========================================"
echo ""
echo "This script will install UxPlay, enabling iOS screen mirroring"
echo "for Desktop Casting Receiver."
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Detected: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "Detected: macOS"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

echo ""

# Check if UxPlay is already installed
if command -v uxplay &> /dev/null; then
    echo "✓ UxPlay is already installed!"
    uxplay -h 2>&1 | head -n 1
    echo ""
    read -p "Do you want to reinstall/update UxPlay? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

echo ""
echo "========================================"
echo "Step 1: Installing Dependencies"
echo "========================================"
echo ""

if [ "$OS" = "linux" ]; then
    # Check if we have apt (Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        echo "Installing dependencies via apt-get..."
        echo "Note: This will require sudo access"
        echo ""

        sudo apt-get update
        sudo apt-get install -y \
            cmake \
            pkg-config \
            libssl-dev \
            libplist-dev \
            libavahi-compat-libdnssd-dev \
            libgstreamer1.0-dev \
            libgstreamer-plugins-base1.0-dev \
            gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad \
            gstreamer1.0-plugins-ugly \
            gstreamer1.0-libav \
            git

        echo ""
        echo "✓ Dependencies installed successfully"

    # Check if we have dnf (Fedora/RHEL)
    elif command -v dnf &> /dev/null; then
        echo "Installing dependencies via dnf..."
        echo "Note: This will require sudo access"
        echo ""

        sudo dnf install -y \
            cmake \
            gcc-c++ \
            openssl-devel \
            libplist-devel \
            avahi-compat-libdns_sd-devel \
            gstreamer1-devel \
            gstreamer1-plugins-base-devel \
            gstreamer1-plugins-good \
            gstreamer1-plugins-bad-free \
            gstreamer1-plugins-ugly-free \
            gstreamer1-libav \
            git

        echo ""
        echo "✓ Dependencies installed successfully"

    else
        echo "❌ Could not detect package manager (apt-get or dnf)"
        echo "Please install dependencies manually:"
        echo "  - cmake, pkg-config, git"
        echo "  - libssl-dev, libplist-dev"
        echo "  - libavahi-compat-libdnssd-dev"
        echo "  - gstreamer1.0 and plugins"
        exit 1
    fi

elif [ "$OS" = "macos" ]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew is not installed!"
        echo ""
        echo "Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo ""
        echo "Then run this script again."
        exit 1
    fi

    echo "Installing dependencies via Homebrew..."
    echo ""

    brew install \
        cmake \
        pkg-config \
        openssl \
        libplist \
        gstreamer \
        gst-plugins-base \
        gst-plugins-good \
        gst-plugins-bad \
        gst-plugins-ugly \
        gst-libav

    echo ""
    echo "✓ Dependencies installed successfully"
fi

echo ""
echo "========================================"
echo "Step 2: Downloading UxPlay"
echo "========================================"
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "Cloning UxPlay repository..."
git clone https://github.com/FDH2/UxPlay.git
cd UxPlay

echo "✓ Downloaded successfully"

echo ""
echo "========================================"
echo "Step 3: Building UxPlay"
echo "========================================"
echo ""

mkdir -p build
cd build

echo "Running CMake..."
if [ "$OS" = "macos" ]; then
    # On macOS, specify OpenSSL location for CMake
    cmake -DOPENSSL_ROOT_DIR=$(brew --prefix openssl) ..
else
    cmake ..
fi

echo ""
echo "Compiling (this may take a few minutes)..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)

echo ""
echo "✓ Build completed successfully"

echo ""
echo "========================================"
echo "Step 4: Installing UxPlay"
echo "========================================"
echo ""
echo "Installing to system (requires sudo)..."

sudo make install

# Update library cache on Linux
if [ "$OS" = "linux" ]; then
    sudo ldconfig 2>/dev/null || true
fi

echo ""
echo "✓ UxPlay installed successfully"

# Cleanup
echo ""
echo "Cleaning up temporary files..."
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "✓ Installation Complete!"
echo "========================================"
echo ""

# Verify installation
if command -v uxplay &> /dev/null; then
    echo "UxPlay version:"
    uxplay -h 2>&1 | head -n 1 || echo "UxPlay installed"
    echo ""
    echo "✓ UxPlay is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Run your Desktop Casting Receiver application"
    echo "  2. On your iPhone/iPad: Control Center → Screen Mirroring"
    echo "  3. Select 'Desktop Casting Receiver'"
    echo ""
else
    echo "⚠ Warning: UxPlay command not found in PATH"
    echo "You may need to:"
    echo "  - Restart your terminal"
    echo "  - Add /usr/local/bin to your PATH"
    echo "  - Run: export PATH=\"/usr/local/bin:\$PATH\""
    echo ""
fi
