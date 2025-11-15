# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop Casting Receiver is a Python application that allows Chromebooks, iPhones, Android phones, and other devices to cast their screens (or camera) to a monitoring station over WebRTC. It can monitor up to 8 simultaneous video streams in real-time using a tkinter GUI interface.

## Common Commands

### Running the Application

```bash
# Run from source (recommended for development)
python run.py

# Or run the GUI directly
python viewer.py

# Or run just the server
python server.py
```

### Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Building Executables

```bash
# Linux/macOS
./build.sh

# Windows
build.bat
```

The executable will be created in `dist/DesktopCastingReceiver/`.

### Running in Development Mode

```bash
# Terminal 1: Run server directly
python server.py

# Terminal 2: Run GUI
python viewer.py
```

## Architecture

### Core Components

1. **server.py**: WebRTC server handling connections from all devices
   - `StreamManager` class: Manages up to 8 simultaneous video streams with thread-safe access
   - `VideoFrameTrack` class: Processes incoming WebRTC video frames and converts them to numpy arrays
   - HTTP endpoints: `/offer` (WebRTC negotiation), `/disconnect`, `/status`, and `/` (serves client.html)
   - Runs on port 8080 by default with optional SSL support

2. **viewer.py**: Tkinter-based GUI monitoring application
   - Creates a 2x4 grid layout for displaying up to 8 streams
   - Imports and uses the `stream_manager` from server.py
   - Runs the server in a background thread when "Start Server" is clicked
   - Updates stream displays at ~10 FPS using tkinter's `.after()` method

3. **client.html**: Web interface for Chromebooks, mobile devices, and browsers
   - Served by the aiohttp server at the root endpoint
   - Detects device type (desktop, Android, iOS) and adapts UI accordingly
   - Uses WebRTC's getDisplayMedia() API for screen capture on supported devices
   - Falls back to getUserMedia() camera streaming on iOS and devices without screen capture support
   - Mobile-responsive design with touch-friendly controls

4. **airplay_receiver.py**: Python AirPlay receiver (fallback implementation)
   - Advertises as AirPlay target using mDNS/Bonjour (zeroconf library)
   - Accepts AirPlay connections from iOS devices (iPhone, iPad)
   - Runs on port 7000 by default
   - **Limitation**: Cryptographic authentication incomplete
   - Used as fallback when UxPlay is not available

5. **uxplay_integration.py**: UxPlay subprocess wrapper (recommended for iOS)
   - Wraps UxPlay (C/C++ AirPlay server) as Python subprocess
   - Provides actual working iOS screen mirroring
   - Monitors UxPlay stdout for connection events
   - Creates streams in StreamManager when iOS devices connect
   - Automatically used if UxPlay is installed on the system
   - Falls back gracefully to Python AirPlay or camera streaming

6. **run.py**: Simple launcher script that imports and runs viewer.main()

### Data Flow

```
Desktop/Chromebook (screen) ─┐
                             │
Android (screen/camera) ─────┼──> WebRTC ──> server.py (StreamManager) ──> viewer.py (GUI)
                             │                         ↓
iOS (browser camera) ────────┤                  numpy frames stored in
                             │                  thread-safe dictionary
iOS (AirPlay via UxPlay) ────┤                         ↑
                             │                        │
                             │                   ┌────┴─────┐
                             │                   │          │
                             └────────> uxplay_integration.py  airplay_receiver.py
                                       (subprocess wrapper)    (Python fallback)
                                              ↓                        ↓
                                          UxPlay binary            mDNS only
                                        (real mirroring)        (incomplete)
```

### Key Design Patterns

- **Shared State**: `viewer.py` imports `stream_manager` directly from `server.py` to access stream data
- **Thread Safety**: StreamManager uses `threading.Lock()` to protect concurrent access to the streams dictionary
- **Async Server**: Server runs using aiohttp and asyncio with WebRTC connections managed by aiortc
- **Frame Processing**: Video frames are converted from WebRTC format to numpy arrays (BGR24) and stored in the StreamManager

### Stream Management

- Streams are stored in `StreamManager.streams` dictionary: `{client_id: {'frame': np.array, 'name': str, 'timestamp': float}}`
- Maximum streams is configurable (default: 8) in `server.py` line 67
- Each stream slot in the GUI corresponds to a client_id in sorted order
- Disconnections are handled via WebRTC connection state changes

## Configuration

### Changing Maximum Streams

Edit `server.py` line 67:
```python
stream_manager = StreamManager(max_streams=16)  # Change to desired number
```

