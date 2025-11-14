# Build Troubleshooting Guide

## ERROR: "Microsoft Visual C++ 14.0 or greater is required"

This is the most common issue. The `av` package needs compilation. Here are your options:

### 🚀 EASIEST: Use the Easy Build Script (No Visual Studio Required!)

```powershell
.\build_windows_easy.ps1
```

This script tries to use pre-built wheels, avoiding the need for Visual Studio Build Tools.

### Option A: Try Installing av with Wheel

```powershell
# Activate your venv
.\venv_build\Scripts\Activate.ps1

# Try installing av with prefer-binary flag
pip install av --prefer-binary
```

If this works, then run the build script again.

### Option B: Download Pre-built Wheel Manually

1. Visit: https://github.com/PyAV-Org/PyAV/releases
2. Download the wheel for Python 3.12 Windows:
   - Look for: `av-*-cp312-cp312-win_amd64.whl`
   - Example: `av-11.0.0-cp312-cp312-win_amd64.whl`
3. Install it:
```powershell
.\venv_build\Scripts\Activate.ps1
pip install path\to\downloaded\av-*.whl
```
4. Then run build script again

### Option C: Install Visual Studio Build Tools (Last Resort)

Only if the above options don't work:
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++" workload (5+ GB)
3. Restart your terminal
4. Run build script again

---

## Quick Fix for Python 3.12.9

If the build script fails, try this manual process:

### Option 1: Use Flexible Requirements (Recommended)

```powershell
# Create and activate virtual environment
python -m venv venv_build
.\venv_build\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install with flexible requirements
pip install -r requirements-flexible.txt

# Build
pyinstaller desktop_caster.spec --clean
```

### Option 2: Install Dependencies One by One

If Option 1 fails, install packages individually to identify the problem:

```powershell
.\venv_build\Scripts\Activate.ps1

# Install in order (easier packages first)
pip install aiohttp
pip install Pillow
pip install numpy
pip install websockets
pip install opencv-python
pip install av
pip install aiortc
pip install pyinstaller

# Then build
pyinstaller desktop_caster.spec --clean
```

### Option 3: Use Pre-built Wheels

For packages that fail to install (especially `av` or `aiortc`):

1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. Download the appropriate `.whl` file for your Python version
3. Install: `pip install path\to\downloaded.whl`

## Common Issues

### Issue: "No module named '_ssl'"
**Solution**: Reinstall Python with SSL support enabled

### Issue: "Microsoft Visual C++ 14.0 is required"
**Solution**: Install Visual Studio Build Tools
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++" workload

### Issue: numpy installation fails
**Solution**: Use newer numpy version
```powershell
pip install numpy>=1.26.0
```

### Issue: av or aiortc fails
**Solution**: These require FFmpeg libraries
1. Try installing av first: `pip install av`
2. If that fails, you may need to install FFmpeg system-wide

## Testing Without Building

You can run the application without building an executable:

```powershell
# Activate your existing venv
.\venv\Scripts\Activate.ps1

# Run directly
python run.py
```

## Need Help?

If you continue having issues:
1. Check the full error message
2. Verify your Python version: `python --version`
3. Make sure you're using Python 3.11 or 3.12 (not 3.14+)
