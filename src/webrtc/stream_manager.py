#!/usr/bin/env python3
"""
Stream Manager - Manages multiple incoming video streams
"""

import time
from threading import Lock
from typing import Optional, Dict, Any
import numpy as np
from aiortc import RTCPeerConnection

from ..common import get_logger

logger = get_logger(__name__)


class StreamManager:
    """Manages multiple incoming video streams with thread-safe access"""

    def __init__(self, max_streams: int = 8):
        """
        Initialize the StreamManager

        Args:
            max_streams: Maximum number of simultaneous streams
        """
        self.max_streams = max_streams
        self.streams: Dict[str, Dict[str, Any]] = {}  # {client_id: {'frame': np.array, 'name': str, 'timestamp': float}}
        self.lock = Lock()
        self.pcs: Dict[str, RTCPeerConnection] = {}  # {client_id: RTCPeerConnection}

    def add_stream(self, client_id: str, name_or_frame, name: Optional[str] = None) -> bool:
        """
        Add a new stream. Supports two signatures:
        - add_stream(client_id, name) for WebRTC streams
        - add_stream(client_id, frame, name) for AirPlay streams

        Args:
            client_id: Unique identifier for the stream
            name_or_frame: Either the stream name (str) or initial frame (np.array)
            name: Optional name (used when name_or_frame is a frame)

        Returns:
            True if stream was added, False if maximum streams reached
        """
        with self.lock:
            if len(self.streams) >= self.max_streams:
                logger.warning(f"Cannot add stream {client_id}: maximum streams ({self.max_streams}) reached")
                return False

            # Determine if this is WebRTC (name_or_frame is string) or AirPlay (name_or_frame is frame)
            if isinstance(name_or_frame, str):
                # WebRTC style: add_stream(client_id, name)
                self.streams[client_id] = {
                    'frame': None,
                    'name': name_or_frame,
                    'timestamp': time.time()
                }
                logger.info(f"Added WebRTC stream: {name_or_frame} ({client_id})")
            else:
                # AirPlay style: add_stream(client_id, frame, name)
                self.streams[client_id] = {
                    'frame': name_or_frame,
                    'name': name if name else 'AirPlay Device',
                    'timestamp': time.time()
                }
                logger.info(f"Added AirPlay stream: {name if name else 'AirPlay Device'} ({client_id})")

            return True

    def update_frame(self, client_id: str, frame: np.ndarray):
        """
        Update frame for a stream

        Args:
            client_id: Stream identifier
            frame: New video frame as numpy array
        """
        with self.lock:
            if client_id in self.streams:
                self.streams[client_id]['frame'] = frame
                self.streams[client_id]['timestamp'] = time.time()

    def update_stream(self, client_id: str, frame: np.ndarray):
        """
        Update frame for a stream (AirPlay interface - alias for update_frame)

        Args:
            client_id: Stream identifier
            frame: New video frame as numpy array
        """
        self.update_frame(client_id, frame)

    def remove_stream(self, client_id: str):
        """
        Remove a stream

        Args:
            client_id: Stream identifier
        """
        with self.lock:
            if client_id in self.streams:
                name = self.streams[client_id]['name']
                del self.streams[client_id]
                logger.info(f"Removed stream: {name} ({client_id})")
            if client_id in self.pcs:
                del self.pcs[client_id]

    def get_all_streams(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all streams with their data (thread-safe copy)

        Returns:
            Dictionary of all streams
        """
        with self.lock:
            return {k: v.copy() for k, v in self.streams.items()}

    def get_stream_count(self) -> int:
        """
        Get the number of active streams

        Returns:
            Number of active streams
        """
        with self.lock:
            return len(self.streams)

    def has_stream(self, client_id: str) -> bool:
        """
        Check if a stream exists

        Args:
            client_id: Stream identifier

        Returns:
            True if stream exists
        """
        with self.lock:
            return client_id in self.streams

    def get_stream(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific stream's data

        Args:
            client_id: Stream identifier

        Returns:
            Stream data dictionary or None if not found
        """
        with self.lock:
            if client_id in self.streams:
                return self.streams[client_id].copy()
            return None
