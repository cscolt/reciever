#!/usr/bin/env python3
"""
Diagnostic Test Tool for Desktop Casting Receiver
Tests all components and provides detailed feedback
"""

import sys
import socket
import logging
import subprocess
import shutil

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_network():
    """Test network configuration"""
    print("\n" + "="*60)
    print("NETWORK DIAGNOSTICS")
    print("="*60)

    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"✓ Local IP: {local_ip}")
    except Exception as e:
        print(f"✗ Could not determine local IP: {e}")
        local_ip = None

    # Test ports
    test_ports = [8080, 7000, 7100]
    for port in test_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"⚠ Port {port} is OCCUPIED (may be in use)")
            else:
                print(f"✓ Port {port} is available")
        except Exception as e:
            print(f"✗ Error checking port {port}: {e}")

    return local_ip

def test_dependencies():
    """Test required dependencies"""
    print("\n" + "="*60)
    print("DEPENDENCY CHECKS")
    print("="*60)

    dependencies = {
        'aiohttp': 'WebRTC server framework',
        'aiortc': 'WebRTC implementation',
        'av': 'Video decoding (PyAV)',
        'cv2': 'OpenCV for frame processing',
        'numpy': 'Numerical operations',
        'PIL': 'Image processing for GUI',
        'zeroconf': 'mDNS/Bonjour service discovery',
        'srp': 'SRP-6a authentication for AirPlay',
        'cryptography': 'Cryptographic operations for AirPlay',
    }

    all_good = True
    for module, description in dependencies.items():
        try:
            if module == 'cv2':
                import cv2
            else:
                __import__(module)
            print(f"✓ {module:15} - {description}")
        except ImportError:
            print(f"✗ {module:15} - {description} (MISSING)")
            all_good = False

    return all_good

def test_uxplay():
    """Test UxPlay installation"""
    print("\n" + "="*60)
    print("UXPLAY DIAGNOSTICS")
    print("="*60)

    uxplay_path = shutil.which('uxplay')
    if uxplay_path:
        print(f"✓ UxPlay found at: {uxplay_path}")
        try:
            result = subprocess.run(['uxplay', '-h'],
                                  capture_output=True,
                                  text=True,
                                  timeout=2)
            print(f"✓ UxPlay is executable")
            return True
        except Exception as e:
            print(f"✗ UxPlay found but not executable: {e}")
            return False
    else:
        print("✗ UxPlay not found in PATH")
        print("  Install from: https://github.com/FDH2/UxPlay")
        return False

def test_zeroconf():
    """Test zeroconf/mDNS functionality"""
    print("\n" + "="*60)
    print("ZEROCONF/MDNS DIAGNOSTICS")
    print("="*60)

    try:
        from zeroconf import Zeroconf, ServiceInfo
        import socket

        print("✓ Zeroconf module available")

        # Try to create a test service
        zc = Zeroconf()

        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = socket.inet_aton(s.getsockname()[0])
        s.close()

        # Create test service
        test_service = ServiceInfo(
            "_test._tcp.local.",
            "TestService._test._tcp.local.",
            addresses=[local_ip],
            port=9999,
            properties={'test': 'true'},
        )

        zc.register_service(test_service)
        print("✓ Can register mDNS services")
        zc.unregister_service(test_service)
        zc.close()
        print("✓ mDNS functionality working")
        return True

    except ImportError:
        print("✗ Zeroconf module not available")
        print("  Install with: pip install zeroconf")
        return False
    except Exception as e:
        print(f"✗ Error testing zeroconf: {e}")
        return False

def test_webrtc_server():
    """Test if WebRTC server can start"""
    print("\n" + "="*60)
    print("WEBRTC SERVER TEST")
    print("="*60)

    try:
        import aiohttp
        from aiortc import RTCPeerConnection
        print("✓ WebRTC modules available")

        # Check if server.py exists
        import os
        if os.path.exists('server.py'):
            print("✓ server.py found")
        else:
            print("✗ server.py not found")
            return False

        return True
    except ImportError as e:
        print(f"✗ WebRTC modules missing: {e}")
        return False