Then update the viewer grid layout in `viewer.py` method `create_stream_grid()` (lines 124-172) to match the new grid dimensions.

### Changing Server Port

Edit `server.py` line 214:
```python
def run_server(host='0.0.0.0', port=9000, use_ssl=True):  # Change port
```

Also update `viewer.py` line 185 where the server thread is started.

### SSL/HTTPS Configuration

The server supports optional SSL. To enable:
1. Generate self-signed certificates: `cert.pem` and `key.pem` in the project root
2. The server automatically detects and uses them if present
3. Clients must accept the self-signed certificate warning in the browser

## Dependencies

Main runtime dependencies (see requirements.txt):
- **aiortc** (1.6.0): WebRTC implementation for Python
- **aiohttp** (3.9.1): Async HTTP server framework
- **opencv-python** (4.8.1.78): Video frame processing
- **Pillow** (10.1.0): Image handling and conversion for tkinter
- **numpy** (1.24.3): Array operations for video frames
- **av** (11.0.0): Python bindings for FFmpeg (used by aiortc)
- **websockets** (12.0): WebSocket support
- **zeroconf** (0.132.2): mDNS/Bonjour service discovery for AirPlay

Build dependency:
- **pyinstaller** (6.3.0): Creates standalone executables

## Important Implementation Details

### Frame Updates
- Frames are captured in `VideoFrameTrack.recv()` at line 79-88 in server.py
- Each frame is converted to BGR24 numpy array using `frame.to_ndarray(format="bgr24")`
- Frames are displayed in the GUI at approximately 10 FPS (configurable at viewer.py:323)

### Client-Server Communication
- WebRTC peer connection is established via HTTP POST to `/offer` endpoint
- Each client generates a unique `client_id` and provides a `client_name` and `capture_mode`
- Server returns SDP answer to complete WebRTC negotiation
- Capture mode can be 'screen' or 'camera' depending on device capabilities

### Mobile Device Support
The application now supports iOS and Android devices through intelligent device detection and fallback mechanisms:

**Device Detection** (client.html:186-193):
- Detects mobile devices using user agent string
- Specifically identifies iOS devices for special handling
- Adapts UI text and functionality based on device type

**Capture Methods**:
1. **Screen Capture** (Desktop, Chromebooks, Android Chrome):
   - Uses `getDisplayMedia()` API
   - Captures the entire screen or selected window
   - Best quality and most appropriate for monitoring

2. **Camera Fallback** (iOS Safari, devices without screen capture):
   - Uses `getUserMedia()` API with video constraints
   - Attempts to use back camera (`facingMode: 'environment'`)
   - Automatically used when screen capture is not available
   - Clearly indicates "Camera Streaming" mode to the user

**Implementation Flow** (client.html:211-337):
1. Try `getDisplayMedia()` first (skipped on iOS)
2. If unavailable or user denies, fall back to `getUserMedia()`
3. Display appropriate UI feedback about capture mode
4. Send `capture_mode` parameter to server for tracking

### AirPlay Support for iOS
The application now includes native AirPlay receiver functionality for true iOS screen mirroring:

**Architecture** (airplay_receiver.py):
- `AirPlayReceiver` class manages the entire AirPlay stack
- Uses `zeroconf` library for mDNS/Bonjour service advertisement
- Advertises as `_airplay._tcp.local.` service type
- Pretends to be an Apple TV for maximum iOS compatibility
- Runs async server on port 7000

**Service Discovery**:
- Advertises with feature flags: `0x5A7FFFF7,0x1E` (screen mirroring supported)
- Includes device ID, model (AppleTV3,2), and version information
- iOS devices discover it automatically in Screen Mirroring menu

**Connection Handling** (airplay_receiver.py:132-232):
- Accepts HTTP-style requests on port 7000
- Handles `/stream` endpoint for video data
- Handles `/reverse` endpoint for event communication
- Creates placeholder frames with device info
- Full H.264 decoding would be needed for production use

**Integration**:
- Started automatically in `server.py:run_server()` when `enable_airplay=True`
- Gracefully degrades if `zeroconf` not installed
- Shares the same `StreamManager` instance as WebRTC streams
- AirPlay streams appear with "AirPlay: [device name]" prefix in GUI

