#!/usr/bin/env python3
"""
Common utility functions for Desktop Casting Receiver
"""

import os
import sys
import socket
from typing import Optional


def get_base_path() -> str:
    """
    Get base path for bundled files, handling PyInstaller bundled mode

    Returns:
        Base path for bundled resources
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - return _MEIPASS for bundled files
        return sys._MEIPASS
    else:
        # Running in development - return project root
        # Go up two levels from src/common/ to reach project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_executable_dir() -> str:
    """
    Get directory where executable/script is located (for user files like certs)

    Returns:
        Directory containing the executable or main script
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - return exe directory
        return os.path.dirname(sys.executable)
    else:
        # Running in development - return project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_local_ip() -> Optional[str]:
    """
    Get the local IP address of this machine

    Returns:
        Local IP address as string, or None if unable to determine
    """
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def is_port_available(port: int, host: str = 'localhost') -> bool:
    """
    Check if a port is available for binding

    Args:
        port: Port number to check
        host: Host to check (default: localhost)

    Returns:
        True if port is available, False if occupied
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except Exception:
        return False


def ensure_directory(path: str):
    """
    Ensure a directory exists, creating it if necessary

    Args:
        path: Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)


def get_asset_path(filename: str) -> str:
    """
    Get the full path to an asset file

    Args:
        filename: Name of the asset file

    Returns:
        Full path to the asset
    """
    base = get_base_path()
    return os.path.join(base, 'assets', filename)


def get_ssl_cert_paths() -> tuple[str, str]:
    """
    Get paths to SSL certificate files

    Returns:
        Tuple of (cert_path, key_path)
    """
    exe_dir = get_executable_dir()
    cert_path = os.path.join(exe_dir, 'cert.pem')
    key_path = os.path.join(exe_dir, 'key.pem')
    return cert_path, key_path
