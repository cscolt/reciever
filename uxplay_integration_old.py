#!/usr/bin/env python3
"""
UxPlay Integration Module
Integrates UxPlay AirPlay mirroring server as a subprocess
Captures video frames and feeds them to StreamManager
"""

import subprocess
import threading
import time
import logging
import shutil
import os
import re
import numpy as np
import cv2
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UxPlayIntegration:
    """
    Integrates UxPlay AirPlay receiver as subprocess
    Captures frames and integrates with existing StreamManager
    """

    def __init__(self, stream_manager, name="Desktop Casting Receiver", video_port=7100):
        """
        Initialize UxPlay integration

        Args:
            stream_manager: The StreamManager instance to add streams to
            name: The name to advertise for AirPlay
            video_port: Port for video mirroring (default 7100)
        """
        self.stream_manager = stream_manager
        self.name = name
        self.video_port = video_port
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.active_clients = {}  # {device_name: client_info}
        self.frame_pipe_path = None

    @staticmethod
    def is_uxplay_available() -> bool:
        """Check if UxPlay is installed and available"""
        return shutil.which('uxplay') is not None

    @staticmethod
    def check_dependencies() -> dict:
        """
        Check if all UxPlay dependencies are available

        Returns:
            dict with dependency status
        """
        deps = {
            'uxplay': shutil.which('uxplay') is not None,
            'gstreamer': shutil.which('gst-launch-1.0') is not None,
            'avahi': os.path.exists('/usr/bin/avahi-daemon') or os.path.exists('/usr/sbin/avahi-daemon'),
        }
        return deps

    def start(self):
        """Start UxPlay as subprocess"""
        if self.running:
            logger.warning("UxPlay integration already running")
            return False

        if not self.is_uxplay_available():
            logger.error("UxPlay not found. Please install UxPlay first.")
            logger.info("Installation: https://github.com/FDH2/UxPlay")
            return False

        try:
            # Create named pipe for frame capture (if using custom video sink)
            # For now, we'll use UxPlay's built-in functionality and monitor output

            logger.info(f"Starting UxPlay with name '{self.name}'")

            # Start UxPlay with minimal output
            # -n: set name
            # -p: disable audio (we only want video)
            # -vs: video sink (using default for now)
            # -reset 5: reset if no connection for 5 seconds
            cmd = [
                'uxplay',
                '-n', self.name,
                '-p',  # Audio port (will use default)
                '-reset', '5',  # Reset after 5 seconds of inactivity
            ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.running = True

            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.monitor_thread.start()

            logger.info("UxPlay subprocess started successfully")
            logger.info("iOS devices should now see 'Desktop Casting Receiver' in AirPlay menu")
            return True

        except Exception as e:
            logger.error(f"Failed to start UxPlay: {e}")
            self.running = False
            return False

    def stop(self):
        """Stop UxPlay subprocess"""
        self.running = False

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping UxPlay: {e}")

            self.process = None

        logger.info("UxPlay stopped")

    def _monitor_output(self):
        """Monitor UxPlay stdout/stderr for connection events"""
        logger.info("Monitoring UxPlay output...")

        connection_pattern = re.compile(r'raop_rtp_mirror starting mirroring')
        client_name_pattern = re.compile(r'Authenticated\s+([^\s]+)')
        disconnect_pattern = re.compile(r'raop_rtp_mirror.*stopped')

        current_client = None

        try:
            while self.running and self.process:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Log UxPlay output
                logger.debug(f"UxPlay: {line}")

                # Detect client authentication
                match = client_name_pattern.search(line)
                if match:
                    current_client = match.group(1)
                    logger.info(f"UxPlay: Client authenticated - {current_client}")

                # Detect mirroring start
                if connection_pattern.search(line):
                    if current_client:
                        client_id = f"uxplay_{current_client}_{int(time.time())}"
                        logger.info(f"UxPlay: Mirroring started for {current_client}")

                        # Create placeholder frame for UxPlay connection
                        placeholder = self._create_uxplay_placeholder(current_client)
                        self.stream_manager.add_stream(client_id, placeholder, f"UxPlay: {current_client}")

                        # Store client info
                        self.active_clients[current_client] = {
                            'client_id': client_id,
                            'connected_at': time.time(),
                        }

                        # Start frame update thread for this client
                        threading.Thread(
                            target=self._update_frames,
                            args=(client_id, current_client),
                            daemon=True
                        ).start()

                # Detect disconnection
                if disconnect_pattern.search(line):
                    logger.info(f"UxPlay: Mirroring stopped")
                    if current_client and current_client in self.active_clients:
                        client_id = self.active_clients[current_client]['client_id']
                        self.stream_manager.remove_stream(client_id)
                        del self.active_clients[current_client]
                    current_client = None

        except Exception as e:
            logger.error(f"Error monitoring UxPlay output: {e}")
        finally:
            logger.info("UxPlay monitor thread stopped")

    def _update_frames(self, client_id: str, device_name: str):
        """
        Update frames for a connected client

        Note: This is a placeholder implementation.
        Full frame capture would require GStreamer pipeline integration.
        """
        frame_count = 0

        try:
            while self.running and device_name in self.active_clients:
                # Create updated placeholder frame
                # In full implementation, this would capture actual video frames
                frame = self._create_uxplay_placeholder(
                    device_name,
                    f"Connected • Frame {frame_count}"
                )

                self.stream_manager.update_stream(client_id, frame)

                frame_count += 1
                time.sleep(0.1)  # 10 FPS placeholder updates

        except Exception as e:
            logger.error(f"Error updating frames for {device_name}: {e}")

    def _create_uxplay_placeholder(self, device_name: str, status: str = "Connected via UxPlay") -> np.ndarray:
        """
        Create a placeholder frame for UxPlay connection

        Args:
            device_name: Name of the iOS device
            status: Status message to display

        Returns:
            NumPy array representing the frame
        """
        # Create a 720p frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Gradient background (blue to purple)
        for y in range(720):
            ratio = y / 720
            r = int(40 + ratio * 80)
            g = int(40 + ratio * 20)
            b = int(60 + ratio * 100)
            frame[y, :] = [b, g, r]

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Title
        text1 = f"UxPlay: {device_name}"
        text_size = cv2.getTextSize(text1, font, 1.5, 2)[0]
        text_x = (1280 - text_size[0]) // 2
        cv2.putText(frame, text1, (text_x, 280), font, 1.5, (255, 255, 255), 3)

        # Status
        text2 = status
        text_size2 = cv2.getTextSize(text2, font, 1.0, 2)[0]
        text_x2 = (1280 - text_size2[0]) // 2
        cv2.putText(frame, text2, (text_x2, 360), font, 1.0, (100, 255, 100), 2)

        # Info message
        info = "Full video decoding requires GStreamer pipeline integration"
        text_size3 = cv2.getTextSize(info, font, 0.6, 1)[0]
        text_x3 = (1280 - text_size3[0]) // 2
        cv2.putText(frame, info, (text_x3, 440), font, 0.6, (200, 200, 200), 1)

        # Instructions
        instructions = [
            "Note: This is a placeholder showing UxPlay is connected.",
            "To see actual video frames, GStreamer frame extraction is needed.",
            "The connection is working - check UxPlay terminal output for details."
        ]

        y_offset = 520
        for instruction in instructions:
            text_size_i = cv2.getTextSize(instruction, font, 0.5, 1)[0]
            text_x_i = (1280 - text_size_i[0]) // 2
            cv2.putText(frame, instruction, (text_x_i, y_offset), font, 0.5, (180, 180, 180), 1)
            y_offset += 30

        return frame

    def get_status(self) -> dict:
        """Get current status of UxPlay integration"""
        return {
            'running': self.running,
            'uxplay_available': self.is_uxplay_available(),
            'active_clients': len(self.active_clients),
            'clients': list(self.active_clients.keys())
        }


# Test standalone
if __name__ == "__main__":
    # Create dummy stream manager
    class DummyStreamManager:
        def add_stream(self, client_id, frame, name):
            print(f"Stream added: {client_id} - {name}")

        def update_stream(self, client_id, frame):
            print(f"Stream updated: {client_id}")

        def remove_stream(self, client_id):
            print(f"Stream removed: {client_id}")

    # Check dependencies
    print("Checking UxPlay dependencies...")
    integration = UxPlayIntegration(DummyStreamManager())
    deps = integration.check_dependencies()

    print("\nDependency Status:")
    for dep, available in deps.items():
        status = "✓ Available" if available else "✗ Missing"
        print(f"  {dep}: {status}")

    if not integration.is_uxplay_available():
        print("\n❌ UxPlay not found!")
        print("Install from: https://github.com/FDH2/UxPlay")
        exit(1)

    print("\n✓ UxPlay is available!")
    print("\nStarting UxPlay integration...")

    try:
        if integration.start():
            print("✓ UxPlay started successfully")
            print("\nConnect from your iPhone:")
            print("  1. Open Control Center")
            print("  2. Tap 'Screen Mirroring'")
            print("  3. Select 'Desktop Casting Receiver'")
            print("\nPress Ctrl+C to stop...")

            while True:
                time.sleep(1)
                status = integration.get_status()
                if status['active_clients'] > 0:
                    print(f"Active clients: {status['clients']}")
    except KeyboardInterrupt:
        print("\n\nStopping UxPlay...")
        integration.stop()
        print("✓ UxPlay stopped")
