# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop Casting Receiver is a Python application that allows Chromebooks to cast their desktop screens to a monitoring station over WebRTC. It can monitor up to 8 simultaneous screen streams in real-time using a tkinter GUI interface.

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

1. **server.py**: WebRTC server handling connections from Chromebooks
   - `StreamManager` class: Manages up to 8 simultaneous video streams with thread-safe access
   - `VideoFrameTrack` class: Processes incoming WebRTC video frames and converts them to numpy arrays
   - HTTP endpoints: `/offer` (WebRTC negotiation), `/disconnect`, `/status`, and `/` (serves client.html)
   - Runs on port 8080 by default with optional SSL support

2. **viewer.py**: Tkinter-based GUI monitoring application
   - Creates a 2x4 grid layout for displaying up to 8 streams
   - Imports and uses the `stream_manager` from server.py
   - Runs the server in a background thread when "Start Server" is clicked
   - Updates stream displays at ~10 FPS using tkinter's `.after()` method

3. **client.html**: Web interface for Chromebooks
   - Served by the aiohttp server at the root endpoint
   - Uses WebRTC's getDisplayMedia() API for screen capture
   - Handles WebRTC peer connection negotiation with the server

4. **run.py**: Simple launcher script that imports and runs viewer.main()

### Data Flow

```
Chromebook (client.html) → WebRTC → server.py (StreamManager) → viewer.py (GUI)
                                          ↓
                                    numpy frames stored in
                                    thread-safe dictionary
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

Build dependency:
- **pyinstaller** (6.3.0): Creates standalone executables

## Important Implementation Details

### Frame Updates
- Frames are captured in `VideoFrameTrack.recv()` at line 79-88 in server.py
- Each frame is converted to BGR24 numpy array using `frame.to_ndarray(format="bgr24")`
- Frames are displayed in the GUI at approximately 10 FPS (configurable at viewer.py:323)

### Client-Server Communication
- WebRTC peer connection is established via HTTP POST to `/offer` endpoint
- Each client generates a unique `client_id` and provides a `client_name`
- Server returns SDP answer to complete WebRTC negotiation

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
- client.html and server.py as data files
- All hidden imports for aiortc, aiohttp, av, opencv, numpy, PIL, websockets

When building, ensure all dependencies are installed in the virtual environment first.

## Network Requirements

- All devices must be on the same local network
- Port 8080 must be accessible (check firewall settings)
- For HTTPS, clients must accept self-signed certificate warnings
