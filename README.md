# Desktop Casting Receiver

A Python application that allows Chromebooks to cast their desktop screens to a monitoring station. Monitor up to 8 simultaneous screen streams in real-time.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Multi-Stream Support**: Monitor up to 8 Chromebooks simultaneously
- **WebRTC Technology**: Low-latency, real-time screen streaming
- **User-Friendly Interface**:
  - Clean web interface for Chromebooks
  - Professional GUI viewer with grid layout
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Standalone Executable**: Can be packaged as a single executable

## Architecture

```
┌─────────────────┐
│   Chromebook 1  │────┐
└─────────────────┘    │
                       │
┌─────────────────┐    │      ┌──────────────────┐      ┌─────────────┐
│   Chromebook 2  │────┼─────>│  WebRTC Server   │─────>│  GUI Viewer │
└─────────────────┘    │      │  (Python/aiortc) │      │  (tkinter)  │
                       │      └──────────────────┘      └─────────────┘
┌─────────────────┐    │              ↑
│   Chromebook 3  │────┘         Runs on your
└─────────────────┘            monitoring computer
      ...
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

4. **Connect Chromebooks**
   - On each Chromebook, open a browser
   - Navigate to `http://<your-computer-ip>:8080`
   - Enter a device name
   - Click "Start Sharing Screen"
   - Select which screen to share

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

### On Chromebooks

1. **Open Browser**
   - Chrome, Edge, or any Chromium-based browser

2. **Navigate to Server**
   - Go to `http://<monitoring-computer-ip>:8080`

3. **Start Sharing**
   - Enter a descriptive name (e.g., "Student 1", "Lab Station 3")
   - Click "Start Sharing Screen"
   - Select the screen you want to share
   - Click "Share"

4. **Verify Connection**
   - You should see "Connected!" message
   - Your screen should appear on the monitoring station

5. **Stop Sharing**
   - Click "Stop Sharing" button
   - Or close the browser tab

## System Requirements

### Monitoring Computer
- **OS**: Linux, Windows 10+, or macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for 8 streams)
- **Network**: Same network as Chromebooks

### Chromebooks
- **Browser**: Chrome, Edge, or Chromium-based
- **Network**: Same network as monitoring computer
- **Permissions**: Allow screen sharing when prompted

## Network Setup

All devices must be on the **same local network**:

1. **Check Your IP Address**
   - Linux/Mac: `ip addr` or `ifconfig`
   - Windows: `ipconfig`
   - Look for local IP (usually 192.168.x.x or 10.x.x.x)

2. **Firewall Settings**
   - Ensure port 8080 is open
   - Allow incoming connections for Python

3. **Test Connection**
   - On Chromebook, try pinging the monitoring computer
   - Or simply access the URL in a browser

## Troubleshooting

### Server Won't Start
- **Check if port 8080 is in use**: `lsof -i :8080` (Linux/Mac)
- **Try a different port**: Edit `server.py` and change port number
- **Check firewall settings**

### Chromebook Can't Connect
- **Verify network**: Both devices on same WiFi/network
- **Check IP address**: Make sure you're using the correct IP
- **Firewall**: Temporarily disable to test
- **Browser**: Use Chrome or Edge (other browsers may not support screen sharing API)

### No Video Appears
- **Check permissions**: Chromebook must allow screen sharing
- **Try different browser**: Some browsers have better WebRTC support
- **Check console**: Open browser dev tools (F12) for errors

### Streams are Laggy
- **Reduce active streams**: Try fewer simultaneous connections
- **Check network**: Ensure good WiFi signal
- **Close other apps**: Free up system resources
- **Lower resolution**: On Chromebook, reduce display resolution

### "Maximum Streams Reached"
- **Current limit**: 8 simultaneous streams
- **Disconnect unused**: Close connections from unused devices
- **Modify limit**: Edit `server.py` line 19 to change `max_streams`

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
├── server.py              # WebRTC server and stream management
├── viewer.py              # GUI application
├── client.html            # Web interface for Chromebooks
├── run.py                 # Simple launcher script
├── requirements.txt       # Python dependencies
├── desktop_caster.spec    # PyInstaller configuration
├── build.sh              # Linux/Mac build script
├── build.bat             # Windows build script
└── README.md             # This file
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
