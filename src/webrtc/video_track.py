#!/usr/bin/env python3
"""
Video Frame Track - Processes incoming WebRTC video frames
"""

from aiortc import VideoStreamTrack

from ..common import get_logger

logger = get_logger(__name__)


class VideoFrameTrack(VideoStreamTrack):
    """Custom video track that processes incoming frames and feeds them to StreamManager"""

    def __init__(self, track: VideoStreamTrack, client_id: str, stream_manager):
        """
        Initialize the video frame track

        Args:
            track: The underlying VideoStreamTrack
            client_id: Unique identifier for this stream
            stream_manager: StreamManager instance to update with frames
        """
        super().__init__()
        self.track = track
        self.client_id = client_id
        self.stream_manager = stream_manager

    async def recv(self):
        """
        Receive and process a video frame

        Returns:
            The processed video frame
        """
        frame = await self.track.recv()

        # Convert frame to numpy array (BGR24 format for OpenCV compatibility)
        img = frame.to_ndarray(format="bgr24")

        # Update the stream manager with the new frame
        self.stream_manager.update_frame(self.client_id, img)

        return frame
