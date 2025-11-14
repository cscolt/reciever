# Quick Build Guide

## 🚀 Easiest Way (Recommended)

Try the easy build script first - it uses pre-built wheels to avoid needing Visual Studio:

```powershell
.\build_windows_easy.ps1
```

## ⚡ If That Fails: Install av Package First

The build usually fails because of the `av` package. Try these in order:

### Try 1: Let pip find a wheel

```powershell
# Activate venv
.\venv_build\Scripts\Activate.ps1

# Try installing av
pip install av --prefer-binary
```

If successful, run `.\build_windows_easy.ps1` again.

### Try 2: Download pre-built wheel

1. Go to: https://github.com/PyAV-Org/PyAV/releases
2. Download: `av-11.0.0-cp312-cp312-win_amd64.whl` (or latest)
3. Install:
```powershell
.\venv_build\Scripts\Activate.ps1
pip install Downloads\av-11.0.0-cp312-cp312-win_amd64.whl
```
4. Run build script: `.\build_windows_easy.ps1`

### Try 3: Use existing environment

If you already have the app running in development mode, you can build from that environment:

```powershell
# Activate your working venv
.\venv\Scripts\Activate.ps1

# Clean old builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build
pyinstaller desktop_caster.spec --clean
```

## 🏗️ Last Resort: Install Visual Studio Build Tools

If nothing else works:
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++" (5+ GB download)
3. Restart PowerShell
4. Run: `.\build_windows.ps1`

## ✅ Test Without Building

You don't need to build an executable to use the app:

```powershell
.\venv\Scripts\Activate.ps1
python run.py
```

---

## Need More Help?

See: `BUILD_TROUBLESHOOTING.md` for detailed solutions
