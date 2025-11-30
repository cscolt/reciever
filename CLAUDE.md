# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop Casting Receiver is a Python application that allows Chromebooks, iPhones, Android phones, and other devices to cast their screens (or camera) to a monitoring station. It supports multiple connection methods:
- **WebRTC**: Direct browser-based screen/tab/camera sharing
- **Google Cast**: Native Cast protocol for managed devices (appears in Chrome Cast menu)
- **AirPlay**: iOS screen mirroring via UxPlay or pure Python implementation

The application can monitor up to 8 simultaneous video streams in real-time using a tkinter GUI interface.

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

4. **airplay_receiver.py**: Complete pure Python AirPlay receiver implementation
   - Advertises as AirPlay target using mDNS/Bonjour (zeroconf library)
   - Accepts AirPlay connections from iOS devices (iPhone, iPad)
   - Implements real SRP-6a authentication using srp library
   - Implements real Ed25519 key exchange using cryptography library
   - Implements real ChaCha20-Poly1305 encryption/decryption
   - Implements H.264 video decoding using PyAV (av library)
   - Runs on port 7000 by default
   - No external binaries required - all dependencies installable via pip
   - Used alongside or as fallback when UxPlay is not available

5. **uxplay_integration.py**: UxPlay subprocess wrapper (recommended for iOS)
   - Wraps UxPlay (C/C++ AirPlay server) as Python subprocess
   - Provides actual working iOS screen mirroring
   - Monitors UxPlay stdout for connection events
   - Creates streams in StreamManager when iOS devices connect
   - Automatically used if UxPlay is installed on the system
   - Falls back gracefully to Python AirPlay or camera streaming

6. **run.py**: Simple launcher script that imports and runs viewer.main()

7. **cast_receiver.html**: Google Cast Web Receiver application
   - Implements Google Cast SDK for Cast protocol support
   - Handles Cast session management and custom namespaces
   - Coordinates with senders to establish WebRTC connections
   - Integrates Cast streams into StreamManager via WebRTC
   - Allows managed Chromebooks to cast without URL restrictions
   - URL: `/cast_receiver` (registered with Google Cast Developer Console)

8. **cast_sender.html**: Google Cast sender application for testing
   - Implements Google Cast Sender SDK
   - Allows manual Cast connections for testing
   - Sets up WebRTC screen/tab capture
   - Communicates with receiver via Cast custom namespaces
   - URL: `/cast_sender` (for testing Cast functionality)

9. **cast_discovery.py**: mDNS advertiser for Google Cast discovery
   - Advertises receiver as `_googlecast._tcp.local.` service
   - Makes receiver appear in Chrome/Android Cast menus
   - Uses zeroconf library for mDNS/Bonjour
   - Provides device ID, capabilities, and receiver URL
   - Automatically started with server when `enable_cast=True`

10. **mdns_discovery.py**: Generic mDNS advertiser for WebRTC discovery
    - Advertises receiver for direct WebRTC connections
    - Separate from Cast discovery (different service types)
    - Helps Chromebooks discover receiver without manual URL entry

### Data Flow

