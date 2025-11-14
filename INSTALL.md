# Installation Guide

## Quick Setup (5 minutes)

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed:
```bash
python3 --version
```

### Step 2: Clone or Download
If you haven't already, get the code:
```bash
cd /home/trevorfulham/Documents/github/reciever
```

### Step 3: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python run.py
```

That's it! The GUI will open.

## First Time Use

1. **Click "Start Server"** in the GUI
2. **Note your IP address** from the popup (e.g., 192.168.1.100)
3. **On a Chromebook**, open Chrome and visit `http://192.168.1.100:8080`
4. **Enter a name** and click "Start Sharing Screen"
5. **Select your screen** when prompted
6. **Watch the stream** appear in the GUI!

## Building Executable (Optional)

If you want a standalone app without Python:

### Linux/macOS
```bash
./build.sh
cd dist/DesktopCastingReceiver
./DesktopCastingReceiver
```

### Windows
```cmd
build.bat
cd dist\DesktopCastingReceiver
DesktopCastingReceiver.exe
```

The executable will be in `dist/DesktopCastingReceiver/`

## Common Issues

### "Command not found: python3"
Try `python` instead of `python3`:
```bash
python --version
python -m venv venv
```

### Port 8080 Already in Use
Kill the process using port 8080:
```bash
# Linux/Mac
lsof -ti:8080 | xargs kill -9

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Chromebook Can't Connect
1. Make sure both devices are on the **same WiFi network**
2. Check your firewall settings
3. Try accessing `http://localhost:8080` on your monitoring computer first

### Missing Dependencies on Linux
Install system packages:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
sudo apt-get install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev

# Fedora/RHEL
sudo dnf install python3-devel python3-pip
sudo dnf install ffmpeg-devel
```

## Next Steps

Once installed, check out:
- [README.md](README.md) - Full documentation
- [Troubleshooting section](README.md#troubleshooting) - Common problems and solutions
- Configuration options for customizing streams and ports

## Need Help?

1. Check the terminal/console for error messages
2. Review the [README.md](README.md) for detailed info
3. Make sure all devices are on the same network
4. Test with just one Chromebook first

Enjoy monitoring your Chromebooks! 🖥️
