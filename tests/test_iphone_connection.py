#!/usr/bin/env python3
"""
iPhone Mirroring Diagnostic Tool
Tests all components needed for iPhone screen mirroring
"""

import subprocess
import socket
import sys
import os

def check_network():
    """Check network connectivity"""
    print("\n" + "="*60)
    print("NETWORK CONNECTIVITY")
    print("="*60)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"✓ Local IP: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"✗ Network error: {e}")
        return None

def check_ports():
    """Check if required ports are available"""
    print("\n" + "="*60)
    print("PORT AVAILABILITY")
    print("="*60)

    ports = {
        8080: "WebRTC/HTTPS Server",
        7000: "Python AirPlay (fallback)",
        7100: "UxPlay Video Port",
        5353: "mDNS Discovery"
    }

    for port, service in ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"⚠ Port {port} ({service}): OCCUPIED")
            else:
                print(f"✓ Port {port} ({service}): Available")
        except Exception as e:
            print(f"✗ Port {port} ({service}): Error - {e}")

def check_uxplay():
    """Check if UxPlay is installed and working"""
    print("\n" + "="*60)
    print("UXPLAY STATUS")
    print("="*60)

    # Check if uxplay is installed
    try:
        result = subprocess.run(['which', 'uxplay'], capture_output=True, text=True)
        if result.returncode == 0:
            uxplay_path = result.stdout.strip()
            print(f"✓ UxPlay installed: {uxplay_path}")

            # Check version
            try:
                version = subprocess.run(['uxplay', '-v'], capture_output=True, text=True, timeout=2)
                print(f"  Version info: {version.stdout.strip() or version.stderr.strip()}")
            except:
                print("  (Version check failed)")

            return True
        else:
            print("✗ UxPlay NOT installed")
            print("  Install with: sudo apt-get install uxplay")
            print("  Or see: https://github.com/FDH2/UxPlay")
            return False
    except Exception as e:
        print(f"✗ Error checking UxPlay: {e}")
        return False

def check_gstreamer():
    """Check if GStreamer is installed"""
    print("\n" + "="*60)
    print("GSTREAMER STATUS")
    print("="*60)

    try:
        result = subprocess.run(['gst-launch-1.0', '--version'],
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ GStreamer installed: {version_line}")
            return True
        else:
            print("✗ GStreamer NOT installed")
            print("  Install with: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base")
            return False
    except FileNotFoundError:
        print("✗ GStreamer NOT installed")
        print("  Install with: sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base")
        return False
    except Exception as e:
        print(f"✗ Error checking GStreamer: {e}")
        return False

def check_ssl_certs():
    """Check if SSL certificates exist"""
    print("\n" + "="*60)
    print("SSL CERTIFICATES")
    print("="*60)

    cert_path = 'cert.pem'
    key_path = 'key.pem'

    cert_exists = os.path.exists(cert_path)
    key_exists = os.path.exists(key_path)

    if cert_exists and key_exists:
        print(f"✓ SSL certificates found")
        print(f"  - {cert_path}")
        print(f"  - {key_path}")
        return True
    else:
        print("⚠ SSL certificates NOT found")
        print("  Generate with: openssl req -x509 -newkey rsa:2048 -nodes \\")
        print("                           -out cert.pem -keyout key.pem -days 365")
        return False

def check_python_deps():
    """Check Python dependencies"""
    print("\n" + "="*60)
    print("PYTHON DEPENDENCIES")
    print("="*60)

    deps = ['zeroconf', 'aiohttp', 'aiortc', 'cv2', 'av', 'PIL']
    all_good = True

    for dep in deps:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - NOT INSTALLED")
            all_good = False

    if not all_good:
        print("\n  Install with: pip install -r requirements.txt")

    return all_good

def main():
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "iPhone Mirroring Diagnostic" + " "*16 + "║")
    print("╚" + "═"*58 + "╝")

    local_ip = check_network()
    check_ports()
    has_uxplay = check_uxplay()
    has_gstreamer = check_gstreamer()
    check_ssl_certs()
    has_deps = check_python_deps()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)

    if not has_deps:
        print("\n❌ CRITICAL: Python dependencies missing")
        print("   Run: pip install -r requirements.txt")
        return

    if not has_uxplay:
        print("\n⚠  WARNING: UxPlay not installed")
        print("   iOS screen mirroring will be limited to camera streaming")
        print("   For full screen mirroring, install UxPlay:")
        print("   - See: https://github.com/FDH2/UxPlay")
    elif not has_gstreamer:
        print("\n⚠  WARNING: GStreamer not installed")
        print("   UxPlay video capture won't work without GStreamer")
        print("   Install with:")
        print("   sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base")
    else:
        print("\n✓ All components for iOS screen mirroring are installed!")

    if local_ip:
        print(f"\n📱 iOS Connection Instructions:")
        print(f"   1. Ensure iPhone is on same network")
        print(f"   2. Start the receiver: python3 run.py")
        print(f"   3. On iPhone: Control Center → Screen Mirroring")
        print(f"   4. Select 'Desktop Casting Receiver'")
        print(f"   5. Or visit in browser: https://{local_ip}:8080")
        print(f"      (Accept certificate warning)")

    print("\n" + "="*60)
    print()

if __name__ == '__main__':
    main()
