#!/usr/bin/env python3
"""
Desktop Casting Receiver Server
Handles WebRTC connections from Chromebooks and manages screen streaming
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    def add_stream(self, client_id, name):
        with self.lock:
            if len(self.streams) >= self.max_streams:
                return False
            self.streams[client_id] = {
                'frame': None,
                'name': name,
                'timestamp': time.time()
            }
            return True

    def update_frame(self, client_id, frame):
        with self.lock:
            if client_id in self.streams:
                self.streams[client_id]['frame'] = frame
                self.streams[client_id]['timestamp'] = time.time()

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


def run_server(host='0.0.0.0', port=8080, use_ssl=True):
    """Run the server"""
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
            logger.info(f"Chromebooks should visit https://<this-computer-ip>:{port}")
            logger.info("Note: You'll need to accept the self-signed certificate warning in the browser")
        else:
            logger.warning("SSL certificates not found, falling back to HTTP")
            logger.info(f"Starting server on http://{host}:{port}")
            logger.info(f"Chromebooks should visit http://<this-computer-ip>:{port}")
    else:
        logger.info(f"Starting server on http://{host}:{port}")
        logger.info(f"Chromebooks should visit http://<this-computer-ip>:{port}")

    web.run_app(app, host=host, port=port, ssl_context=ssl_context, handle_signals=False)


if __name__ == '__main__':
    run_server()
