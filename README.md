# Desktop Casting Receiver

A Python application that allows Chromebooks, iPhones, Android phones, and other devices to cast their screens or camera to a monitoring station. Monitor up to 8 simultaneous video streams in real-time.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Multi-Device Support**: Monitor up to 8 devices simultaneously (Chromebooks, iPhones, Android phones, desktops)
- **Intelligent Device Detection**: Automatically adapts to device capabilities
  - Screen sharing for desktop/Chromebook/Android Chrome
  - Camera streaming fallback for iOS and devices without screen capture
- **WebRTC Technology**: Low-latency, real-time video streaming
- **User-Friendly Interface**:
  - Mobile-responsive web interface
  - Professional GUI viewer with grid layout
  - Touch-friendly controls for mobile devices
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Standalone Executable**: Can be packaged as a single executable

## Architecture

```
┌─────────────────┐
│  Chromebook 1   │─────┐
│  (Screen Share) │     │
└─────────────────┘     │
                        │
┌─────────────────┐     │
│  Android Phone  │─────┤      ┌──────────────────┐      ┌─────────────┐
│ (Screen/Camera) │     ├─────>│  WebRTC Server   │─────>│  GUI Viewer │
└─────────────────┘     │      │  (Python/aiortc) │      │  (tkinter)  │
                        │      └──────────────────┘      └─────────────┘
┌─────────────────┐     │              ↑
│   iPhone/iPad   │─────┤         Runs on your
│ (Camera Stream) │     │      monitoring computer
└─────────────────┘     │
      ...               │
┌─────────────────┐     │
│   Desktop PC    │─────┘
│  (Screen Share) │
└─────────────────┘
```

## Quick Start

### Option 1: Run from Source (Recommended for Testing)

1. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python run.py
   ```

3. **Start the Server**
   - Click "Start Server" in the GUI
   - Note your computer's IP address (shown in the popup)

4. **Connect Devices**
   - On each device (Chromebook, phone, tablet, etc.), open a browser
   - Navigate to `http://<your-computer-ip>:8080`
   - Enter a device name
   - Click "Start Sharing Screen" (or "Start Camera Streaming" on iOS)
   - On desktop/Chromebook/Android: Select which screen to share
   - On iOS: Allow camera access when prompted

### Option 2: Build Executable

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
cd dist/DesktopCastingReceiver
./DesktopCastingReceiver
```

**Windows:**
```cmd
build.bat
cd dist\DesktopCastingReceiver
DesktopCastingReceiver.exe
```

## Usage Guide

### On the Monitoring Computer

1. **Launch the Application**
   - Run `python run.py` or use the built executable

2. **Start the Server**
   - Click the "Start Server" button
   - Make note of the IP address displayed

3. **Monitor Streams**
   - Connected devices appear in the 2x4 grid
   - Each slot shows:
     - Device name
     - Live screen feed
     - Connection status

### On Client Devices (Chromebooks, Phones, Tablets)

1. **Open Browser**
   - Desktop/Chromebook: Chrome, Edge, or any Chromium-based browser
   - Android: Chrome browser (recommended)
   - iOS: Safari browser

2. **Navigate to Server**
   - Go to `http://<monitoring-computer-ip>:8080`
   - The interface automatically adapts to your device type

3. **Start Sharing**
   - Enter a descriptive name (e.g., "Student 1", "iPhone 12", "Android Tablet")
   - Click "Start Sharing Screen" (or "Start Camera Streaming" on iOS)

   **For Desktop/Chromebook/Android Chrome:**
   - Select the screen/window you want to share
   - Click "Share"

   **For iOS or devices without screen capture:**
   - Allow camera access when prompted
   - The app will use your camera instead of screen sharing
   - Point camera at what you want to monitor

4. **Verify Connection**
   - You should see "Connected!" message with your capture mode
   - Your video feed should appear on the monitoring station

5. **Stop Sharing**
   - Click "Stop Sharing" button
   - Or close the browser tab

### On iOS Devices (AirPlay Method)

**This is the recommended method for iPhones and iPads as it provides true screen mirroring.**

#### Prerequisites: Install UxPlay (Recommended)

For the best iOS screen mirroring experience, install UxPlay on your monitoring computer.

**Quick Install (Automated):**

We provide automated installation scripts that handle all dependencies and building:

**Linux/macOS:**
```bash
./install_uxplay.sh
```

**Windows:**
```powershell
.\install_uxplay.ps1
```

These scripts will:
- Check for and install required dependencies
- Download and build UxPlay
- Install it to your system

**Automatic Installation During Build:**

The build scripts (build.sh, build.bat, build_windows_easy.ps1) will automatically offer to install UxPlay after building the application.

**Manual Installation:**

For manual installation instructions, see [INSTALL_UXPLAY.md](INSTALL_UXPLAY.md)

**Note:** If UxPlay is not installed, the application will fall back to Python AirPlay infrastructure (which has limited functionality) and browser-based camera streaming.

#### Using AirPlay Screen Mirroring

1. **Ensure Same Network**
   - Make sure your iPhone/iPad is on the same WiFi as the monitoring computer

