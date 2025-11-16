#!/usr/bin/env python3
"""
Desktop Casting Receiver Server
Handles WebRTC connections from Chromebooks and manages screen streaming
Supports AirPlay mirroring from iOS devices
"""

import asyncio
import json
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import numpy as np
from threading import Lock
import time
import ssl
import os
import sys

# Enhanced logging with DEBUG level
# Set to DEBUG for detailed troubleshooting, INFO for normal operation
LOG_LEVEL = os.getenv('DEBUG', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances (will be initialized in run_server)
airplay_receiver = None
uxplay_integration = None
mdns_advertiser = None

# Helper function to get base path (works in both dev and PyInstaller)
def get_base_path():
    """Get base path for bundled files, handling PyInstaller bundled mode"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - return _MEIPASS for bundled files
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

def get_executable_dir():
    """Get directory where executable/script is located (for user files like certs)"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - return exe directory
        return os.path.dirname(sys.executable)
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))


class StreamManager:
    """Manages multiple incoming video streams"""

    def __init__(self, max_streams=8):
        self.max_streams = max_streams
        self.streams = {}  # {client_id: {'frame': np.array, 'name': str, 'timestamp': float}}
        self.lock = Lock()
        self.pcs = {}  # {client_id: RTCPeerConnection}

    def add_stream(self, client_id, name_or_frame, name=None):
        """
        Add a new stream. Supports two signatures:
        - add_stream(client_id, name) for WebRTC streams
        - add_stream(client_id, frame, name) for AirPlay streams
        """
        with self.lock:
            if len(self.streams) >= self.max_streams:
                return False

            # Determine if this is WebRTC (name_or_frame is string) or AirPlay (name_or_frame is frame)
            if isinstance(name_or_frame, str):
                # WebRTC style: add_stream(client_id, name)
                self.streams[client_id] = {
                    'frame': None,
                    'name': name_or_frame,
                    'timestamp': time.time()
                }
            else:
                # AirPlay style: add_stream(client_id, frame, name)
                self.streams[client_id] = {
                    'frame': name_or_frame,
                    'name': name if name else 'AirPlay Device',
                    'timestamp': time.time()
                }
            return True

    def update_frame(self, client_id, frame):
        """Update frame for a stream (WebRTC interface)"""
        with self.lock:
            if client_id in self.streams:
                self.streams[client_id]['frame'] = frame
                self.streams[client_id]['timestamp'] = time.time()

    def update_stream(self, client_id, frame):
        """Update frame for a stream (AirPlay interface - alias for update_frame)"""
        self.update_frame(client_id, frame)

    def remove_stream(self, client_id):
        with self.lock:
            if client_id in self.streams:
                del self.streams[client_id]
            if client_id in self.pcs:
                del self.pcs[client_id]

    def get_all_streams(self):
        with self.lock:
            return {k: v.copy() for k, v in self.streams.items()}

    def get_stream_count(self):
        with self.lock:
            return len(self.streams)


# Global stream manager
stream_manager = StreamManager(max_streams=8)


class VideoFrameTrack(VideoStreamTrack):
    """Custom video track that processes incoming frames"""

    def __init__(self, track, client_id, stream_manager):
        super().__init__()
        self.track = track
        self.client_id = client_id
        self.stream_manager = stream_manager

    async def recv(self):
        frame = await self.track.recv()

        # Convert frame to numpy array
        img = frame.to_ndarray(format="bgr24")

        # Update the stream manager with the new frame
        self.stream_manager.update_frame(self.client_id, img)

        return frame


async def offer(request):
    """Handle WebRTC offer from client"""
    params = await request.json()
    offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    client_id = params.get("client_id")
    client_name = params.get("client_name", f"Client {client_id[:8]}")

    logger.info(f"Received offer from {client_name} ({client_id})")

    # Check if we can accept more streams
    if not stream_manager.add_stream(client_id, client_name):
        return web.Response(
            content_type="application/json",
            text=json.dumps({"error": "Maximum streams reached"}),
            status=503
        )

    # Create peer connection
    pc = RTCPeerConnection()
    stream_manager.pcs[client_id] = pc

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state for {client_name}: {pc.connectionState}")
        if pc.connectionState in ["failed", "closed"]:
            stream_manager.remove_stream(client_id)
            await pc.close()

    @pc.on("track")
    async def on_track(track):
        logger.info(f"Received track from {client_name}: {track.kind}")
        if track.kind == "video":
            # Wrap the track to process frames
            video_track = VideoFrameTrack(track, client_id, stream_manager)

            # Create a task to consume the track and process frames
            async def consume_track():
                try:
                    while True:
                        await video_track.recv()
                except Exception as e:
                    logger.info(f"Track ended for {client_name}: {e}")
                    stream_manager.remove_stream(client_id)

            # Start consuming frames
            asyncio.create_task(consume_track())

            # Keep track alive
            @track.on("ended")
            async def on_ended():
                logger.info(f"Track ended for {client_name}")
                stream_manager.remove_stream(client_id)

    # Set remote description
    await pc.setRemoteDescription(offer_sdp)

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )


async def disconnect(request):
    """Handle client disconnect"""
    params = await request.json()
    client_id = params.get("client_id")

    if client_id in stream_manager.pcs:
        pc = stream_manager.pcs[client_id]
        await pc.close()

    stream_manager.remove_stream(client_id)
    logger.info(f"Client {client_id} disconnected")

    return web.Response(
        content_type="application/json",
        text=json.dumps({"status": "disconnected"})
    )


async def status(request):
    """Return current streaming status"""
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "active_streams": stream_manager.get_stream_count(),
            "max_streams": stream_manager.max_streams
        })
    )