**Current Limitations**:
- **Cryptographic authentication incomplete**: AirPlay requires real SRP-6a and Ed25519 protocols
- iOS can discover the receiver but won't complete pairing handshake
- Random dummy data fails iOS's cryptographic validation
- Full implementation would require:
  - Real SRP-6a protocol implementation (~1000 lines)
  - Real Ed25519 key exchange (~500 lines)
  - ChaCha20-Poly1305 encryption for video stream
  - H.264 video decoder
- Infrastructure is complete and ready for proper crypto implementation
- **SOLVED**: Use UxPlay integration instead (see below)

### UxPlay Integration for iOS Screen Mirroring

The application now includes UxPlay integration to provide actual working iOS screen mirroring:

**Implementation** (uxplay_integration.py):
- `UxPlayIntegration` class wraps UxPlay C/C++ binary as subprocess
- Uses `shutil.which('uxplay')` to detect if UxPlay is installed
- Starts UxPlay with command: `uxplay -n "Desktop Casting Receiver" -p -reset 5`
- Monitors stdout using regex patterns for connection events:
  - `Authenticated\s+([^\s]+)` - detects device name
  - `raop_rtp_mirror starting mirroring` - detects connection start
  - `raop_rtp_mirror.*stopped` - detects disconnection

**Connection Flow**:
1. UxPlay subprocess started in background thread
2. iOS device discovers "Desktop Casting Receiver" via mDNS
3. User selects it from iOS Control Center → Screen Mirroring
4. UxPlay handles all AirPlay protocol (SRP, encryption, H.264)
5. Python monitor thread detects "Authenticated" in stdout
6. Creates stream in StreamManager with device name
7. Updates frames (currently placeholders, GStreamer needed for real frames)

**Fallback Logic** (server.py:290-333):
```python
if enable_airplay:
    # Try UxPlay first
    try:
        uxplay = UxPlayIntegration(stream_manager)
        if uxplay.is_uxplay_available() and uxplay.start():
            # UxPlay working - best option
    except:
        # Fall back to Python AirPlay (mDNS only)
        airplay_receiver = AirPlayReceiver(stream_manager)
        airplay_receiver.start()
```

**Advantages**:
- Uses proven C/C++ implementation (UxPlay)
- Handles all cryptographic requirements correctly
- Works with iOS 9+
- No Python crypto library dependencies
- Falls back gracefully if UxPlay not installed

**Current Status**:
- Subprocess integration: ✅ Complete
- Connection detection: ✅ Complete
- StreamManager integration: ✅ Complete
- Frame capture: ⚠️ Placeholder (GStreamer pipeline needed for actual video)
- Fallback logic: ✅ Complete

**Future Enhancement**:
To capture actual video frames from UxPlay, integrate GStreamer pipeline:
```python
# In _update_frames(), replace placeholder with:
pipeline = f"uxplay ... ! videoconvert ! appsink"
# Use opencv to capture from appsink
```

### Module Import Pattern
The viewer imports server functionality using:
```python
spec = importlib.util.spec_from_file_location("server", "server.py")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)
stream_manager = server_module.stream_manager
```
This allows viewer.py to access the same StreamManager instance that the server thread uses.

## PyInstaller Packaging

The `desktop_caster.spec` file bundles:
- viewer.py as the entry point
- client.html, server.py, airplay_receiver.py, and uxplay_integration.py as data files
- All hidden imports for aiortc, aiohttp, av, opencv, numpy, PIL, websockets, zeroconf

When building, ensure all dependencies are installed in the virtual environment first.

**Note on UxPlay**: UxPlay is an external binary and must be installed separately on the system. The Python executable will detect it at runtime using `shutil.which('uxplay')`.

## Network Requirements

- All devices must be on the same local network
- Port 8080 must be accessible for WebRTC/browser connections (check firewall settings)
- Port 7000 must be accessible for Python AirPlay receiver (fallback mode)
- Port 7100 must be accessible for UxPlay video mirroring (if UxPlay is installed)
- mDNS/Bonjour must be enabled on the network for AirPlay device discovery
- For HTTPS, clients must accept self-signed certificate warnings

## Testing UxPlay Integration

To verify UxPlay integration works:

1. **Install UxPlay** (see README.md for platform-specific instructions)
2. **Verify installation**: `uxplay -h` should show help text
3. **Run the application**: `python run.py` or use the built executable
4. **Check logs**: Should see "✓ UxPlay started successfully" message
5. **Test iOS connection**: Open Control Center → Screen Mirroring → Select "Desktop Casting Receiver"
6. **Verify stream appears**: Check that iOS device stream shows in GUI grid

If UxPlay is not installed, the application will automatically fall back to camera streaming via the web interface.
