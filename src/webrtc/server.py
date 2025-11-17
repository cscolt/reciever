#!/usr/bin/env python3
"""
WebRTC Server - Handles WebRTC connections and HTTP endpoints
"""

import asyncio
import json
import ssl
import os
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

from ..common import get_logger, get_asset_path, get_ssl_cert_paths, ServerConfig
from .stream_manager import StreamManager
from .video_track import VideoFrameTrack

logger = get_logger(__name__)


class WebRTCServer:
    """WebRTC server for handling streaming connections"""

    def __init__(self, stream_manager: StreamManager, config: ServerConfig):
        """
        Initialize the WebRTC server

        Args:
            stream_manager: StreamManager instance for managing streams
            config: Server configuration
        """
        self.stream_manager = stream_manager
        self.config = config
        self.app = self._create_app()

    def _create_app(self) -> web.Application:
        """Create and configure the web application"""
        app = web.Application()
        app.router.add_get('/', self._handle_index)
        app.router.add_post('/offer', self._handle_offer)
        app.router.add_post('/disconnect', self._handle_disconnect)
        app.router.add_get('/status', self._handle_status)
        app.on_shutdown.append(self._on_shutdown)
        return app

    async def _handle_index(self, request: web.Request) -> web.Response:
        """Serve the client HTML page"""
        try:
            client_html_path = get_asset_path('client.html')
            with open(client_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(content_type='text/html', text=content)
        except FileNotFoundError:
            logger.error(f"Client HTML not found at {client_html_path}")
            return web.Response(
                content_type='text/html',
                text='<h1>Error: Client interface not found</h1>',
                status=500
            )

    async def _handle_offer(self, request: web.Request) -> web.Response:
        """Handle WebRTC offer from client"""
        params = await request.json()
        offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        client_id = params.get("client_id")
        client_name = params.get("client_name", f"Client {client_id[:8]}")

        logger.info(f"Received offer from {client_name} ({client_id})")

        # Check if we can accept more streams
        if not self.stream_manager.add_stream(client_id, client_name):
            return web.Response(
                content_type="application/json",
                text=json.dumps({"error": "Maximum streams reached"}),
                status=503
            )

        # Create peer connection
        pc = RTCPeerConnection()
        self.stream_manager.pcs[client_id] = pc

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state for {client_name}: {pc.connectionState}")
            if pc.connectionState in ["failed", "closed"]:
                self.stream_manager.remove_stream(client_id)
                await pc.close()

        @pc.on("track")
        async def on_track(track):
            logger.info(f"Received track from {client_name}: {track.kind}")
            if track.kind == "video":
                # Wrap the track to process frames
                video_track = VideoFrameTrack(track, client_id, self.stream_manager)

                # Create a task to consume the track and process frames
                async def consume_track():
                    try:
                        while True:
                            await video_track.recv()
                    except Exception as e:
                        logger.debug(f"Track ended for {client_name}: {e}")
                        self.stream_manager.remove_stream(client_id)

                # Start consuming frames
                asyncio.create_task(consume_track())

                # Keep track alive
                @track.on("ended")
                async def on_ended():
                    logger.info(f"Track ended for {client_name}")
                    self.stream_manager.remove_stream(client_id)

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

    async def _handle_disconnect(self, request: web.Request) -> web.Response:
        """Handle client disconnect"""
        params = await request.json()
        client_id = params.get("client_id")

        if client_id in self.stream_manager.pcs:
            pc = self.stream_manager.pcs[client_id]
            await pc.close()

        self.stream_manager.remove_stream(client_id)
        logger.info(f"Client {client_id} disconnected")

        return web.Response(
            content_type="application/json",
            text=json.dumps({"status": "disconnected"})
        )

    async def _handle_status(self, request: web.Request) -> web.Response:
        """Return current streaming status"""
        return web.Response(
            content_type="application/json",
            text=json.dumps({
                "active_streams": self.stream_manager.get_stream_count(),
                "max_streams": self.stream_manager.max_streams
            })
        )

    async def _on_shutdown(self, app: web.Application):
        """Cleanup on shutdown"""
        logger.info("Shutting down WebRTC server, closing all connections...")
        for client_id, pc in list(self.stream_manager.pcs.items()):
            await pc.close()

    def get_ssl_context(self) -> tuple[ssl.SSLContext | None, str]:
        """
        Get SSL context if certificates are available

        Returns:
            Tuple of (ssl_context, protocol) where protocol is 'http' or 'https'
        """
        if not self.config.use_ssl:
            return None, "http"

        cert_file, key_file = get_ssl_cert_paths()

        if os.path.exists(cert_file) and os.path.exists(key_file):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            logger.info(f"SSL certificates loaded from {os.path.dirname(cert_file)}")
            return ssl_context, "https"
        else:
            logger.warning("SSL certificates not found, falling back to HTTP")
            logger.info(f"Expected cert at: {cert_file}")
            logger.info(f"Expected key at: {key_file}")
            return None, "http"

    def run(self):
        """Run the WebRTC server"""
        ssl_context, protocol = self.get_ssl_context()

        logger.info(f"Starting WebRTC server on {protocol}://{self.config.host}:{self.config.port}")
        logger.info(f"Devices should visit {protocol}://<this-computer-ip>:{self.config.port}")

        if protocol == "https":
            logger.info("Note: You'll need to accept the self-signed certificate warning in the browser")

        web.run_app(
            self.app,
            host=self.config.host,
            port=self.config.port,
            ssl_context=ssl_context,
            handle_signals=False
        )
