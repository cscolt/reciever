#!/usr/bin/env python3
"""
Google Cast Discovery Service
Advertises the receiver as a Cast target using mDNS/Zeroconf
"""

import socket
import uuid
import logging
from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


class CastDiscovery:
    """
    Advertises the receiver as a Google Cast target using mDNS.
    This makes the receiver appear in the Cast menu on Chrome and Android devices.
    """

    def __init__(self, friendly_name="Desktop Casting Receiver", port=8080, protocol="http"):
        """
        Initialize Cast discovery service

        Args:
            friendly_name: Name that appears in Cast menus
            port: Port where the receiver is listening
            protocol: 'http' or 'https'
        """
        self.friendly_name = friendly_name
        self.port = port
        self.protocol = protocol
        self.zeroconf = None
        self.service_info = None

        # Generate a unique device ID (UUID format)
        self.device_id = str(uuid.uuid4())

        # Get local IP address
        self.ip_address = self._get_local_ip()

        logger.info(f"Cast Discovery initialized for {friendly_name} at {self.ip_address}:{port}")

    def _get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            # Create a socket to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.warning(f"Could not determine local IP: {e}")
            return "127.0.0.1"

    def start(self):
        """Start advertising as a Cast receiver"""
        try:
            # Google Cast uses _googlecast._tcp service type
            service_type = "_googlecast._tcp.local."
            service_name = f"{self.friendly_name}.{service_type}"

            # Cast receiver properties
            # These tell Cast senders about our capabilities
            properties = {
                # Device identification
                b'id': self.device_id.encode('utf-8'),
                b'fn': self.friendly_name.encode('utf-8'),  # Friendly name
                b'md': b'Desktop Casting Receiver',  # Model name
                b've': b'02',  # Version

                # Capabilities
                # ca: Capabilities bitmask
                # Bit 0 (0x01): Video output supported
                # Bit 1 (0x02): Audio output supported
                # Bit 2 (0x04): Video input supported
                # Bit 3 (0x08): Audio input supported
                b'ca': b'4101',  # Supports video/audio out, screen mirroring

                # Application URL - where Cast loads the receiver HTML
                b'rs': b'',  # Receiver status (empty means ready)

                # Icon URL (optional)
                b'ic': b'/icon.png',

                # Network status
                b'st': b'0',  # Status flag (0 = available)
            }

            # Create service info
            # The service info tells Cast senders how to connect to us
            self.service_info = ServiceInfo(
                type_=service_type,
                name=service_name,
                addresses=[socket.inet_aton(self.ip_address)],
                port=self.port,
                properties=properties,
                server=f"{socket.gethostname()}.local."
            )

            # Start zeroconf
            self.zeroconf = Zeroconf()
            self.zeroconf.register_service(self.service_info)

            logger.info(f"✓ Cast discovery service started")
            logger.info(f"  Service: {service_name}")
            logger.info(f"  Address: {self.ip_address}:{self.port}")
            logger.info(f"  Device ID: {self.device_id}")
            logger.info(f"  Protocol: {self.protocol}")
            logger.info("")
            logger.info("Your receiver should now appear in:")
            logger.info("  - Chrome Cast menu (click Cast button in toolbar)")
            logger.info("  - Android Cast menu (Settings > Connected devices > Cast)")
            logger.info("")
            logger.info("IMPORTANT: To complete Cast setup:")
            logger.info("  1. Register your app at https://cast.google.com/publish/")
            logger.info(f"  2. Set receiver URL to: {self.protocol}://{self.ip_address}:{self.port}/cast_receiver")
            logger.info("  3. Get your Application ID")
            logger.info("  4. Devices will need to use that Application ID to cast")

            return True

        except Exception as e:
            logger.error(f"Failed to start Cast discovery: {e}", exc_info=True)
            return False

    def stop(self):
        """Stop advertising the Cast receiver"""
        try:
            if self.zeroconf and self.service_info:
                logger.info("Stopping Cast discovery service...")
                self.zeroconf.unregister_service(self.service_info)
                self.zeroconf.close()
                self.zeroconf = None
                self.service_info = None
                logger.info("Cast discovery stopped")
        except Exception as e:
            logger.error(f"Error stopping Cast discovery: {e}")

    def update_status(self, status):
        """
        Update the receiver status

        Args:
            status: Status string (e.g., 'IDLE', 'BUSY', 'STREAMING')
        """
        # This would require re-registering the service with updated properties
        # For simplicity, we'll log it for now
        logger.debug(f"Cast receiver status: {status}")


# Test the module
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Starting Cast Discovery test...")
    print("Press Ctrl+C to stop")
    print()

    discovery = CastDiscovery("Test Cast Receiver", 8080, "http")

    if discovery.start():
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            discovery.stop()
    else:
        print("Failed to start Cast discovery")
