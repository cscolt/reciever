# Troubleshooting Guide - Desktop Casting Receiver

## Quick Fix: Run on Windows (Not WSL)

This application uses tkinter for GUI, which works best on Windows directly.

### Windows Setup (Recommended):

```cmd
# Open Command Prompt or PowerShell
cd C:\Users\control\Documents\reciever-master\reciever-master

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the application
python run.py
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'PIL'"

**Cause**: Dependencies not installed

**Solution**:
```cmd
pip install -r requirements.txt
```

### Issue 2: Running from WSL doesn't show GUI

**Cause**: tkinter requires X server in WSL

**Solutions**:

**Option A**: Run on Windows (see above) ✅ Recommended

**Option B**: Install X server for WSL
1. Install VcXsrv or use WSLg (Windows 11)
2. Set DISPLAY environment variable:
   ```bash
   export DISPLAY=:0
   ```
3. Install dependencies in WSL venv

### Issue 3: "error: externally-managed-environment"

**Cause**: Python 3.13+ uses PEP 668 restrictions

**Solution**: Always use virtual environments:

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/WSL**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Server won't start - Port 8080 in use

**Check what's using port 8080**:

**Windows**:
```cmd
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Linux/WSL**:
```bash
lsof -i :8080
kill -9 <PID>
```

**Or change the port** in `server.py` line 214 and `viewer.py` line 185

### Issue 5: Chromebooks can't connect

**Checklist**:
- [ ] All devices on same WiFi network
- [ ] Firewall allows port 8080
- [ ] Using correct IP address (not localhost)
- [ ] Server is running (check GUI status)

**Get your IP address**:

**Windows**:
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually 192.168.x.x)

**Linux**:
```bash
ip addr show
```

### Issue 6: Certificate warnings in browser (HTTPS mode)

**Expected behavior**: Self-signed certificates trigger warnings

**To proceed**:
1. Click "Advanced" in browser
2. Click "Proceed to [IP address]" or "Accept Risk"
3. This is safe on your local network

**To avoid warnings**: Use HTTP mode by removing cert.pem and key.pem files

### Issue 7: No video appears in GUI

**Causes**:
- Chromebook didn't grant screen sharing permission
- WebRTC connection failed
- Network issues

**Solutions**:
1. Check browser console (F12) on Chromebook for errors
2. Try refreshing the Chromebook browser page
3. Restart the server
4. Check firewall settings

### Issue 8: Streams are laggy or dropping frames

**Solutions**:
- Reduce number of simultaneous streams
- Ensure strong WiFi signal
- Close unnecessary applications
- Update network drivers
- Check CPU usage (high CPU can cause lag)

### Issue 9: "Maximum streams reached"

**Current limit**: 8 simultaneous streams

**To increase**:
1. Edit `server.py` line 67:
   ```python
   stream_manager = StreamManager(max_streams=16)  # Your desired number
   ```
2. Edit `viewer.py` line 124-172 to adjust grid layout for more streams

### Issue 10: Build executable fails

**Common causes**:
- Dependencies not installed
- Missing files
- PyInstaller not installed

**Solution**:
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Clean previous builds
rm -rf build/ dist/

# Rebuild
./build.sh  # Linux/Mac
# OR
build.bat   # Windows
```

## Testing Checklist

Before using with Chromebooks, test locally:

1. [ ] Run `python run.py`
2. [ ] Click "Start Server"
3. [ ] Open browser on same computer
4. [ ] Visit http://localhost:8080
5. [ ] Enter test name and share screen
6. [ ] Verify video appears in GUI

## Getting Help

If none of these solutions work:

1. Check terminal/console for error messages
2. Review `CLAUDE.md` for architecture details
3. Ensure Python version is 3.8+
4. Try running server.py and viewer.py separately:
   ```bash
   # Terminal 1
   python server.py

   # Terminal 2
   python viewer.py
   ```

## Environment Details

- **Working from**: WSL (Windows Subsystem for Linux)
- **Project location**: C:\Users\control\Documents\reciever-master\reciever-master
- **Python version**: 3.13.5 in WSL, likely different in Windows
- **Virtual envs**: `venv` and `myenv` exist (Windows-based)
