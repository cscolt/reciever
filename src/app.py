#!/usr/bin/env python3
"""
Main Application Module
Orchestrates all components: WebRTC server, AirPlay, mDNS, and GUI
"""

import tkinter as tk
import threading

from .common import (
    get_config,
    set_config,
    setup_logging,
    get_logger,
    AppConfig,
)
from .webrtc import StreamManager, WebRTCServer
from .gui import StreamViewer
from .discovery import MDNSAdvertiser
from .airplay import UxPlayIntegration, AirPlayReceiver

logger = get_logger(__name__)


class DesktopCastingReceiver:
    """Main application that orchestrates all components"""

    def __init__(self, config: AppConfig = None):
        """
        Initialize the Desktop Casting Receiver

        Args:
            config: Application configuration (uses defaults if None)
        """
        # Setup configuration
        if config:
            set_config(config)
        self.config = get_config()

        # Setup logging
        setup_logging(self.config.logging)
        logger.info("Starting Desktop Casting Receiver")
        logger.info(f"Configuration: {self.config.server.max_streams} max streams")

        # Initialize components
        self.stream_manager = StreamManager(max_streams=self.config.server.max_streams)
        self.webrtc_server = WebRTCServer(self.stream_manager, self.config.server)
        self.mdns_advertiser = None
        self.uxplay = None
        self.airplay = None

        # GUI components
        self.root = None
        self.viewer = None

    def start_server(self):
        """Start the WebRTC server and all services"""
        logger.info("Starting all services...")

        # Start mDNS discovery
        if self.config.mdns.enabled:
            try:
                ssl_context, protocol = self.webrtc_server.get_ssl_context()
                self.mdns_advertiser = MDNSAdvertiser(
                    name=self.config.mdns.service_name,
                    port=self.config.server.port,
                    protocol=protocol
                )
                if self.mdns_advertiser.start():
                    logger.info("✓ mDNS discovery enabled")
                else:
                    logger.warning("mDNS discovery failed to start")
            except Exception as e:
                logger.error(f"Failed to start mDNS: {e}")

        # Start AirPlay support
        if self.config.airplay.enabled:
            self._start_airplay()

        # Start WebRTC server (this blocks)
        logger.info("Starting WebRTC server...")
        self.webrtc_server.run()

    def _start_airplay(self):
        """Start AirPlay support (UxPlay or Python fallback)"""
        uxplay_started = False

        # Try UxPlay first if enabled
        if self.config.airplay.use_uxplay:
            try:
                self.uxplay = UxPlayIntegration(
                    self.stream_manager,
                    name=self.config.airplay.uxplay_name,
                    video_port=self.config.airplay.video_port
                )

                if self.uxplay.is_uxplay_available():
                    logger.info("UxPlay detected - starting iOS screen mirroring service")
                    if self.uxplay.start():
                        uxplay_started = True
                        logger.info("✓ UxPlay started successfully")
                        logger.info("  iOS devices can mirror via Control Center → Screen Mirroring")
                    else:
                        logger.warning("UxPlay failed to start")
                else:
                    logger.info("UxPlay not installed - will use Python AirPlay fallback")
            except Exception as e:
                logger.warning(f"UxPlay integration error: {e}")

        # Fall back to Python AirPlay implementation
        if not uxplay_started:
            try:
                self.airplay = AirPlayReceiver(
                    self.stream_manager,
                    name=self.config.airplay.uxplay_name,
                    port=self.config.airplay.port
                )
                self.airplay.start()
                logger.info("✓ Python AirPlay receiver started (fallback mode)")
                logger.info("  iOS devices can discover in Control Center → Screen Mirroring")
            except ImportError as e:
                logger.warning(f"AirPlay fallback not available (missing dependency: {e})")
            except Exception as e:
                logger.error(f"Failed to start AirPlay receiver: {e}")

    def stop_services(self):
        """Stop all services"""
        logger.info("Stopping services...")

        if self.mdns_advertiser:
            self.mdns_advertiser.stop()

        if self.uxplay:
            self.uxplay.stop()

        if self.airplay:
            self.airplay.stop()

        logger.info("All services stopped")

    def run_gui(self):
        """Run with GUI"""
        logger.info("Starting GUI mode...")

        # Create Tkinter root
        self.root = tk.Tk()

        # Create viewer with server runner callback
        self.viewer = StreamViewer(
            root=self.root,
            stream_manager=self.stream_manager,
            server_runner=self.start_server,
            config=self.config.gui
        )

        # Start the GUI event loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop_services()

    def run_headless(self):
        """Run without GUI (headless mode)"""
        logger.info("Starting headless mode...")

        try:
            self.start_server()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop_services()


def main(headless: bool = False, config: AppConfig = None):
    """
    Main entry point for the application

    Args:
        headless: Run without GUI
        config: Application configuration
    """
    app = DesktopCastingReceiver(config)

    if headless:
        app.run_headless()
    else:
        app.run_gui()


if __name__ == '__main__':
    # Default to GUI mode
    main()