2. **Start the Server**
   - Launch Desktop Casting Receiver
   - Click "Start Server"
   - The application will automatically detect and use UxPlay if available

3. **Open Control Center on iPhone/iPad**
   - iPhone X and later: Swipe down from top-right corner
   - iPhone 8 and earlier: Swipe up from bottom
   - iPad: Swipe down from top-right corner

4. **Start Screen Mirroring**
   - Tap "Screen Mirroring" button
   - Wait a moment for devices to appear
   - Select "Desktop Casting Receiver" from the list
   - Connection should establish automatically (no pairing code required with UxPlay)

5. **Verify Connection**
   - Your iPhone/iPad screen should appear on the monitoring station
   - Everything you do on your device will be visible in real-time
   - Status bar will show blue/green indicator that screen mirroring is active

6. **Stop Mirroring**
   - Open Control Center again
   - Tap "Screen Mirroring"
   - Tap "Stop Mirroring"
   - Or stop from the monitoring station

**Troubleshooting AirPlay:**
- **Device not appearing**: Ensure both devices are on the same network and the server is running
- **Connection fails**: Check firewall settings (port 7000 must be open)
- **UxPlay not detected**: Verify UxPlay is installed with `uxplay -h` in terminal
- **Lag or stuttering**: Move closer to WiFi router or reduce other network activity
- **Black screen**: Some apps (like Netflix) block screen mirroring for DRM protection
- **Fallback option**: If AirPlay isn't working, use the browser method (camera streaming) at http://<computer-ip>:8080

## System Requirements

### Monitoring Computer
- **OS**: Linux, Windows 10+, or macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for 8 streams)
- **Network**: Same network as Chromebooks

### Client Devices
**Chromebooks/Desktop:**
- **Browser**: Chrome, Edge, or Chromium-based
- **Network**: Same network as monitoring computer
- **Permissions**: Allow screen sharing when prompted

**Android Phones/Tablets:**
- **Browser**: Chrome (recommended) or other Chromium-based
- **OS**: Android 6.0 or higher
- **Network**: Same network as monitoring computer
- **Permissions**: Allow screen sharing or camera access when prompted

**iOS Devices (iPhone/iPad):**
- **Browser**: Safari (recommended)
- **OS**: iOS 11 or higher
- **Network**: Same network as monitoring computer
- **Permissions**: Allow camera access when prompted
- **Note**: iOS doesn't support browser-based screen capture; camera streaming is used instead

## Network Setup

All devices must be on the **same local network**:

1. **Check Your IP Address**
   - Linux/Mac: `ip addr` or `ifconfig`
   - Windows: `ipconfig`
   - Look for local IP (usually 192.168.x.x or 10.x.x.x)

2. **Firewall Settings**
   - Ensure port 8080 is open (for WebRTC/browser connections)
   - Ensure port 7000 is open (for AirPlay connections - Python implementation)
   - Ensure port 7100 is open (for UxPlay video mirroring)
   - Allow incoming connections for Python and UxPlay

3. **Test Connection**
   - On Chromebook, try pinging the monitoring computer
   - Or simply access the URL in a browser

## Troubleshooting

### Server Won't Start
- **Check if port 8080 is in use**: `lsof -i :8080` (Linux/Mac)
- **Try a different port**: Edit `server.py` and change port number
- **Check firewall settings**

### Device Can't Connect
- **Verify network**: Both devices on same WiFi/network
- **Check IP address**: Make sure you're using the correct IP
- **Firewall**: Temporarily disable to test
- **Browser compatibility**:
  - Desktop/Chromebook: Use Chrome or Edge
  - Android: Use Chrome browser
  - iOS: Use Safari browser

### No Video Appears
- **Check permissions**:
  - Desktop/Chromebook/Android: Allow screen sharing
  - iOS: Allow camera access
- **Try different browser**: Some browsers have better WebRTC support
- **Check console**: Open browser dev tools (F12 on desktop) for errors
- **Mobile-specific**:
  - Ensure HTTPS is being used or access via localhost
  - Check if browser has necessary permissions in device settings

### iOS Shows Camera Instead of Screen (Browser Method)
- **This is expected behavior for browser method**: iOS Safari does not support browser-based screen capture
- **Solution**: Use AirPlay screen mirroring instead (see "On iOS Devices (AirPlay Method)" in Usage Guide)
- **AirPlay provides true screen mirroring** from iOS devices without using the browser

### Streams are Laggy
- **Reduce active streams**: Try fewer simultaneous connections
- **Check network**: Ensure good WiFi signal
- **Close other apps**: Free up system resources
- **Lower resolution**: On Chromebook, reduce display resolution

### "Maximum Streams Reached"
- **Current limit**: 8 simultaneous streams
- **Disconnect unused**: Close connections from unused devices
- **Modify limit**: Edit `server.py` line 19 to change `max_streams`

## Mobile Device Support

The application now supports iPhone, iPad, and Android devices with intelligent fallback mechanisms:

### How It Works

