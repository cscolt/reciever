"""Desktop Casting Receiver - Multi-device screen casting receiver"""

__version__ = "2.0.0"

from .app import DesktopCastingReceiver, main
from .common import AppConfig, get_config, set_config

__all__ = [
    'DesktopCastingReceiver',
    'main',
    'AppConfig',
    'get_config',
    'set_config',
]
