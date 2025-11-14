# Windows Build Guide

## Quick Start

### Option 1: PowerShell (Recommended)
```powershell
# Run from project directory
.\build_windows.ps1
```

### Option 2: Command Prompt
```cmd
build_windows_simple.bat
```

### Option 3: Manual Build
See "Manual Build Process" below.

---

## Python Version Compatibility

### ⚠️ IMPORTANT: Python 3.14 Limitation

**Your system has Python 3.14 installed**, which is very new. Many required packages (especially `av` and `google-crc32c`) don't have pre-built wheels for Python 3.14 yet and require C++ compilation.

### Recommended Solutions

#### Solution 1: Install Python 3.11 or 3.12 (Easiest)

1. **Download Python 3.11** (recommended):
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11.9 or 3.12.x
   - During installation, check "Add Python to PATH"

2. **Use the new Python version**:
   ```powershell
   # If you have py launcher (recommended)
   py -3.11 -m venv venv_build
   venv_build\Scripts\activate
   pip install -r requirements.txt
   pyinstaller desktop_caster.spec --clean
   ```

   OR specify the path:
   ```powershell
   C:\Python311\python.exe -m venv venv_build
   venv_build\Scripts\activate
   pip install -r requirements.txt
   pyinstaller desktop_caster.spec --clean
   ```

#### Solution 2: Install Visual Studio Build Tools

If you want to keep Python 3.14, install C++ build tools:

1. **Download Visual Studio Build Tools**:
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Click "Download Build Tools"

2. **Install C++ Development Tools**:
   - Run the installer
   - Select "Desktop development with C++"
   - Click Install (requires ~6GB)
   - Restart your computer

3. **Run the build script**:
   ```powershell
   .\build_windows.ps1
   ```

---

## Manual Build Process

### Step 1: Create Virtual Environment

```powershell
# Remove old venv if exists
Remove-Item -Recurse -Force venv_build -ErrorAction SilentlyContinue

# Create new venv
python -m venv venv_build

# Activate it
.\venv_build\Scripts\Activate.ps1  # PowerShell
# OR
venv_build\Scripts\activate.bat    # Command Prompt
```

### Step 2: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**If this fails**, see "Troubleshooting" below.

### Step 3: Build Executable

```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build with PyInstaller
pyinstaller desktop_caster.spec --clean
```

### Step 4: Run the Executable

```powershell
cd dist\DesktopCastingReceiver
.\DesktopCastingReceiver.exe
```

---

## Troubleshooting

### Error: "Microsoft Visual C++ 14.0 or greater is required"

**Cause**: Python packages like `av` need to be compiled from source.

**Solutions**:
1. Install Python 3.11/3.12 (easiest)
2. Install Visual Studio Build Tools (see Solution 2 above)

### Error: "Could not find a version that satisfies the requirement av"

**Cause**: No pre-built wheel for your Python version.

**Solution**: Use Python 3.11 or 3.12

### Error: "No module named 'PIL'"

**Cause**: Dependencies not installed.

**Solution**:
```powershell
pip install -r requirements.txt
```

### Error: "python: command not found"

**Cause**: Python not in PATH.

**Solutions**:
1. Reinstall Python and check "Add to PATH"
2. Use full path: `C:\Python311\python.exe`
3. Use py launcher: `py -3.11`

### Build succeeds but executable doesn't run

**Causes**:
- Missing DLL files
- Antivirus blocking
- Windows Defender SmartScreen

**Solutions**:
1. Check Windows Defender logs
2. Add exception for the dist folder
3. Run from dist\DesktopCastingReceiver\ directory
4. Check console output for errors

---

## Alternative: Run Without Building

If building is problematic, you can run directly from source:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies (one time)
pip install -r requirements.txt

# Run the application
python run.py
```

---

## WSL Users

If you're using WSL (Windows Subsystem for Linux):

1. **Don't build from WSL** - tkinter GUIs don't work well
2. **Open PowerShell or Command Prompt on Windows**
3. **Navigate to your project**:
   ```powershell
   cd C:\Users\control\Documents\reciever-master\reciever-master
   ```
4. **Run the build script**:
   ```powershell
   .\build_windows.ps1
   ```

---

## Checking Your Python Version

```powershell
# Check version
python --version

# If you have multiple Python versions
py --list  # Shows all installed versions
py -3.11 --version  # Use specific version
```

---

## Build Script Details

### build_windows.ps1 (PowerShell)
- Full-featured with colored output
- Checks Python version compatibility
- Provides helpful error messages
- Offers to run executable after build

### build_windows_simple.bat (Batch)
- Simple, reliable
- Works in Command Prompt
- No special features needed

### build.bat (Original)
- Basic build script
- May not work with Python 3.14

---

## After Building

The executable and all dependencies will be in:
```
dist\DesktopCastingReceiver\
├── DesktopCastingReceiver.exe  ← Main executable
├── client.html                  ← Web interface
├── server.py                    ← Server module
└── [many DLL and library files]
```

You can:
1. Run it directly from that folder
2. Copy the entire folder to another Windows computer
3. Create a shortcut to the .exe file
4. Distribute the whole folder (it's portable)

---

## Size and Performance

- **Build time**: 3-10 minutes
- **Executable size**: ~150-300 MB (includes Python runtime and all dependencies)
- **First run**: May take a few seconds to initialize
- **Subsequent runs**: Starts quickly

---

## Need Help?

1. Check the error message carefully
2. Read this guide's Troubleshooting section
3. See TROUBLESHOOTING.md for runtime issues
4. Verify your Python version is 3.11 or 3.12

## Summary for Python 3.14 Users

**You have Python 3.14, which is too new. Please:**

1. Install Python 3.11 from https://www.python.org/downloads/
2. Use py launcher: `py -3.11 build_windows.ps1`
3. OR install Visual Studio Build Tools

**Quick fix:**
```powershell
# Download and install Python 3.11.9
# Then run:
py -3.11 -m venv venv_build
.\venv_build\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller desktop_caster.spec --clean
```
