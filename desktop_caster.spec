# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['viewer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('client.html', '.'),
        ('server.py', '.'),
        ('airplay_receiver.py', '.'),
        ('uxplay_integration.py', '.'),
    ],
    hiddenimports=[
        'aiortc',
        'aiohttp',
        'av',
        'opencv-python',
        'numpy',
        'PIL',
        'websockets',
        'zeroconf',
        'zeroconf._utils',
        'zeroconf._utils.ipaddress',
        'zeroconf._logger',
        'zeroconf._services',
        'zeroconf._services.browser',
        'zeroconf._services.registry',
        'plistlib',
        'ipaddress',
        'socket',
    ],
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