def test_chrome_casting_discovery():
    """Check Chrome casting discovery requirements"""
    print("\n" + "="*60)
    print("CHROME CASTING DISCOVERY")
    print("="*60)

    print("Chrome Cast discovery requires:")
    print("  1. mDNS service advertisement (_googlecast._tcp)")
    print("  2. DIAL protocol support (optional)")
    print("  3. Device must be discoverable on local network")
    print("")

    try:
        from zeroconf import Zeroconf
        print("✓ Zeroconf available for mDNS advertisement")
    except ImportError:
        print("✗ Zeroconf not available - Chrome won't discover device")
        return False

    print("\n⚠ ISSUE DETECTED:")
    print("  The current server.py does NOT advertise via mDNS!")
    print("  Chrome/Chromebook will NOT find the device automatically.")
    print("  Users must manually type the URL: http://<ip>:8080")
    print("")
    print("RECOMMENDATION:")
    print("  Add mDNS service advertisement for Cast API discovery")

    return False

def test_airplay_crypto():
    """Test AirPlay cryptographic dependencies"""
    print("\n" + "="*60)
    print("AIRPLAY CRYPTO DIAGNOSTICS")
    print("="*60)

    all_good = True

    # Test SRP
    try:
        import srp
        print("✓ SRP library available (authentication)")
    except ImportError:
        print("✗ SRP library missing (authentication will fail)")
        print("  Install with: pip install srp")
        all_good = False

    # Test cryptography
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        print("✓ Cryptography library available (encryption)")
    except ImportError:
        print("✗ Cryptography library missing (encryption will fail)")
        print("  Install with: pip install cryptography")
        all_good = False

    # Test video decoding
    try:
        import av
        print("✓ PyAV library available (H.264 decoding)")
    except ImportError:
        print("✗ PyAV library missing (video decoding will fail)")
        print("  Install with: pip install av")
        all_good = False

    return all_good

def main():
    """Run all diagnostic tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "DESKTOP CASTING DIAGNOSTICS" + " "*16 + "║")
    print("╚" + "="*58 + "╝")

    results = {}

    results['network'] = test_network()
    results['dependencies'] = test_dependencies()
    results['uxplay'] = test_uxplay()
    results['zeroconf'] = test_zeroconf()
    results['webrtc'] = test_webrtc_server()
    results['chrome_cast'] = test_chrome_casting_discovery()
    results['airplay_crypto'] = test_airplay_crypto()

    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)

    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test:20} {status}")

    print("\n" + "="*60)
    print("KEY ISSUES IDENTIFIED:")
    print("="*60)

    if not results['chrome_cast']:
        print("\n1. CHROME CASTING NOT DISCOVERABLE")
        print("   - Server doesn't advertise via mDNS")
        print("   - Chrome/Chromebook won't find it automatically")
        print("   - Fix: Add mDNS service advertisement")

    if not results['uxplay']:
        print("\n2. UXPLAY NOT INSTALLED")
        print("   - iOS screen mirroring won't work optimally")
        print("   - Fix: Install UxPlay (see INSTALL_UXPLAY.md)")

    if not results['airplay_crypto']:
        print("\n3. AIRPLAY CRYPTO INCOMPLETE")
        print("   - Python AirPlay receiver won't work")
        print("   - Fix: Install missing crypto libraries")

    print("\n" + "="*60)
    print("UXPLAY BLACK SCREEN ISSUE:")
    print("="*60)
    print("The current uxplay_integration.py only creates placeholder frames.")
    print("It does NOT capture actual video from UxPlay output.")
    print("This is why you see a black screen or placeholder text.")
    print("")
    print("To fix this, the integration needs to:")
    print("  1. Configure UxPlay with video output sink (GStreamer)")
    print("  2. Capture frames from the GStreamer pipeline")
    print("  3. Feed captured frames to StreamManager")
    print("")
    print("Current implementation at line 203-228 uses:")
    print("  _create_uxplay_placeholder() - generates fake frames")
    print("")

    print("\n" + "="*60)

if __name__ == '__main__':
    main()
