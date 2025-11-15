# Installing UxPlay for iOS Screen Mirroring

This guide explains how to install UxPlay to enable true iOS screen mirroring support in Desktop Casting Receiver.

## What is UxPlay?

UxPlay is an open-source AirPlay mirroring server that allows your computer to receive iOS screen mirroring connections. Installing UxPlay enables:

- **True iOS screen mirroring** via AirPlay protocol
- **Native iOS integration** - no browser required
- **Better quality** than camera streaming fallback
- **Full screen capture** from iPhone/iPad

## Quick Start

### Automatic Installation (Recommended)

The easiest way to install UxPlay is to use our automated installation scripts:

#### Linux/macOS:
```bash
./install_uxplay.sh
```

#### Windows:
```powershell
.\install_uxplay.ps1
```

These scripts will:
1. Check for required dependencies
2. Install missing dependencies (with your permission)
3. Download UxPlay source code
4. Build UxPlay
5. Install UxPlay to your system

### During Application Build

The build scripts (build.sh, build.bat, build_windows_easy.ps1) will automatically offer to install UxPlay after successfully building the application. Simply answer "y" when prompted.

## Manual Installation

If you prefer to install UxPlay manually, follow the platform-specific instructions below.

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    cmake pkg-config git \
    libssl-dev libplist-dev libavahi-compat-libdnssd-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav

# Clone and build UxPlay
git clone https://github.com/FDH2/UxPlay.git
cd UxPlay
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig
```

### Linux (Fedora/RHEL)

```bash
# Install dependencies
sudo dnf install -y \
    cmake gcc-c++ git \
    openssl-devel libplist-devel avahi-compat-libdns_sd-devel \
    gstreamer1-devel gstreamer1-plugins-base-devel \
    gstreamer1-plugins-good gstreamer1-plugins-bad-free \
    gstreamer1-plugins-ugly-free gstreamer1-libav

# Clone and build UxPlay
git clone https://github.com/FDH2/UxPlay.git
cd UxPlay
mkdir build && cd build
cmake ..
make
sudo make install
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake pkg-config openssl libplist \
    gstreamer gst-plugins-base gst-plugins-good \
    gst-plugins-bad gst-plugins-ugly gst-libav

# Clone and build UxPlay
git clone https://github.com/FDH2/UxPlay.git
cd UxPlay
mkdir build && cd build
cmake -DOPENSSL_ROOT_DIR=$(brew --prefix openssl) ..
make
sudo make install
```

### Windows

Windows installation is more complex and requires:
1. **Visual Studio Build Tools** (or Visual Studio Community)
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select: "Desktop development with C++"

2. **CMake**
   - Download: https://cmake.org/download/
   - Choose: Windows x64 Installer
   - Enable: Add CMake to system PATH

3. **Git for Windows**
   - Download: https://git-scm.com/download/win

4. **GStreamer**
   - Download runtime installer: https://gstreamer.freedesktop.org/download/
   - Download development installer: https://gstreamer.freedesktop.org/download/
   - Run both installers

Then build UxPlay:
```powershell
# Clone UxPlay
git clone https://github.com/FDH2/UxPlay.git
cd UxPlay
mkdir build
cd build

# Build
cmake -G "Visual Studio 17 2022" -A x64 ..
cmake --build . --config Release

# Install (copy to a directory in your PATH)
copy Release\uxplay.exe "C:\Program Files\UxPlay\"
```

**Tip:** Use our automated script `install_uxplay.ps1` instead - it handles all of this for you!

## Verifying Installation

After installation, verify UxPlay is working:

```bash
# Check if installed
uxplay -h

# Should show UxPlay help text
```

## Using UxPlay with Desktop Casting Receiver

Once UxPlay is installed:

1. **Start the application**
   - Run `python run.py` or use the built executable
   - The application will automatically detect UxPlay

2. **Check the logs**
   - You should see: "✓ UxPlay started successfully"
   - And: "iOS devices can mirror via AirPlay"

3. **Connect from iPhone/iPad**
   - Open Control Center
   - Tap "Screen Mirroring"
   - Select "Desktop Casting Receiver"
   - Your screen will appear in the application!

## Troubleshooting

### "UxPlay not found" after installation

**Linux/macOS:**
- Restart your terminal
- Check if `/usr/local/bin` is in your PATH:
  ```bash
  echo $PATH
  ```
- If not, add it:
  ```bash
  export PATH="/usr/local/bin:$PATH"
  ```

**Windows:**
- Restart PowerShell or Command Prompt
- Check if UxPlay directory is in your PATH
- Manually add to PATH if needed:
  - System → Advanced → Environment Variables → Path

### Build errors on Linux

**"Cannot find OpenSSL":**
```bash
sudo apt-get install libssl-dev
```

**"GStreamer not found":**
```bash
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
```

### Build errors on Windows

**"CMake not found":**
- Ensure CMake is installed
- Add CMake to PATH during installation
- Or manually add: `C:\Program Files\CMake\bin`

**"Cannot find Visual Studio":**
- Install Visual Studio Build Tools
- Ensure "Desktop development with C++" is selected

### iOS device can't find "Desktop Casting Receiver"

1. **Check network**: Ensure both devices on same WiFi
2. **Check firewall**: Allow port 7100 (UxPlay) and port 7000 (fallback)
3. **Check UxPlay is running**: Look for "✓ UxPlay started" in logs
4. **Restart application**: Sometimes mDNS discovery needs a fresh start

### Connection established but no video

**This is expected in current version!**
- UxPlay integration currently shows placeholder frames
- Full video decoding requires GStreamer pipeline integration (future enhancement)
- You will see confirmation that iOS device connected
- The infrastructure is working correctly

## Fallback Options

If UxPlay installation fails or isn't working:

### Option 1: Browser Camera Streaming (Always Available)
- No installation required
- On iPhone/iPad: Open Safari
- Go to: `http://<computer-ip>:8080`
- Allow camera access
- Point camera at screen/workspace

### Option 2: AirPlay to Mac, then Screen Share
If you have a Mac:
1. AirPlay from iPhone to Mac
2. Screen share from Mac to Desktop Casting Receiver via browser

## Getting Help

- **UxPlay issues**: https://github.com/FDH2/UxPlay/issues
- **Desktop Casting Receiver issues**: Check README.md troubleshooting section
- **Installation script issues**: Review script output for specific error messages

## Uninstalling UxPlay

### Linux/macOS:
```bash
sudo rm /usr/local/bin/uxplay
sudo rm -rf /usr/local/share/uxplay
```

### Windows:
Remove the directory where you installed UxPlay and remove from PATH.

---

**Note**: UxPlay is an external open-source project. Desktop Casting Receiver simply integrates with it to provide iOS screen mirroring support.
