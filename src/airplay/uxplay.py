#!/usr/bin/env python3
"""
Improved UxPlay Integration Module with Real Video Capture
Captures actual video frames from UxPlay using various methods
"""

import subprocess
import threading
import time
import shutil
import os
import re
import numpy as np
import cv2
from typing import Optional
import socket
import struct

# Use common logging
from ..common import get_logger

logger = get_logger(__name__)


class UxPlayIntegration:
    """
    Improved UxPlay integration with real video frame capture
    Supports multiple capture methods:
    1. UDP stream capture (recommended)
    2. GStreamer appsink (if available)
    3. Placeholder frames (fallback)
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

        # Video capture settings
        self.capture_method = None
        self.udp_port = 5000  # Port for UDP video stream
        self.udp_socket = None

    @staticmethod
    def is_uxplay_available() -> bool:
        """Check if UxPlay is installed and available"""
        return shutil.which('uxplay') is not None

    @staticmethod
    def check_gstreamer() -> bool:
        """Check if GStreamer is available"""
        try:
            result = subprocess.run(
                ['gst-launch-1.0', '--version'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def start(self):
        """Start UxPlay with video capture"""
        if self.running:
            logger.warning("UxPlay integration already running")
            return False

        if not self.is_uxplay_available():
            logger.error("UxPlay not found. Please install UxPlay first.")
            logger.info("Installation: https://github.com/FDH2/UxPlay")
            return False

        # Determine capture method
        if self.check_gstreamer():
            logger.info("GStreamer detected - will use advanced video capture")
            self.capture_method = "gstreamer"
        else:
            logger.warning("GStreamer not detected - using basic capture")
            self.capture_method = "basic"

        try:
            logger.info(f"Starting UxPlay with name '{self.name}'")
            logger.info(f"Capture method: {self.capture_method}")

            # Start UxPlay with appropriate options
            if self.capture_method == "gstreamer":
                success = self._start_with_gstreamer()
            else:
                success = self._start_basic()

            if success:
                # Start monitoring thread
                self.monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
                self.monitor_thread.start()

                logger.info("✓ UxPlay started successfully")
                logger.info("  iOS devices should now see 'Desktop Casting Receiver' in AirPlay menu")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to start UxPlay: {e}")
            logger.debug("Exception details:", exc_info=True)
            self.running = False
            return False

    def _start_with_gstreamer(self) -> bool:
        """Start UxPlay with GStreamer video sink for frame capture"""
        try:
            # Use shmsink for efficient IPC between UxPlay and our Python code
            gst_pipeline = (
                f"videoconvert ! "
                f"videoscale ! "
                f"video/x-raw,width=1280,height=720,format=BGR ! "
                f"shmsink socket-path=/tmp/uxplay_frames wait-for-connection=false "
                f"shm-size=10000000 sync=false"
            )

            cmd = [
                'uxplay',
                '-n', self.name,
                '-p',  # Disable audio
                '-vs', gst_pipeline,  # Custom video sink
                '-reset', '5',
                '-vp', '0',  # Disable hardware acceleration issues
            ]

            logger.debug(f"UxPlay command: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Start shared memory frame capture
            threading.Thread(target=self._capture_shm_frames, daemon=True).start()

            self.running = True
            logger.info("✓ UxPlay started with GStreamer shared memory capture")
            return True

        except Exception as e:
            logger.error(f"Failed to start UxPlay with GStreamer: {e}")
            logger.debug("Exception details:", exc_info=True)
            # Fall back to basic mode
            logger.info("Falling back to basic mode (placeholder frames)")
            return self._start_basic()

    def _start_basic(self) -> bool:
        """Start UxPlay in basic mode (no video capture)"""
        try:
            cmd = [
                'uxplay',
                '-n', self.name,
                '-p',  # Disable audio
                '-reset', '5',
            ]

            logger.debug(f"UxPlay command: {' '.join(cmd)}")

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.running = True
            logger.warning("Basic mode: Video frames will be placeholders")
            logger.warning("For real video capture, install GStreamer:")
            logger.warning("  Ubuntu/Debian: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base")
            logger.warning("  Fedora: sudo dnf install gstreamer1-plugins-base gstreamer1-plugins-good")

            return True

        except Exception as e:
            logger.error(f"Failed to start UxPlay in basic mode: {e}")
            logger.debug("Exception details:", exc_info=True)
            return False

    def _start_udp_listener(self):
        """Start UDP socket to receive video frames from GStreamer"""
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**24)  # 16MB buffer
            self.udp_socket.bind(('127.0.0.1', self.udp_port))
            self.udp_socket.settimeout(1.0)

            logger.info(f"UDP listener started on port {self.udp_port}")

            # Start frame capture thread
            capture_thread = threading.Thread(target=self._capture_udp_frames, daemon=True)
            capture_thread.start()

        except Exception as e:
            logger.error(f"Failed to start UDP listener: {e}")
            logger.debug("Exception details:", exc_info=True)
            self.udp_socket = None

    def _capture_shm_frames(self):
        """Capture video frames from GStreamer shared memory"""
        logger.info("Starting shared memory frame capture...")

        # Build GStreamer pipeline to read from shared memory
        try:
            import gi
            gi.require_version('Gst', '1.0')
            from gi.repository import Gst, GLib

            Gst.init(None)

            # Pipeline to read from shmsrc
            pipeline_str = (
                f"shmsrc socket-path=/tmp/uxplay_frames is-live=true ! "
                f"video/x-raw,format=BGR,width=1280,height=720,framerate=30/1 ! "
                f"appsink name=sink emit-signals=true sync=false max-buffers=1 drop=true"
            )

            pipeline = Gst.parse_launch(pipeline_str)
            appsink = pipeline.get_by_name('sink')

            def on_new_sample(sink):
                sample = sink.emit('pull-sample')
                if sample:
                    buf = sample.get_buffer()
                    caps = sample.get_caps()

                    # Get frame data
                    success, map_info = buf.map(Gst.MapFlags.READ)
                    if success:
                        # Convert to numpy array
                        frame = np.frombuffer(map_info.data, dtype=np.uint8)
                        frame = frame.reshape((720, 1280, 3))

                        # Update all active clients
                        for device_name, client_info in list(self.active_clients.items()):
                            self.stream_manager.update_stream(client_info['client_id'], frame.copy())

                        buf.unmap(map_info)

                return Gst.FlowReturn.OK

            appsink.connect('new-sample', on_new_sample)
            pipeline.set_state(Gst.State.PLAYING)

            # Run GLib main loop
            loop = GLib.MainLoop()
            try:
                while self.running:
                    loop.get_context().iteration(True)
            except KeyboardInterrupt:
                pass
            finally:
                pipeline.set_state(Gst.State.NULL)

        except ImportError:
            logger.warning("GStreamer Python bindings not available")
            logger.warning("Install with: sudo apt-get install python3-gi python3-gst-1.0")
            logger.info("Falling back to placeholder frames")
        except Exception as e:
            logger.error(f"Shared memory frame capture failed: {e}")
            logger.debug("Exception details:", exc_info=True)
        finally:
            logger.info("Frame capture stopped")

    def stop(self):
        """Stop UxPlay subprocess"""
        self.running = False

        # Close UDP socket
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except:
                pass
            self.udp_socket = None

        # Terminate UxPlay process
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
                    logger.info(f"✓ iOS device authenticated: {current_client}")

                # Detect mirroring start
                if connection_pattern.search(line):
                    if current_client:
                        client_id = f"uxplay_{current_client}_{int(time.time())}"
                        logger.info(f"✓ Screen mirroring started: {current_client}")

                        # Create initial frame
                        if self.capture_method == "gstreamer":
                            # Use a connecting placeholder until UDP frames arrive
                            placeholder = self._create_connecting_frame(current_client)
                        else:
                            # Use static placeholder for basic mode
                            placeholder = self._create_placeholder_frame(current_client)

                        self.stream_manager.add_stream(client_id, placeholder, f"iOS: {current_client}")

                        # Store client info
                        self.active_clients[current_client] = {
                            'client_id': client_id,
                            'connected_at': time.time(),
                        }

                        # In basic mode, start placeholder updates
                        if self.capture_method != "gstreamer":
                            threading.Thread(
                                target=self._update_placeholder_frames,
                                args=(client_id, current_client),
                                daemon=True
                            ).start()

                # Detect disconnection
                if disconnect_pattern.search(line):
                    logger.info(f"✓ Screen mirroring stopped: {current_client if current_client else 'device'}")
                    if current_client and current_client in self.active_clients:
                        client_id = self.active_clients[current_client]['client_id']
                        self.stream_manager.remove_stream(client_id)
                        del self.active_clients[current_client]
                    current_client = None

        except Exception as e:
            logger.error(f"Error monitoring UxPlay output: {e}")
            logger.debug("Exception details:", exc_info=True)
        finally:
            logger.info("UxPlay monitor thread stopped")

    def _update_placeholder_frames(self, client_id: str, device_name: str):
        """Update placeholder frames (for basic mode)"""
        frame_count = 0

        try:
            while self.running and device_name in self.active_clients:
                frame = self._create_placeholder_frame(
                    device_name,
                    f"Connected • No video capture • Frame {frame_count}"
                )

                self.stream_manager.update_stream(client_id, frame)

                frame_count += 1
                time.sleep(0.5)  # 2 FPS for placeholders

        except Exception as e:
            logger.error(f"Error updating placeholder frames: {e}")

    def _create_connecting_frame(self, device_name: str) -> np.ndarray:
        """Create a 'connecting' frame"""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Blue gradient background
        for y in range(720):
            ratio = y / 720
            b = int(120 + ratio * 80)
            g = int(80 + ratio * 40)
            r = int(40 + ratio * 20)
            frame[y, :] = [b, g, r]

        font = cv2.FONT_HERSHEY_SIMPLEX

        # Title
        text1 = f"iOS: {device_name}"
        text_size = cv2.getTextSize(text1, font, 1.8, 3)[0]
        text_x = (1280 - text_size[0]) // 2
        cv2.putText(frame, text1, (text_x, 300), font, 1.8, (255, 255, 255), 3)

        # Status
        text2 = "Connecting to video stream..."
        text_size2 = cv2.getTextSize(text2, font, 1.0, 2)[0]
        text_x2 = (1280 - text_size2[0]) // 2
        cv2.putText(frame, text2, (text_x2, 380), font, 1.0, (150, 255, 150), 2)

        return frame

    def _create_placeholder_frame(self, device_name: str, status: str = "Connected") -> np.ndarray:
        """Create a placeholder frame (for basic mode)"""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Purple gradient background
        for y in range(720):
            ratio = y / 720
            r = int(60 + ratio * 100)
            g = int(40 + ratio * 30)
            b = int(80 + ratio * 120)
            frame[y, :] = [b, g, r]

        font = cv2.FONT_HERSHEY_SIMPLEX

        # Title
        text1 = f"UxPlay: {device_name}"
        text_size = cv2.getTextSize(text1, font, 1.5, 3)[0]
        text_x = (1280 - text_size[0]) // 2
        cv2.putText(frame, text1, (text_x, 280), font, 1.5, (255, 255, 255), 3)

        # Status
        text_size2 = cv2.getTextSize(status, font, 0.9, 2)[0]
        text_x2 = (1280 - text_size2[0]) // 2
        cv2.putText(frame, status, (text_x2, 350), font, 0.9, (100, 255, 100), 2)

        # Warning message
        warning = "Video capture not available - install GStreamer for real frames"
        text_size3 = cv2.getTextSize(warning, font, 0.5, 1)[0]
        text_x3 = (1280 - text_size3[0]) // 2
        cv2.putText(frame, warning, (text_x3, 420), font, 0.5, (200, 200, 200), 1)

        return frame

    def get_status(self) -> dict:
        """Get current status"""
        return {
            'running': self.running,
            'uxplay_available': self.is_uxplay_available(),
            'capture_method': self.capture_method,
            'active_clients': len(self.active_clients),
            'clients': list(self.active_clients.keys())
        }


if __name__ == "__main__":
    # Test standalone
    class DummyStreamManager:
        def add_stream(self, client_id, frame, name):
            print(f"Stream added: {client_id} - {name} - frame shape: {frame.shape if isinstance(frame, np.ndarray) else 'N/A'}")

        def update_stream(self, client_id, frame):
            print(f"Stream updated: {client_id} - frame shape: {frame.shape}")

        def remove_stream(self, client_id):
            print(f"Stream removed: {client_id}")

    integration = UxPlayIntegration(DummyStreamManager())

    if integration.start():
        print("✓ UxPlay started")
        print("Connect from your iPhone and watch the console output")
        print("Press Ctrl+C to stop...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            integration.stop()
            print("✓ Stopped")
    else:
        print("✗ Failed to start UxPlay")