**Automatic Device Detection:**
- The web interface detects your device type and adapts accordingly
- iOS devices automatically use camera streaming
- Android devices try screen capture first, fall back to camera if needed
- Desktop browsers use standard screen capture

**Capture Modes:**

1. **Screen Sharing** (Desktop, Chromebook, Android Chrome):
   - Captures the entire screen or selected window
   - Best for monitoring computer work
   - Uses WebRTC `getDisplayMedia()` API

2. **AirPlay Screen Mirroring** (iOS iPhone/iPad):
   - Native iOS screen mirroring via AirPlay protocol
   - Mirrors the entire device screen in real-time
   - No browser required, uses built-in iOS feature
   - Best quality and most reliable for iOS devices
   - Uses mDNS service discovery and AirPlay protocol

3. **Camera Streaming** (iOS browser fallback, other devices):
   - Uses device camera as video source
   - Automatically attempts to use back camera on mobile
   - Useful for showing physical work, whiteboards, etc.
   - Uses WebRTC `getUserMedia()` API

### Mobile Usage Tips

**Android Devices:**
- Use Chrome browser for best compatibility
- Screen capture works on Android 5.0+ with Chrome
- If screen capture isn't working, the app will automatically fall back to camera

**iOS Devices:**
- **Option 1: AirPlay Screen Mirroring via UxPlay (Recommended)**
  - Install UxPlay on the monitoring computer (see installation instructions above)
  - Provides true iOS screen mirroring with full video quality
  - Uses native iOS AirPlay protocol
  - No browser required - works directly from Control Center
  - Best quality and reliability
  - Automatically used if UxPlay is installed

- **Option 2: Browser Camera Streaming (Always Available Fallback)**
  - Use Safari browser (pre-installed)
  - iOS doesn't support browser-based screen capture, so camera is used
  - Grant camera permission when prompted
  - Point camera at screen or workspace you want to monitor
  - Works immediately, no UxPlay installation required
  - Access at http://<computer-ip>:8080

- **Option 3: Python AirPlay Infrastructure (Automatic Fallback)**
  - Used automatically if UxPlay is not installed
  - iOS devices can discover "Desktop Casting Receiver"
  - **Limitation**: Cryptographic authentication incomplete
  - Connection establishes but may not complete pairing
  - Mainly serves as mDNS service discovery

**Camera Streaming Tips:**
- Point camera at what you want to monitor (screen, whiteboard, workspace, etc.)
- Use a phone stand or holder for stable viewing
- Ensure good lighting for better video quality
- Back camera typically has better quality than front camera

## Advanced Configuration

### Change Maximum Streams
Edit `server.py`:
```python
stream_manager = StreamManager(max_streams=16)  # Change to desired number
```

### Change Port
Edit `server.py`:
```python
def run_server(host='0.0.0.0', port=9000):  # Change port
```

### Customize Grid Layout
Edit `viewer.py` in the `create_stream_grid()` method to change grid dimensions.

## Project Structure

```
reciever/
├── server.py                  # WebRTC server and stream management
├── viewer.py                  # GUI application
├── client.html                # Web interface for clients
├── airplay_receiver.py        # Python AirPlay receiver (fallback)
├── uxplay_integration.py      # UxPlay subprocess wrapper
├── run.py                     # Simple launcher script
├── requirements.txt           # Python dependencies
├── desktop_caster.spec        # PyInstaller configuration
├── build.sh                   # Linux/Mac build script
├── build.bat                  # Windows build script
├── build_windows_easy.ps1     # Windows easy build script
├── build_windows.ps1          # Windows PowerShell build script
├── install_uxplay.sh          # UxPlay installation script (Linux/Mac)
├── install_uxplay.ps1         # UxPlay installation script (Windows)
├── README.md                  # This file
└── INSTALL_UXPLAY.md          # UxPlay installation guide
```

## Security Considerations

⚠️ **Important**: This application is designed for **local network use only**.

- No authentication/encryption by default
- Only use on trusted networks
- Not suitable for public internet exposure
- For production use, implement:
  - TLS/HTTPS
  - Authentication
  - Access controls

## Development

### Running in Development Mode
```bash
# Terminal 1: Run server directly
python server.py

# Terminal 2: Run GUI
python viewer.py
```

### Testing
```bash
# Test with a single browser
# Open http://localhost:8080 in Chrome
```

## Dependencies

- **aiortc**: WebRTC implementation for Python
- **aiohttp**: Async HTTP server
- **opencv-python**: Video processing
- **Pillow**: Image handling
- **numpy**: Array operations
- **pyinstaller**: Executable packaging

## License

MIT License - Feel free to use and modify for your needs.

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Support

If you encounter issues:
1. Check the Troubleshooting section
2. Review console/terminal output for errors
3. Open an issue with detailed information

## Acknowledgments

Built with:
- [aiortc](https://github.com/aiortc/aiortc) - WebRTC implementation
- [aiohttp](https://github.com/aio-libs/aiohttp) - Web framework
- Python standard library

---

**Note**: This tool is designed for educational and monitoring purposes in controlled environments (classrooms, labs, etc.). Always ensure you have proper authorization before monitoring devices.
