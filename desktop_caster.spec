# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all zeroconf data, binaries, and metadata
zeroconf_datas, zeroconf_binaries, zeroconf_hiddenimports = collect_all('zeroconf')
ifaddr_datas, ifaddr_binaries, ifaddr_hiddenimports = collect_all('ifaddr')

a = Analysis(
    ['viewer.py'],
    pathex=[],
    binaries=zeroconf_binaries + ifaddr_binaries,
    datas=[
        ('client.html', '.'),
        ('server.py', '.'),
        ('airplay_receiver.py', '.'),
        ('uxplay_integration.py', '.'),
        ('mdns_discovery.py', '.'),
    ] + zeroconf_datas + ifaddr_datas,
    hiddenimports=[
        'aiortc',
        'aiohttp',
        'av',
        'opencv-python',
        'numpy',
        'PIL',
        'PIL._tkinter_finder',
        'websockets',
        # Zeroconf - using collect_all but keeping these for completeness
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
        'ifaddr',  # Required by zeroconf for network interface detection
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
