#!/usr/bin/env python3
"""
mDNS Service Discovery Module
Advertises the WebRTC server so Chrome/Chromebook can discover it
"""

import socket
from typing import Optional

try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    ServiceInfo = None
    Zeroconf = None

from ..common import get_logger, get_local_ip

logger = get_logger(__name__)


class MDNSAdvertiser:
    """
    Advertises the server via mDNS/Bonjour for automatic discovery
    Supports both Chrome Cast and custom discovery protocols
    """

    def __init__(self, name: str = "Desktop Casting Receiver", port: int = 8080, protocol: str = "http"):
        """
        Initialize mDNS advertiser

        Args:
            name: Friendly name for the service
            port: WebRTC server port
            protocol: 'http' or 'https'
        """
        self.name = name
        self.port = port
        self.protocol = protocol
        self.zeroconf: Optional[Zeroconf] = None
        self.services = []
        self.running = False

    def start(self) -> bool:
        """
        Start advertising services via mDNS

        Returns:
            True if successfully started, False otherwise
        """
        if not ZEROCONF_AVAILABLE:
            logger.warning("Zeroconf not available - mDNS discovery disabled")
            logger.warning("Chrome/Chromebook will NOT discover this server automatically")
            logger.warning("Install with: pip install zeroconf")
            return False

        try:
            logger.info("Starting mDNS service advertisement...")
            self.zeroconf = Zeroconf()

            # Get local IP address
            local_ip = get_local_ip()
            if not local_ip:
                logger.error("Could not determine local IP address for mDNS")
                return False

            addresses = [socket.inet_aton(local_ip)]

            # Advertise as Cast-compatible device
            # Chrome looks for _googlecast._tcp services
            cast_service = ServiceInfo(
                "_googlecast._tcp.local.",
                f"{self.name}._googlecast._tcp.local.",
                addresses=addresses,
                port=self.port,
                properties={
                    'id': self.name.replace(' ', '-').lower(),
                    'fn': self.name,  # Friendly name
                    've': '05',  # Version
                    'md': 'Desktop Casting Receiver',  # Model
                    'ic': '/icon.png',  # Icon path
                    'ca': '4101',  # Capabilities
                    'st': '0',  # State
                },
                server=f"{socket.gethostname()}.local."
            )

            logger.info(f"Registering Cast service: {self.name}")
            self.zeroconf.register_service(cast_service)
            self.services.append(cast_service)

            # Also advertise as custom WebRTC service
            # This allows custom clients to discover it
            webrtc_service = ServiceInfo(
                "_webrtc._tcp.local.",
                f"{self.name}._webrtc._tcp.local.",
                addresses=addresses,
                port=self.port,
                properties={
                    'name': self.name,
                    'protocol': self.protocol,
                    'path': '/',
                    'type': 'screen-casting',
                },
                server=f"{socket.gethostname()}.local."
            )

            logger.info(f"Registering WebRTC service: {self.name}")
            self.zeroconf.register_service(webrtc_service)
            self.services.append(webrtc_service)

            self.running = True
            logger.info(f"✓ mDNS services advertised on {local_ip}:{self.port}")
            logger.info("Chrome/Chromebook devices can now discover this receiver")
            return True

        except Exception as e:
            logger.error(f"Failed to start mDNS advertisement: {e}")
            logger.debug("Exception details:", exc_info=True)
            return False

    def stop(self):
        """Stop advertising services"""
        if self.zeroconf and self.running:
            logger.info("Stopping mDNS service advertisement...")
            try:
                for service in self.services:
                    self.zeroconf.unregister_service(service)
                self.zeroconf.close()
                self.running = False
                logger.info("✓ mDNS services stopped")
            except Exception as e:
                logger.error(f"Error stopping mDNS services: {e}")