```
Desktop/Chromebook (WebRTC URL) ─────┐
                                     │
Desktop/Chromebook (Cast button) ────┼──> Cast Protocol ──┐
                                     │                     │
Android (WebRTC URL) ────────────────┤                     ├─> WebRTC ──> server.py
                                     │                     │              (StreamManager)
Android (Cast button) ───────────────┼──> Cast Protocol ──┘                   │
                                     │                                         ↓
iOS (browser camera) ────────────────┤                              numpy frames stored
                                     │                              in thread-safe dict
iOS (AirPlay) ───────────────────────┤                                         │
                                     │                                         │
                                     └────────────────────────────────────> viewer.py
                                                                              (GUI)

Cast Discovery Flow:
─────────────────────
cast_discovery.py ──> mDNS (_googlecast._tcp) ──> Chrome/Android ──> User clicks Cast
                                                                   ──> Selects receiver
                                                                   ──> Cast session starts
                                                                   ──> WebRTC negotiation
                                                                   ──> Video stream

AirPlay Flow:
────────────
uxplay_integration.py ──> UxPlay binary ──> mDNS (_airplay._tcp) ──> iOS discovers
     (or)                                                           ──> User mirrors
airplay_receiver.py ──────────────────────> mDNS (_airplay._tcp) ──> Encrypted stream
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
- **av** (11.0.0): Python bindings for FFmpeg (used by aiortc and H.264 decoding)
- **websockets** (12.0): WebSocket support
- **zeroconf** (0.132.2): mDNS/Bonjour service discovery for AirPlay
- **srp** (1.0.20): SRP-6a authentication protocol for AirPlay
- **cryptography** (41.0.7): Ed25519, ChaCha20-Poly1305, and HKDF for AirPlay encryption

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
The application includes a complete pure Python AirPlay receiver implementation with real cryptography for true iOS screen mirroring:

**Architecture** (airplay_receiver.py):
- `AirPlayReceiver` class manages the entire AirPlay stack
- `AirPlayCrypto` class handles all cryptographic operations (lines 95-368)
- `H264Decoder` class decodes video frames using PyAV (lines 371-425)
- Uses `zeroconf` library for mDNS/Bonjour service advertisement
- Advertises as `_airplay._tcp.local.` service type
- Pretends to be an Apple TV for maximum iOS compatibility
- Runs async server on port 7000

**Service Discovery**:
- Advertises with feature flags: `0x5A7FFFF7,0x1E` (screen mirroring supported)
- Includes device ID, model (AppleTV3,2), and version information
- Real Ed25519 public key for pairing
- iOS devices discover it automatically in Screen Mirroring menu

**Cryptographic Implementation**:
1. **SRP-6a Authentication** (airplay_receiver.py:714-767):
   - Uses `srp` library for password-authenticated key exchange
   - Handles M1->M2 and M3->M4 handshake states
   - Establishes initial trust between devices

2. **Ed25519 Key Exchange** (airplay_receiver.py:769-830):
   - Uses `cryptography` library for Curve25519 ECDH
   - Exchanges public keys and computes shared secret
   - Signs data to verify authenticity

3. **ChaCha20-Poly1305 Encryption** (airplay_receiver.py:269-348):
   - Encrypts/decrypts video stream data
   - Uses AEAD for authenticated encryption
   - Derives keys using HKDF-SHA512

4. **H.264 Video Decoding** (airplay_receiver.py:387-417):
   - Uses PyAV (`av` library) to decode video frames
   - Converts H.264 NAL units to numpy arrays
   - Real-time frame processing for display

**Connection Handling**:
- Accepts HTTP-style requests on port 7000
- Handles `/info`, `/server-info`, `/pair-setup`, `/pair-verify` endpoints
- Handles `/stream` endpoint for encrypted video data
- Handles `/reverse` endpoint for event communication
- Decrypts and decodes H.264 frames in real-time

**Integration**:
- Started automatically in `server.py:run_server()` when `enable_airplay=True`
- Checks for all dependencies and provides graceful fallbacks
- Shares the same `StreamManager` instance as WebRTC streams
- AirPlay streams appear with "AirPlay: [device name]" prefix in GUI

**Implementation Status**:
- ✅ Real SRP-6a authentication (using `srp` library)
- ✅ Real Ed25519 key exchange (using `cryptography` library)
- ✅ Real ChaCha20-Poly1305 encryption/decryption
- ✅ Real H.264 video decoder (using `av`/PyAV library)
- ✅ Complete pure Python implementation (no external binaries required)
- ✅ All dependencies installable via pip
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

### Google Cast Support for Managed Chromebooks/Android

The application includes full Google Cast protocol support to allow managed devices (with URL restrictions) to cast via the native Cast button:

**Architecture** (cast_receiver.html, cast_sender.html, cast_discovery.py):
- Cast receiver implements Google Cast Web Receiver SDK
- Cast sender provides testing interface for manual connections
- Cast discovery advertises receiver as `_googlecast._tcp.local.` service
- Uses Cast custom namespaces for WebRTC coordination
- Integrates seamlessly with existing StreamManager

**Why Google Cast Support?**:
- **Managed Devices**: Many schools/enterprises block arbitrary URL access but allow Cast
- **Native Integration**: Appears in Chrome's Cast button menu (no URL to type)
- **User Familiarity**: Users already know how to use Cast button
- **Multiple Protocols**: Works alongside WebRTC and AirPlay, not replacing them

**Connection Flow**:
1. `cast_discovery.py` advertises receiver via mDNS
2. Chrome/Android discovers "Desktop Casting Receiver" in Cast menu
3. User clicks Cast button → Screen Mirroring → Selects receiver
4. Cast SDK establishes session with receiver
5. Cast custom namespace coordinates WebRTC offer/answer
6. WebRTC handles actual video streaming
7. Stream appears in StreamManager alongside other streams

**Implementation Details** (cast_receiver.html:180-360):
- Initializes Cast Receiver SDK with `cast.framework.CastReceiverContext`
- Configures custom namespace: `urn:x-cast:com.desktop.casting.screenmirror`
- Handles Cast sender connections/disconnections
- Receives WebRTC offer via Cast messages
- Creates WebRTC peer connection and sends answer back
- Each Cast sender gets independent stream in StreamManager

**Discovery Details** (cast_discovery.py:45-95):
- Advertises as Google Cast device using zeroconf
- Service type: `_googlecast._tcp.local.`
- Properties include:
  - Device ID (UUID)
  - Friendly name ("Desktop Casting Receiver")
  - Capabilities (video/audio output, screen mirroring)
  - Receiver URL (for Google Cast Console registration)
- Automatically started when `enable_cast=True` in `server.py`

**Setup Requirements**:
1. Register application at https://cast.google.com/publish/
2. Provide receiver URL: `http://YOUR_IP:8080/cast_receiver`
3. Get Application ID (e.g., `ABCD1234`)
4. For testing: Register device serial numbers
5. For production: Submit app for review

