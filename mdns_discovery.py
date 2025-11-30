#!/usr/bin/env python3
"""
mDNS Service Discovery Module
Advertises the WebRTC server so Chrome/Chromebook can discover it
"""

import socket
import logging
from typing import Optional

try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    ServiceInfo = None
    Zeroconf = None

logger = logging.getLogger(__name__)


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

    def start(self):
        """Start advertising services via mDNS"""
        if not ZEROCONF_AVAILABLE:
            logger.warning("Zeroconf not available - mDNS discovery disabled")
            logger.warning("Chrome/Chromebook will NOT discover this server automatically")
            logger.warning("Install with: pip install zeroconf")
            return False

        try:
            logger.info("Starting mDNS service advertisement...")
            self.zeroconf = Zeroconf()

            # Get local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            addresses = [socket.inet_aton(local_ip)]

            # NOTE: Google Cast service is now handled by cast_discovery.py
            # to avoid conflicts. This module only handles WebRTC and HTTP discovery.

            # Advertise as custom WebRTC service
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

            # Advertise as HTTP/HTTPS service for general discovery
            http_type = "_https._tcp.local." if self.protocol == "https" else "_http._tcp.local."
            http_service = ServiceInfo(
                http_type,
                f"{self.name}.{http_type}",
                addresses=addresses,
                port=self.port,
                properties={
                    'path': '/',
                    'name': self.name,
                },
                server=f"{socket.gethostname()}.local."
            )

            logger.info(f"Registering HTTP service: {self.name}")
            self.zeroconf.register_service(http_service)
            self.services.append(http_service)

            self.running = True
            logger.info("✓ mDNS services registered successfully (WebRTC & HTTP)")
            logger.info(f"  Service: '{self.name}'")
            logger.info(f"  Service URL: {self.protocol}://{local_ip}:{self.port}/")
            logger.info(f"  Note: Google Cast discovery is handled separately by cast_discovery.py")

            return True

        except Exception as e:
            logger.error(f"Failed to start mDNS advertising: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def stop(self):
        """Stop advertising services"""
        if not self.running or not self.zeroconf:
            return

        try:
            logger.info("Stopping mDNS service advertisement...")

            for service in self.services:
                try:
                    self.zeroconf.unregister_service(service)
                    logger.debug(f"Unregistered service: {service.name}")
                except Exception as e:
                    logger.warning(f"Error unregistering service: {e}")

            self.zeroconf.close()
            self.zeroconf = None
            self.services = []
            self.running = False

            logger.info("✓ mDNS services stopped")

        except Exception as e:
            logger.error(f"Error stopping mDNS advertising: {e}")

    def get_status(self) -> dict:
        """Get current advertising status"""
        return {
            'running': self.running,
            'zeroconf_available': ZEROCONF_AVAILABLE,
            'service_count': len(self.services),
            'services': [s.name for s in self.services] if self.services else []
        }


# Test standalone
if __name__ == "__main__":
    import time

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("\nTesting mDNS Discovery Module\n")
    print("="*60)

    advertiser = MDNSAdvertiser("Test Casting Receiver", 8080, "http")

    if advertiser.start():
        print("\n✓ mDNS advertising started")
        print("\nTry discovering this device:")
        print("  - Open Chrome on another device")
        print("  - Look for cast devices")
        print("  - Should see 'Test Casting Receiver'")
        print("\nPress Ctrl+C to stop...")

        try:
            while True:
                time.sleep(1)
                status = advertiser.get_status()
                if status['running']:
                    print(f"  Broadcasting {status['service_count']} services...", end='\r')
        except KeyboardInterrupt:
            print("\n\nStopping...")
            advertiser.stop()
            print("✓ Stopped")
    else:
        print("\n✗ Failed to start mDNS advertising")
