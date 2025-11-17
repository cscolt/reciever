# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Desktop Casting Receiver v2.0
# Updated for new refactored structure

from PyInstaller.utils.hooks import collect_all
import os

block_cipher = None

# Project root directory
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect all zeroconf and ifaddr data
zeroconf_datas, zeroconf_binaries, zeroconf_hiddenimports = collect_all('zeroconf')
ifaddr_datas, ifaddr_binaries, ifaddr_hiddenimports = collect_all('ifaddr')

a = Analysis(
    [os.path.join(project_root, 'run.py')],
    pathex=[project_root],
    binaries=zeroconf_binaries + ifaddr_binaries,
    datas=[
        # Assets
        (os.path.join(project_root, 'assets', 'client.html'), 'assets'),
        # Source modules (include all src/ directory)
        (os.path.join(project_root, 'src'), 'src'),
    ] + zeroconf_datas + ifaddr_datas,
    hiddenimports=[
        # Core dependencies
        'aiortc',
        'aiohttp',
        'av',
        'cv2',
        'numpy',
        'PIL',
        'websockets',
        'tkinter',
        # Zeroconf dependencies
        'zeroconf',
        'zeroconf._cache',
        'zeroconf._core',
        'zeroconf._dns',
        'zeroconf._engine',
        'zeroconf._exceptions',
        'zeroconf._handlers',
        'zeroconf._history',
        'zeroconf._listener',
        'zeroconf._logger',
        'zeroconf._protocol',
        'zeroconf._record_update',
        'zeroconf._services',
        'zeroconf._services.browser',
        'zeroconf._services.info',
        'zeroconf._services.registry',
        'zeroconf._transport',
        'zeroconf._updates',
        'zeroconf._utils',
        'zeroconf._utils.asyncio',
        'zeroconf._utils.ipaddress',
        'zeroconf._utils.name',
        'zeroconf._utils.net',
        'zeroconf._utils.time',
        'zeroconf.asyncio',
        'zeroconf.const',
        'plistlib',
        'ipaddress',
        'socket',
        'ifaddr',
        # SRP and Cryptography
        'srp',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.asymmetric.ed25519',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.ciphers.aead',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.hkdf',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'hashlib',
        'hmac',
        # New modules from refactored structure
        'src',
        'src.common',
        'src.webrtc',
        'src.gui',
        'src.discovery',
        'src.airplay',
        'src.app',
    ] + zeroconf_hiddenimports + ifaddr_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DesktopCastingReceiver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DesktopCastingReceiver',
)
