# Building Desktop Casting Receiver

This guide covers building standalone executables for Desktop Casting Receiver on Windows, Linux, and macOS.

## Table of Contents
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Building on Windows](#building-on-windows)
- [Building on Linux/macOS](#building-on-linuxmacos)
- [Troubleshooting](#troubleshooting)
- [Running Without Building](#running-without-building)

---

## Quick Start

### Windows
```powershell
# Recommended: Use the easy build script
.\build_windows_easy.ps1
```

### Linux/macOS
```bash
# Run the build script
./build.sh
```

The executable will be created in `dist/DesktopCastingReceiver/`

---

## Requirements

### Python Version
- **Recommended**: Python 3.11 or 3.12
- **Avoid**: Python 3.14+ (many packages lack pre-built wheels)

Check your version:
```bash
python --version
```

### Build Dependencies
All platforms need:
- Python 3.11 or 3.12
- pip (Python package installer)
- Virtual environment support

**Windows-specific:**
- PowerShell (for build_windows_easy.ps1)
- OR Command Prompt (for alternative methods)

**Linux-specific:**
- Development tools (`build-essential` on Debian/Ubuntu)
- Python development headers

**macOS-specific:**
- Xcode Command Line Tools

---

## Building on Windows

### Option 1: Easy Build Script (Recommended)

This script automatically handles dependencies and uses pre-built wheels when possible:

```powershell
.\build_windows_easy.ps1
```

The script will:
1. Check Python version compatibility
2. Create a build virtual environment
3. Install dependencies (using pre-built wheels)
4. Generate SSL certificates if needed
5. Build the executable with PyInstaller
6. Offer to run the executable

### Option 2: Manual Build Process

If you prefer manual control or the script fails:

#### Step 1: Create Virtual Environment
```powershell
# Remove old venv if exists
Remove-Item -Recurse -Force venv_build -ErrorAction SilentlyContinue

# Create new venv with Python 3.11 or 3.12
python -m venv venv_build

# Activate it
.\venv_build\Scripts\Activate.ps1  # PowerShell
# OR
venv_build\Scripts\activate.bat    # Command Prompt
```

#### Step 2: Install Dependencies
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**If `av` package fails**, see [Troubleshooting: av Package Issues](#av-package-installation-issues)

#### Step 3: Build Executable
```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build with PyInstaller
pyinstaller desktop_caster.spec --clean
```

#### Step 4: Run the Executable
```powershell
cd dist\DesktopCastingReceiver
.\DesktopCastingReceiver.exe
```

### Using Specific Python Version

If you have multiple Python versions:
```powershell
# List available versions
py --list

# Use specific version
py -3.11 -m venv venv_build
.\venv_build\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller desktop_caster.spec --clean
```

---

## Building on Linux/macOS

### Using Build Script (Recommended)

```bash
# Make script executable (first time only)
chmod +x build.sh

# Run the build script
./build.sh
```

The script will:
1. Create a virtual environment
2. Install dependencies
3. Prompt for SSL certificate generation
4. Check for optional dependencies (UxPlay, GStreamer)
5. Build the executable

### Manual Build Process

#### Step 1: Install System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3-venv python3-dev build-essential
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-devel gcc gcc-c++
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

#### Step 2: Create Virtual Environment
```bash
# Create venv
python3 -m venv venv_build

# Activate it
source venv_build/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Build Executable
```bash
# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller desktop_caster.spec --clean
```

#### Step 5: Run the Executable
```bash
cd dist/DesktopCastingReceiver
./DesktopCastingReceiver
```

---

## Troubleshooting

### Python Version Issues

#### Error: "No pre-built wheel for Python 3.14"

**Cause**: Python 3.14 is too new; many packages lack compatible wheels.

**Solution**: Install Python 3.11 or 3.12
1. Download from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Use the new version:
   ```powershell
   py -3.11 -m venv venv_build
   .\venv_build\Scripts\Activate.ps1
   pip install -r requirements.txt
   pyinstaller desktop_caster.spec --clean
   ```

### av Package Installation Issues

The `av` package (PyAV) is the most common installation problem.

#### Method 1: Use Pre-built Binary
```bash
pip install av --prefer-binary
```

#### Method 2: Download Wheel Manually (Windows)
1. Visit: https://github.com/PyAV-Org/PyAV/releases
2. Download the wheel for your Python version:
   - Python 3.11: `av-*-cp311-cp311-win_amd64.whl`
   - Python 3.12: `av-*-cp312-cp312-win_amd64.whl`
3. Install it:
   ```powershell
   .\venv_build\Scripts\Activate.ps1
   pip install path\to\av-*.whl
   ```

#### Method 3: Install Compilation Tools (Last Resort)

**Windows**: Install Visual Studio Build Tools
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "Desktop development with C++"
4. Install (requires ~6GB)
5. Restart terminal

**Linux**: Install development packages
```bash
# Debian/Ubuntu
sudo apt install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev

# Fedora/RHEL
sudo dnf install ffmpeg-devel
```

**macOS**: Install FFmpeg
```bash
brew install ffmpeg
```

### Common Build Errors

#### Error: "Microsoft Visual C++ 14.0 or greater is required"

**Windows only** - `av` package needs compilation.

**Solutions** (in order of preference):
1. Use Python 3.11 or 3.12 (easiest)
2. Download pre-built wheel (see above)
3. Use build_windows_easy.ps1 script
4. Install Visual Studio Build Tools

#### Error: "No module named 'PIL'"

**Cause**: Dependencies not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

#### Error: "python: command not found"

**Cause**: Python not in PATH.

**Solutions**:
1. Reinstall Python with "Add to PATH" option
2. Use full path: `/usr/bin/python3` or `C:\Python311\python.exe`
3. Use py launcher (Windows): `py -3.11`

#### Build Succeeds but Executable Won't Run

**Causes**:
- Missing DLL files (Windows)
- Missing shared libraries (Linux)
- Antivirus blocking execution
- Incorrect file permissions

**Solutions**:
1. Run from the dist/DesktopCastingReceiver/ directory
2. Check for error messages in terminal
3. Add antivirus exception for dist folder
4. Check file permissions: `chmod +x DesktopCastingReceiver` (Linux/macOS)

### WSL Users (Windows Subsystem for Linux)

**Don't build from WSL** - tkinter GUIs don't work well in WSL.

Instead:
1. Open PowerShell or Command Prompt on Windows
2. Navigate to project: `cd C:\Users\YourName\path\to\project`
3. Run Windows build script: `.\build_windows_easy.ps1`

---

## Running Without Building

You don't need to build an executable to use the application. Run directly from source:

### Windows
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the application
python run.py
```

### Linux/macOS
```bash
# Activate venv
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the application
python run.py
```

---

## Build Output

After successful build, find the executable in:
```
dist/DesktopCastingReceiver/
├── DesktopCastingReceiver.exe  (Windows)
├── DesktopCastingReceiver      (Linux/macOS)
├── client.html
├── server.py
├── airplay_receiver.py
├── uxplay_integration.py
└── [library files and DLLs]
```

You can:
- Run it directly from this folder
- Copy the entire folder to another computer
- Create a desktop shortcut to the executable
- Distribute the whole folder (it's portable)

### Size and Performance
- **Build time**: 3-10 minutes
- **Executable size**: 150-300 MB (includes Python runtime and dependencies)
- **First run**: May take a few seconds to initialize
- **Subsequent runs**: Starts quickly

---

## Generating SSL Certificates

SSL certificates are needed for HTTPS connections (required for screen capture on some browsers).

### Automatic Generation
The build scripts prompt for SSL certificate generation. Choose "yes" when asked.

### Manual Generation

**Linux/macOS:**
```bash
./generate_ssl.sh
```

**Windows:**
```powershell
.\generate_ssl.ps1
```

Certificates will be created in the `dist/DesktopCastingReceiver/` folder.

**Note**: Self-signed certificates will show browser warnings. Users must accept the certificate to connect.

---

## Need More Help?

- **Installation issues**: See [INSTALLATION.md](INSTALLATION.md)
- **Runtime problems**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Testing connectivity**: See [TESTING.md](TESTING.md)
- **UxPlay setup**: See [INSTALL_UXPLAY.md](INSTALL_UXPLAY.md)
