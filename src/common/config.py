#!/usr/bin/env python3
"""
Configuration Management for Desktop Casting Receiver
Centralized configuration with environment variables, config files, and CLI args
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = '0.0.0.0'
    port: int = 8080
    use_ssl: bool = True
    cert_file: str = 'cert.pem'
    key_file: str = 'key.pem'
    max_streams: int = 8


@dataclass
class AirPlayConfig:
    """AirPlay configuration"""
    enabled: bool = True
    use_uxplay: bool = True  # Prefer UxPlay over Python implementation
    uxplay_name: str = 'Desktop Casting Receiver'
    port: int = 7000
    video_port: int = 7100


@dataclass
class MDNSConfig:
    """mDNS Discovery configuration"""
    enabled: bool = True
    service_name: str = 'Desktop Casting Receiver'


@dataclass
class GUIConfig:
    """GUI configuration"""
    window_title: str = 'Desktop Casting Receiver'
    grid_rows: int = 2
    grid_cols: int = 4
    frame_update_ms: int = 100  # Update interval in milliseconds


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None  # Log to file if specified


@dataclass
class AppConfig:
    """Main application configuration"""
    server: ServerConfig = field(default_factory=ServerConfig)
    airplay: AirPlayConfig = field(default_factory=AirPlayConfig)
    mdns: MDNSConfig = field(default_factory=MDNSConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def load_from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        config = cls()

        # Server config
        config.server.host = os.getenv('DCR_HOST', config.server.host)
        config.server.port = int(os.getenv('DCR_PORT', config.server.port))
        config.server.use_ssl = os.getenv('DCR_USE_SSL', 'true').lower() == 'true'
        config.server.cert_file = os.getenv('DCR_CERT_FILE', config.server.cert_file)
        config.server.key_file = os.getenv('DCR_KEY_FILE', config.server.key_file)
        config.server.max_streams = int(os.getenv('DCR_MAX_STREAMS', config.server.max_streams))

        # AirPlay config
        config.airplay.enabled = os.getenv('DCR_AIRPLAY_ENABLED', 'true').lower() == 'true'
        config.airplay.use_uxplay = os.getenv('DCR_USE_UXPLAY', 'true').lower() == 'true'
        config.airplay.uxplay_name = os.getenv('DCR_AIRPLAY_NAME', config.airplay.uxplay_name)
        config.airplay.port = int(os.getenv('DCR_AIRPLAY_PORT', config.airplay.port))
        config.airplay.video_port = int(os.getenv('DCR_AIRPLAY_VIDEO_PORT', config.airplay.video_port))

        # mDNS config
        config.mdns.enabled = os.getenv('DCR_MDNS_ENABLED', 'true').lower() == 'true'
        config.mdns.service_name = os.getenv('DCR_MDNS_NAME', config.mdns.service_name)

        # GUI config
        config.gui.window_title = os.getenv('DCR_WINDOW_TITLE', config.gui.window_title)
        config.gui.grid_rows = int(os.getenv('DCR_GRID_ROWS', config.gui.grid_rows))
        config.gui.grid_cols = int(os.getenv('DCR_GRID_COLS', config.gui.grid_cols))
        config.gui.frame_update_ms = int(os.getenv('DCR_FRAME_UPDATE_MS', config.gui.frame_update_ms))

        # Logging config
        config.logging.level = os.getenv('DCR_LOG_LEVEL', config.logging.level).upper()
        config.logging.file = os.getenv('DCR_LOG_FILE', config.logging.file)

        return config

    @classmethod
    def load_from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            config = cls()

            # Load server config
            if 'server' in data:
                for key, value in data['server'].items():
                    if hasattr(config.server, key):
                        setattr(config.server, key, value)

            # Load airplay config
            if 'airplay' in data:
                for key, value in data['airplay'].items():
                    if hasattr(config.airplay, key):
                        setattr(config.airplay, key, value)

            # Load mdns config
            if 'mdns' in data:
                for key, value in data['mdns'].items():
                    if hasattr(config.mdns, key):
                        setattr(config.mdns, key, value)

            # Load gui config
            if 'gui' in data:
                for key, value in data['gui'].items():
                    if hasattr(config.gui, key):
                        setattr(config.gui, key, value)

            # Load logging config
            if 'logging' in data:
                for key, value in data['logging'].items():
                    if hasattr(config.logging, key):
                        setattr(config.logging, key, value)

            logger.info(f"Configuration loaded from {config_path}")
            return config

        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            return cls()

    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        data = {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'use_ssl': self.server.use_ssl,
                'cert_file': self.server.cert_file,
                'key_file': self.server.key_file,
                'max_streams': self.server.max_streams,
            },
            'airplay': {
                'enabled': self.airplay.enabled,
                'use_uxplay': self.airplay.use_uxplay,
                'uxplay_name': self.airplay.uxplay_name,
                'port': self.airplay.port,
                'video_port': self.airplay.video_port,
            },
            'mdns': {
                'enabled': self.mdns.enabled,
                'service_name': self.mdns.service_name,
            },
            'gui': {
                'window_title': self.gui.window_title,
                'grid_rows': self.gui.grid_rows,
                'grid_cols': self.gui.grid_cols,
                'frame_update_ms': self.gui.frame_update_ms,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
            }
        }

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Configuration saved to {config_path}")


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        # Try to load from file first, then fall back to environment
        config_file = os.getenv('DCR_CONFIG_FILE', 'config.json')
        if os.path.exists(config_file):
            _config = AppConfig.load_from_file(config_file)
        else:
            _config = AppConfig.load_from_env()
    return _config


def set_config(config: AppConfig):
    """Set the global configuration instance"""
    global _config
    _config = config