**URL Endpoints**:
- `/cast_receiver` - Cast Web Receiver (registered with Google)
- `/cast_sender` - Cast sender page for manual testing
- Both integrate with existing `/offer` WebRTC endpoint

**Integration with Server** (server.py:333-348):
```python
if enable_cast:
    from cast_discovery import CastDiscovery
    cast_discovery = CastDiscovery("Desktop Casting Receiver", port, protocol)
    cast_discovery.start()
    # Receiver now appears in Cast menus
```

**Advantages**:
- Works on URL-restricted managed Chromebooks
- Native Cast button integration
- No URL to remember or type
- Supports multiple simultaneous Cast sessions
- Falls back gracefully if Cast not needed

**Limitations**:
- Requires Google Cast registration (one-time, free)
- Needs same network connectivity as WebRTC
- Testing requires device serial number registration
- Production requires Google approval (1-3 days)

**Documentation**:
- Complete setup guide: `CAST_SETUP.md`
- Includes troubleshooting, network requirements, and deployment examples
- Step-by-step registration and testing instructions

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
- HTML files: client.html, cast_receiver.html, cast_sender.html
- Python modules: server.py, airplay_receiver.py, uxplay_integration.py, mdns_discovery.py, cast_discovery.py
- All hidden imports for aiortc, aiohttp, av, opencv, numpy, PIL, websockets, zeroconf

When building, ensure all dependencies are installed in the virtual environment first.

**Note on UxPlay**: UxPlay is an external binary and must be installed separately on the system. The Python executable will detect it at runtime using `shutil.which('uxplay')`.

## Network Requirements

- All devices must be on the same local network (or same VLAN)
- **Port 8080/TCP** must be accessible for HTTP/WebRTC/Cast connections (check firewall)
- **Port 7000/TCP** must be accessible for Python AirPlay receiver (fallback mode)
- **Port 7100/TCP** must be accessible for UxPlay video mirroring (if UxPlay installed)
- **Port 5353/UDP** must be open for mDNS/Bonjour discovery (AirPlay and Cast)
- **WebRTC ports**: Ephemeral UDP ports for media streaming
- **mDNS/Bonjour** must be enabled on the network:
  - Required for AirPlay device discovery
  - Required for Google Cast device discovery
  - Often blocked in enterprise networks - work with IT to allowlist
- For HTTPS, clients must accept self-signed certificate warnings

**Cast-Specific Requirements**:
- Same network/VLAN for Cast discovery
- mDNS must not be blocked by firewall
- For managed devices: Cast App ID may need to be allowlisted in MDM
- For testing: Device serial numbers must be registered in Google Cast Console

## Testing Google Cast Integration

To verify Google Cast integration works:

1. **Start the server**: `python run.py` or use the built executable
2. **Check logs**: Should see "✓ Google Cast discovery enabled" message
3. **Note the receiver URL**: Copy the Cast receiver URL from logs (e.g., `http://192.168.1.100:8080/cast_receiver`)
4. **Register with Google**:
   - Visit https://cast.google.com/publish/
   - Create new Custom Receiver application
   - Use the receiver URL from step 3
   - Get your Application ID
   - Add test device serial numbers
5. **Test from Chrome**:
   - On Chromebook or Chrome browser (same network as server)
   - Click Cast button in Chrome toolbar (⏏️ icon)
   - Should see "Desktop Casting Receiver" in the list
   - Select it and choose "Cast tab" or "Cast screen"
   - Stream should appear in GUI
6. **Alternative test using Cast sender page**:
   - Visit `http://YOUR_SERVER_IP:8080/cast_sender`
   - Enter your Application ID
   - Click "Initialize Cast SDK"
   - Click "Start Casting"
   - Select screen/window/tab to share

If Cast discovery fails, check firewall settings and ensure port 5353/UDP is open for mDNS.

## Testing UxPlay Integration

To verify UxPlay integration works:

1. **Install UxPlay** (see README.md for platform-specific instructions)
2. **Verify installation**: `uxplay -h` should show help text
3. **Run the application**: `python run.py` or use the built executable
4. **Check logs**: Should see "✓ UxPlay started successfully" message
5. **Test iOS connection**: Open Control Center → Screen Mirroring → Select "Desktop Casting Receiver"
6. **Verify stream appears**: Check that iOS device stream shows in GUI grid

If UxPlay is not installed, the application will automatically fall back to camera streaming via the web interface.