async def index(request):
    """Serve the client HTML page"""
    client_html_path = os.path.join(get_base_path(), 'client.html')
    with open(client_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return web.Response(content_type='text/html', text=content)


async def on_shutdown(app):
    """Cleanup on shutdown"""
    logger.info("Shutting down, closing all connections...")
    for client_id, pc in list(stream_manager.pcs.items()):
        await pc.close()


def create_app():
    """Create and configure the web application"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_post('/offer', offer)
    app.router.add_post('/disconnect', disconnect)
    app.router.add_get('/status', status)
    app.on_shutdown.append(on_shutdown)
    return app


def run_server(host='0.0.0.0', port=8080, use_ssl=True, enable_airplay=True, enable_mdns=True):
    """Run the server with optional AirPlay support and mDNS discovery"""
    global airplay_receiver, mdns_advertiser

    app = create_app()

    ssl_context = None
    protocol = "http"

    if use_ssl:
        # Get the directory where executable/script is located (for user-provided certs)
        exe_dir = get_executable_dir()
        cert_file = os.path.join(exe_dir, 'cert.pem')
        key_file = os.path.join(exe_dir, 'key.pem')

        if os.path.exists(cert_file) and os.path.exists(key_file):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            protocol = "https"
            logger.info(f"Starting server on https://{host}:{port}")
            logger.info(f"Devices should visit https://<this-computer-ip>:{port}")
            logger.info("Note: You'll need to accept the self-signed certificate warning in the browser")
        else:
            logger.warning("SSL certificates not found, falling back to HTTP")
            logger.info(f"Starting server on http://{host}:{port}")
            logger.info(f"Devices should visit http://<this-computer-ip>:{port}")
    else:
        logger.info(f"Starting server on http://{host}:{port}")
        logger.info(f"Devices should visit http://<this-computer-ip>:{port}")

    # Start mDNS discovery for Chrome/Chromebook casting
    if enable_mdns:
        try:
            from mdns_discovery import MDNSAdvertiser
            mdns_advertiser = MDNSAdvertiser("Desktop Casting Receiver", port, protocol)
            if mdns_advertiser.start():
                logger.info("✓ mDNS discovery enabled - Chrome/Chromebook can discover this device")
            else:
                logger.warning("mDNS discovery failed - devices must use manual URL entry")
        except ImportError:
            logger.warning("mdns_discovery module not found - Chrome won't discover device automatically")
        except Exception as e:
            logger.error(f"Failed to start mDNS discovery: {e}")
            logger.debug("Exception details:", exc_info=True)

    # Start AirPlay receiver if enabled
    # Try UxPlay first (provides actual iOS screen mirroring), fall back to Python implementation
    if enable_airplay:
        global uxplay_integration
        uxplay_started = False

        # Try UxPlay integration first (C/C++ implementation with real screen mirroring)
        try:
            from uxplay_integration import UxPlayIntegration
            uxplay = UxPlayIntegration(stream_manager, name="Desktop Casting Receiver")

            if uxplay.is_uxplay_available():
                logger.info("UxPlay detected - attempting to start iOS screen mirroring service")
                if uxplay.start():
                    uxplay_integration = uxplay
                    uxplay_started = True
                    logger.info("✓ UxPlay started successfully - iOS devices can mirror via AirPlay")
                    logger.info("  Open Control Center on iPhone/iPad → Screen Mirroring → 'Desktop Casting Receiver'")
                else:
                    logger.warning("UxPlay failed to start, will try Python AirPlay fallback")
            else:
                logger.info("UxPlay not installed - using built-in Python AirPlay receiver")
                logger.info("  Python AirPlay has full crypto support (SRP-6a, Ed25519, ChaCha20, H.264)")
        except ImportError:
            logger.info("UxPlay integration module not found - using Python AirPlay infrastructure")
        except Exception as e:
            logger.warning(f"UxPlay integration error: {e}")

        # Fall back to Python AirPlay implementation if UxPlay didn't start
        if not uxplay_started:
            try:
                from airplay_receiver import AirPlayReceiver
                airplay_receiver = AirPlayReceiver(stream_manager, name="Desktop Casting Receiver", port=7000)
                airplay_receiver.start()
                logger.info("✓ Pure Python AirPlay receiver started with full crypto support!")
                logger.info("  - Real SRP-6a authentication")
                logger.info("  - Real Ed25519 key exchange")
                logger.info("  - Real ChaCha20-Poly1305 encryption")
                logger.info("  - H.264 video decoding")
                logger.info("iOS devices can discover 'Desktop Casting Receiver' in Control Center > Screen Mirroring")
            except ImportError as e:
                logger.warning(f"AirPlay support not available (missing dependency: {e})")
                logger.warning("Install 'zeroconf' package for AirPlay support: pip install zeroconf")
            except Exception as e:
                logger.error(f"Failed to start AirPlay receiver: {e}")

        logger.info("WebRTC camera streaming available for all mobile devices at the web interface")

    web.run_app(app, host=host, port=port, ssl_context=ssl_context, handle_signals=False)

    # Cleanup on exit
    logger.info("Shutting down services...")

    if mdns_advertiser:
        logger.info("Stopping mDNS discovery...")
        mdns_advertiser.stop()

    if uxplay_integration:
        logger.info("Stopping UxPlay...")
        uxplay_integration.stop()

    if airplay_receiver:
        logger.info("Stopping Python AirPlay receiver...")
        airplay_receiver.stop()

    logger.info("Shutdown complete")


if __name__ == '__main__':
    run_server()
