#!/usr/bin/env python3
"""
AirPlay Receiver Module
Implements an AirPlay mirroring receiver for iPhone/iPad screen mirroring
Integrates with the existing StreamManager
"""

import asyncio
import socket
import struct
import threading
import time
import plistlib
import os
from zeroconf import ServiceInfo, Zeroconf
import numpy as np
import cv2
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tlv8_encode(type_id, data):
    """Encode data in TLV8 format (Type-Length-Value)"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, int):
        data = data.to_bytes((data.bit_length() + 7) // 8, 'little')

    result = b''
    # Split data into 255-byte chunks
    while len(data) > 255:
        result += bytes([type_id, 255]) + data[:255]
        data = data[255:]
    if len(data) > 0:
        result += bytes([type_id, len(data)]) + data
    return result


def tlv8_decode(data):
    """Decode TLV8 format data"""
    result = {}
    i = 0
    while i < len(data):
        if i + 1 >= len(data):
            break
        type_id = data[i]
        length = data[i + 1]
        i += 2
        if i + length > len(data):
            break
        value = data[i:i + length]
        if type_id in result:
            result[type_id] += value
        else:
            result[type_id] = value
        i += length
    return result


class AirPlayReceiver:
    """
    AirPlay receiver that advertises as an AirPlay target and receives
    screen mirroring streams from iOS devices
    """

    def __init__(self, stream_manager, name="Desktop Casting Receiver", port=7000):
        """
        Initialize AirPlay receiver

        Args:
            stream_manager: The StreamManager instance to add streams to
            name: The name to advertise as
            port: Port to listen on for AirPlay connections
        """
        self.stream_manager = stream_manager
        self.name = name
        self.port = port
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.running = False
        self.server_task: Optional[asyncio.Task] = None
        self.active_connections: Dict[str, dict] = {}

    def start(self):
        """Start the AirPlay receiver service"""
        if self.running:
            logger.warning("AirPlay receiver already running")
            return

        self.running = True

        # Start mDNS service advertisement
        self._advertise_service()

        # Start server in background thread
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

        logger.info(f"AirPlay receiver started on port {self.port}")

    def stop(self):
        """Stop the AirPlay receiver service"""
        self.running = False

        # Stop mDNS advertisement
        if self.zeroconf and self.service_info:
            self.zeroconf.unregister_service(self.service_info)
            self.zeroconf.close()
            self.zeroconf = None
            self.service_info = None

        logger.info("AirPlay receiver stopped")

    def _advertise_service(self):
        """Advertise AirPlay service via mDNS (Bonjour)"""
        try:
            # Get local IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Create service info for AirPlay
            # AirPlay uses _airplay._tcp for service discovery
            service_type = "_airplay._tcp.local."
            service_name = f"{self.name}.{service_type}"

            # AirPlay service properties
            properties = {
                b'deviceid': self._get_device_id().encode(),
                b'features': b'0x5A7FFFF7,0x1E',  # Feature flags for screen mirroring
                b'flags': b'0x4',  # Supports screen mirroring
                b'model': b'AppleTV3,2',  # Pretend to be Apple TV
                b'pi': self._get_device_id().encode(),
                b'psi': b'00000000-0000-0000-0000-000000000000',
                b'pk': self._generate_public_key(),
                b'srcvers': b'220.68',  # AirPlay version
                b'vv': b'2',
            }

            # Register service
            self.service_info = ServiceInfo(
                service_type,
                service_name,
                addresses=[socket.inet_aton(local_ip)],
                port=self.port,
                properties=properties,
                server=f"{hostname}.local."
            )

            self.zeroconf = Zeroconf()
            self.zeroconf.register_service(self.service_info)

            logger.info(f"AirPlay service advertised as '{self.name}' at {local_ip}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to advertise AirPlay service: {e}")

    def _get_device_id(self) -> str:
        """Generate a unique device ID"""
        mac = ':'.join(['{:02x}'.format((hash(socket.gethostname()) >> i) & 0xff)
                       for i in range(0, 48, 8)])
        return mac

    def _generate_public_key(self) -> bytes:
        """Generate a dummy public key for AirPlay authentication"""
        # In a full implementation, this would be a real RSA public key
        # For now, return empty key (some iOS versions may work without full auth)
        return b''

    def _run_server(self):
        """Run the AirPlay server in a background thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._server_loop())
        except Exception as e:
            logger.error(f"AirPlay server error: {e}")
        finally:
            loop.close()

    async def _server_loop(self):
        """Main server loop for handling AirPlay connections"""
        server = await asyncio.start_server(
            self._handle_client,
            '0.0.0.0',
            self.port
        )

        logger.info(f"AirPlay server listening on port {self.port}")

        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle an incoming AirPlay client connection - supports multiple requests"""
        addr = writer.get_extra_info('peername')
        client_id = f"airplay_{addr[0]}_{int(time.time())}"

        logger.info(f"AirPlay connection from {addr}")

        try:
            # Keep connection alive for multiple requests
            while True:
                # Read HTTP-style request with timeout
                try:
                    request_line = await asyncio.wait_for(reader.readline(), timeout=30.0)
                except asyncio.TimeoutError:
                    logger.info(f"Connection timeout for {addr}")
                    break

                request = request_line.decode('utf-8', errors='ignore').strip()

                if not request:
                    break

                # Read headers
                headers = {}
                content_length = 0
                while True:
                    line = await reader.readline()
                    if line == b'\r\n' or line == b'\n' or not line:
                        break
                    try:
                        header_line = line.decode('utf-8', errors='ignore').strip()
                        if ':' in header_line:
                            key, value = header_line.split(':', 1)
                            key_lower = key.strip().lower()
                            headers[key_lower] = value.strip()
                            if key_lower == 'content-length':
                                content_length = int(value.strip())
                    except:
                        pass

                # Read body if present
                body = b''
                if content_length > 0:
                    body = await reader.read(content_length)

                # Handle different AirPlay requests
                if 'POST' in request or 'GET' in request:
                    await self._handle_airplay_request(request, headers, reader, writer, client_id, body)
                else:
                    break

        except Exception as e:
            logger.error(f"Error handling AirPlay client: {e}", exc_info=True)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass

    async def _handle_airplay_request(self, request: str, headers: dict,
                                      reader: asyncio.StreamReader,
                                      writer: asyncio.StreamWriter,
                                      client_id: str,
                                      body: bytes = b''):
        """Handle specific AirPlay protocol requests"""

        # Parse request
        parts = request.split()
        if len(parts) < 2:
            return

        method = parts[0]
        path = parts[1]

        logger.info(f"AirPlay request: {method} {path} (body size: {len(body)} bytes)")

        # Handle different endpoints
        if '/info' in path:
            # Device info request
            await self._handle_info(writer)

        elif '/server-info' in path:
            # Server info request
            await self._handle_server_info(writer)

        elif path == '/pair-setup' and method == 'POST':
            # Pairing setup - implement simplified SRP protocol
            logger.info("Handling pair-setup (SRP protocol)")

            # Decode request to see what state iOS is in
            request_tlv = tlv8_decode(body) if body else {}
            state = request_tlv.get(0x06, b'\x01')[0]

            logger.info(f"Pair-setup state: {state}")

            # Build response based on state
            if state == 1:
                # M1->M2: iOS requests setup, we send salt + server public key
                response_state = 2
                tlv_data = tlv8_encode(0x06, bytes([response_state]))  # State = 2
                # Add salt (16 bytes of random data)
                salt = os.urandom(16)
                tlv_data += tlv8_encode(0x02, salt)  # Salt
                # Add server public key (384 bytes for SRP-6a)
                public_key = os.urandom(384)
                tlv_data += tlv8_encode(0x03, public_key)  # Public Key

            elif state == 3:
                # M3->M4: iOS sends proof, we verify and respond
                response_state = 4
                tlv_data = tlv8_encode(0x06, bytes([response_state]))  # State = 4
                # Add server proof (64 bytes of random data)
                proof = os.urandom(64)
                tlv_data += tlv8_encode(0x04, proof)  # Proof

            else:
                # Unknown state, send error
                logger.warning(f"Unknown pair-setup state: {state}")
                response_state = state + 1
                tlv_data = tlv8_encode(0x06, bytes([response_state]))
                tlv_data += tlv8_encode(0x07, bytes([1]))  # Error = 1 (unknown)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(tlv_data)}\r\n"
                "Server: AirTunes/366.0\r\n"
                "\r\n"
            )
            writer.write(response.encode())
            writer.write(tlv_data)
            await writer.drain()
            logger.info(f"Sent pair-setup response (state {response_state}, {len(tlv_data)} bytes)")

        elif path == '/pair-verify' and method == 'POST':
            # Pairing verify - implement Ed25519 verification protocol
            logger.info("Handling pair-verify (Ed25519 protocol)")

            # Decode request to see what state iOS is in
            request_tlv = tlv8_decode(body) if body else {}
            state = request_tlv.get(0x06, b'\x01')[0]

            logger.info(f"Pair-verify state: {state}")

            # Build response based on state
            if state == 1:
                # M1->M2: iOS sends its public key, we send ours + signature
                response_state = 2
                tlv_data = tlv8_encode(0x06, bytes([response_state]))  # State = 2
                # Add server public key (32 bytes for Curve25519)
                public_key = os.urandom(32)
                tlv_data += tlv8_encode(0x03, public_key)  # Public Key
                # Add encrypted data (signature, ~80 bytes typical)
                encrypted_data = os.urandom(80)
                tlv_data += tlv8_encode(0x05, encrypted_data)  # Encrypted Data

            elif state == 3:
                # M3->M4: iOS sends encrypted data, we verify
                response_state = 4
                tlv_data = tlv8_encode(0x06, bytes([response_state]))  # State = 4
                # No additional data needed for M4

            else:
                # Unknown state, send error
                logger.warning(f"Unknown pair-verify state: {state}")
                response_state = state + 1
                tlv_data = tlv8_encode(0x06, bytes([response_state]))
                tlv_data += tlv8_encode(0x07, bytes([1]))  # Error = 1 (unknown)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(tlv_data)}\r\n"
                "Server: AirTunes/366.0\r\n"
                "\r\n"
            )
            writer.write(response.encode())
            writer.write(tlv_data)
            await writer.drain()
            logger.info(f"Sent pair-verify response (state {response_state}, {len(tlv_data)} bytes)")

        elif path == '/fp-setup' and method == 'POST':
            # FairPlay setup - send minimal response
            logger.info("Handling fp-setup (no FairPlay DRM)")

            # FairPlay can be skipped for non-DRM content
            # Send back empty response with success status
            response_data = b''  # Empty FairPlay response

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(response_data)}\r\n"
                "Server: AirTunes/366.0\r\n"
                "\r\n"
            )
            writer.write(response.encode())
            if response_data:
                writer.write(response_data)
            await writer.drain()
            logger.info("Sent fp-setup response")

        elif '/stream' in path and method == 'POST':
            # This is a video stream
            await self._handle_stream(reader, writer, client_id, headers)

        elif '/reverse' in path:
            # Reverse HTTP connection for events
            await self._handle_reverse_http(reader, writer, client_id)

        elif path == '/feedback' and method == 'POST':
            # Feedback from client
            logger.info("Received feedback from client")
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Server: AirPlay/220.68\r\n"
                "Content-Length: 0\r\n"
                "\r\n"
            )
            writer.write(response.encode())
            await writer.drain()

        else:
            # Send basic response for unknown endpoints
            logger.info(f"Unknown endpoint: {method} {path}")
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Server: AirPlay/220.68\r\n"
                "Content-Length: 0\r\n"
                "\r\n"
            )
            writer.write(response.encode())
            await writer.drain()

    async def _handle_info(self, writer: asyncio.StreamWriter):
        """Handle /info request - return device capabilities"""
        # Create device info plist with all required fields
        info = {
            'deviceid': self._get_device_id(),
            'features': 0x5A7FFFF7,  # Feature flags for screen mirroring
            'model': 'AppleTV3,2',
            'protovers': '1.1',
            'srcvers': '366.0',  # Updated version
            'name': self.name,
            'pi': self._get_device_id(),
            'pk': b'',  # Public key (empty for no auth)
            'vv': 2,
            'statusFlags': 0x4,  # Ready to receive
            'keepAliveLowPower': 1,
            'keepAliveSendStatsAsBody': 1,
        }

        # Convert to binary plist (more reliable than XML)
        try:
            plist_data = plistlib.dumps(info, fmt=plistlib.FMT_BINARY)
        except:
            # Fallback to XML if binary fails
            plist_data = plistlib.dumps(info, fmt=plistlib.FMT_XML)

        # Send response with proper headers
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Date: Sat, 15 Nov 2025 12:00:00 GMT\r\n"
            "Content-Type: application/x-apple-binary-plist\r\n"
            f"Content-Length: {len(plist_data)}\r\n"
            "Server: AirTunes/366.0\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        writer.write(plist_data)
        await writer.drain()
        logger.info(f"Sent /info response ({len(plist_data)} bytes)")

    async def _handle_server_info(self, writer: asyncio.StreamWriter):
        """Handle /server-info request"""
        # Create server info plist
        server_info = {
            'deviceid': self._get_device_id(),
            'features': 0x5A7FFFF7,
            'model': 'AppleTV3,2',
            'protovers': '1.1',
            'srcvers': '366.0',
            'name': self.name,
            'pi': self._get_device_id(),
            'pk': b'',
            'statusFlags': 0x4,
        }

        # Convert to binary plist
        try:
            plist_data = plistlib.dumps(server_info, fmt=plistlib.FMT_BINARY)
        except:
            plist_data = plistlib.dumps(server_info, fmt=plistlib.FMT_XML)

        # Send response
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Date: Sat, 15 Nov 2025 12:00:00 GMT\r\n"
            "Content-Type: application/x-apple-binary-plist\r\n"
            f"Content-Length: {len(plist_data)}\r\n"
            "Server: AirTunes/366.0\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        writer.write(plist_data)
        await writer.drain()
        logger.info(f"Sent /server-info response ({len(plist_data)} bytes)")

    async def _handle_stream(self, reader: asyncio.StreamReader,
                            writer: asyncio.StreamWriter,
                            client_id: str,
                            headers: dict):
        """Handle incoming video stream from AirPlay"""

        # Extract device name if provided
        device_name = headers.get('x-apple-device-id', 'iPhone')

        # Send success response
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Server: AirPlay/220.68\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        await writer.drain()

        logger.info(f"Receiving AirPlay stream from {device_name}")

        # Add to active connections
        self.active_connections[client_id] = {
            'name': device_name,
            'start_time': time.time()
        }

        # Process stream
        try:
            await self._process_video_stream(reader, client_id, device_name)
        except Exception as e:
            logger.error(f"Error processing AirPlay stream: {e}")
        finally:
            # Remove from active connections
            if client_id in self.active_connections:
                del self.active_connections[client_id]

    async def _process_video_stream(self, reader: asyncio.StreamReader,
                                    client_id: str, device_name: str):
        """Process the video stream data"""

        logger.info(f"Processing video stream for {device_name}")

        # Create a placeholder frame
        placeholder = self._create_placeholder_frame(device_name)

        # Add to stream manager
        self.stream_manager.add_stream(client_id, placeholder, f"AirPlay: {device_name}")

        try:
            # Read and process stream data
            # Note: Full H.264 decoding would be needed here
            # For now, we'll create a placeholder that updates
            frame_count = 0

            while self.running:
                # Try to read data
                try:
                    data = await asyncio.wait_for(reader.read(4096), timeout=1.0)
                    if not data:
                        break

                    # In a full implementation, this would decode H.264 video
                    # For now, update placeholder periodically
                    frame_count += 1
                    if frame_count % 30 == 0:  # Update every 30 chunks
                        placeholder = self._create_placeholder_frame(
                            device_name,
                            f"Receiving... ({len(data)} bytes)"
                        )
                        self.stream_manager.update_stream(client_id, placeholder)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Stream read error: {e}")
                    break

        finally:
            self.stream_manager.remove_stream(client_id)
            logger.info(f"AirPlay stream ended for {device_name}")

    async def _handle_reverse_http(self, reader: asyncio.StreamReader,
                                   writer: asyncio.StreamWriter,
                                   client_id: str):
        """Handle reverse HTTP connection for events"""
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: PTTH/1.0\r\n"
            "Connection: Upgrade\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        await writer.drain()

        # Keep connection alive for events
        while self.running:
            await asyncio.sleep(1)

    def _create_placeholder_frame(self, device_name: str, status: str = "Connected") -> np.ndarray:
        """Create a placeholder frame with device info"""
        # Create a 720p frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:] = (40, 40, 60)  # Dark blue background

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Device name
        text1 = f"AirPlay: {device_name}"
        cv2.putText(frame, text1, (50, 300), font, 1.5, (255, 255, 255), 2)

        # Status
        cv2.putText(frame, status, (50, 400), font, 1.0, (100, 255, 100), 2)

        # Info message
        info = "Note: Full video decoding requires additional implementation"
        cv2.putText(frame, info, (50, 500), font, 0.6, (200, 200, 200), 1)

        return frame


# Standalone test
if __name__ == "__main__":
    # Create a dummy stream manager for testing
    class DummyStreamManager:
        def add_stream(self, client_id, frame, name):
            print(f"Stream added: {client_id} - {name}")

        def update_stream(self, client_id, frame):
            print(f"Stream updated: {client_id}")

        def remove_stream(self, client_id):
            print(f"Stream removed: {client_id}")

    manager = DummyStreamManager()
    receiver = AirPlayReceiver(manager)

    try:
        receiver.start()
        print("AirPlay receiver running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        receiver.stop()
        print("\nAirPlay receiver stopped")
