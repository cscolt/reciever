# Testing and Connection Guide

This guide covers testing Desktop Casting Receiver functionality and troubleshooting connection issues.

## Table of Contents
- [Quick Testing](#quick-testing)
- [Testing Chrome/Chromebook Casting](#testing-chromechromebook-casting)
- [Testing iOS AirPlay](#testing-ios-airplay)
- [Network Diagnostics](#network-diagnostics)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Debug Mode](#debug-mode)

---

## Quick Testing

### Start the Server

**From Source:**
```bash
# Linux/macOS
source venv/bin/activate
python run.py

# Windows
.\venv\Scripts\Activate.ps1
python run.py
```

**From Executable:**
```bash
# Navigate to dist directory
cd dist/DesktopCastingReceiver
./DesktopCastingReceiver  # Linux/macOS
DesktopCastingReceiver.exe  # Windows
```

### Expected Startup Messages

Look for these success indicators:
```
✓ Server started on port 8080
✓ mDNS discovery enabled - Chrome/Chromebook can discover this device
✓ Service URL: http://YOUR_IP:8080/
```

If UxPlay is installed:
```
✓ UxPlay started successfully - iOS devices can mirror via AirPlay
✓ GStreamer detected - will use advanced video capture
```

---

## Testing Chrome/Chromebook Casting

### Method 1: Automatic Discovery (Recommended)

1. **Start the server** (see above)
2. **On Chrome/Chromebook:**
   - Click the Cast icon or visit chrome://cast
   - Wait 5-10 seconds for device discovery
   - Look for "Desktop Casting Receiver" in the list
   - Click to connect

### Method 2: Manual URL Connection

This method works even if automatic discovery fails:

1. **Find your server IP:**
   ```bash
   # Linux/macOS
   ip addr | grep "inet " | grep -v "127.0.0.1"
   ifconfig | grep "inet " | grep -v "127.0.0.1"

   # Windows
   ipconfig | findstr "IPv4"
   ```

2. **On Chrome browser:**
   - Open: `http://YOUR_SERVER_IP:8080`
   - Or with SSL: `https://YOUR_SERVER_IP:8080`

3. **Accept certificate** (if using HTTPS):
   - Click "Advanced"
   - Click "Proceed to [IP address]"

4. **Enter device name** and click "Start Sharing Screen"

5. **Select screen/window** to share and click "Share"

### Expected Console Output

When a Chrome client connects, the server should show:
```
Received offer from [Device Name]
Connection state: connecting
Received track: video
Connection state: connected
```

### Verification

- Video should appear in the GUI within 2-3 seconds
- Check GUI for the stream in one of the 8 slots
- Video should update in real-time

---

## Testing iOS AirPlay

### Prerequisites

- iOS device and server must be on the same WiFi network
- Server must be running
- Optional: UxPlay installed for screen mirroring (see [INSTALL_UXPLAY.md](INSTALL_UXPLAY.md))

### Connection Method 1: AirPlay Screen Mirroring (with UxPlay)

1. **Verify UxPlay is running:**
   ```bash
   # Check for these messages on startup:
   ✓ UxPlay started successfully
   ✓ GStreamer detected - will use advanced video capture
   ```

2. **On iOS device:**
   - Open Control Center:
     - iPhone X+: Swipe down from top-right
     - iPhone 8 or earlier: Swipe up from bottom
     - iPad: Swipe down from top-right
   - Tap "Screen Mirroring"
   - Wait 5-10 seconds for list to populate
   - Look for "Desktop Casting Receiver"
   - Tap to connect

3. **Expected console output:**
   ```
   ✓ iOS device authenticated: [iPhone Name]
   ✓ Screen mirroring started: [iPhone Name]
   UDP listener started on port 5000
   Captured frame: (720, 1280, 3)
   ```

4. **Verification:**
   - Your iOS screen should appear in the GUI
   - Video should be real-time
   - Check for actual screen content (not placeholders)

### Connection Method 2: Browser Camera Streaming (Fallback)

If AirPlay doesn't work or UxPlay isn't installed:

1. **On iPhone/iPad, open Safari**
2. **Visit:** `http://YOUR_SERVER_IP:8080`
3. **Accept certificate warning** (if using HTTPS)
4. **Enter device name**
5. **Click "Start Camera Streaming"**
6. **Allow camera access**
7. **Point camera at what you want to monitor**

This uses WebRTC camera streaming instead of screen mirroring.

---

## Network Diagnostics

### Server-Side Checks

**Check server is listening:**
```bash
# Linux/macOS
netstat -tuln | grep -E ":8080|:7000|:7100"
lsof -i :8080

# Windows
netstat -an | findstr ":8080"
```

Should show ports LISTENING.

**Check mDNS is broadcasting:**
```bash
# Linux (requires avahi-utils)
avahi-browse -a | grep "Desktop Casting"

# macOS
dns-sd -B _http._tcp
```

**Check firewall status:**
```bash
# Linux (UFW)
sudo ufw status

# Linux (firewalld)
sudo firewall-cmd --list-all

# Windows
Get-NetFirewallProfile | Select-Object Name, Enabled
```

### Client-Side Checks

**Test basic connectivity:**
```bash
# Can you reach the server?
ping YOUR_SERVER_IP

# Can you connect to the port?
telnet YOUR_SERVER_IP 8080

# Or use curl:
curl http://YOUR_SERVER_IP:8080
curl -k https://YOUR_SERVER_IP:8080  # With SSL
```

**Check network configuration:**
```bash
# Verify client and server are on same subnet
# Server: 192.168.1.10
# Client should also be: 192.168.1.x
```

---

## Troubleshooting Common Issues

### Issue: Chrome Can't Discover Server

**Symptoms:**
- Cast icon doesn't show "Desktop Casting Receiver"
- Device list is empty after waiting

**Possible Causes & Solutions:**

1. **Firewall blocking mDNS (port 5353)**
   ```bash
   # Linux
   sudo ufw allow 5353/udp
   sudo ufw allow 8080/tcp

   # Windows PowerShell (as admin)
   New-NetFirewallRule -DisplayName "mDNS" -Direction Inbound -Protocol UDP -LocalPort 5353 -Action Allow
   New-NetFirewallRule -DisplayName "WebRTC Server" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```

2. **Different networks**
   - Verify both devices show same subnet (e.g., 192.168.1.x)
   - Connect to same WiFi network

3. **Router AP isolation**
   - Check router settings for "AP Isolation" or "Client Isolation"
   - Disable if present

4. **Workaround: Use manual URL**
   - Always works: `http://YOUR_SERVER_IP:8080`
   - Bypasses discovery issues

### Issue: iOS Device Not Showing in Screen Mirroring

**Symptoms:**
- "Desktop Casting Receiver" doesn't appear in iOS Screen Mirroring list

**Possible Causes & Solutions:**

1. **Different networks**
   - Check iOS WiFi settings
   - Verify IP address is on same subnet as server

2. **iOS not refreshing AirPlay list**
   - Turn Airplane Mode ON
   - Wait 3 seconds
   - Turn Airplane Mode OFF
   - Wait for WiFi to reconnect
   - Try Screen Mirroring again

3. **mDNS blocked by router**
   - Check router firewall settings
   - Ensure multicast is allowed
   - Disable AP isolation

4. **UxPlay not running**
   ```bash
   # Check if UxPlay is running
   ps aux | grep uxplay  # Linux/macOS
   Get-Process | Select-String uxplay  # Windows
   ```

5. **Workaround: Use browser method**
   - Open Safari on iOS
   - Visit server URL
   - Use camera streaming instead

### Issue: Black Screen or Placeholder

**Symptoms:**
- Connection works but video shows black screen or placeholder text

**For UxPlay/iOS:**

1. **GStreamer not installed**
   ```bash
   # Check GStreamer
   gst-launch-1.0 --version

   # Should show version like: GStreamer 1.20.3
   ```

2. **Install GStreamer** (see [INSTALL_UXPLAY.md](INSTALL_UXPLAY.md))

3. **UDP port conflict**
   ```bash
   # Check if port 5000 is available
   netstat -an | grep 5000
   ```

**For Chrome/WebRTC:**

1. **Screen sharing permission denied**
   - Grant screen sharing permissions in browser
   - Try selecting different screen/window

2. **Browser not allowing capture**
   - Some browsers require HTTPS for screen capture
   - Generate SSL certificates (see [BUILD.md](BUILD.md))

### Issue: "Port Already in Use"

**Symptoms:**
```
Error: Address already in use: 8080
```

**Solutions:**

1. **Find what's using the port:**
   ```bash
   # Linux/macOS
   lsof -i :8080
   sudo lsof -i :7000

   # Windows
   netstat -ano | findstr ":8080"
   ```

2. **Kill the process:**
   ```bash
   # Linux/macOS
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   ```

3. **Change the port:**
   - Edit `server.py`
   - Find: `port=8080`
   - Change to different port (e.g., 8081)

### Issue: Connection Drops or Freezes

**Possible Causes:**

1. **Weak WiFi signal**
   - Move devices closer to router
   - Reduce interference

2. **Network congestion**
   - Close other streaming apps
   - Limit other network usage

3. **Insufficient bandwidth**
   - Video streaming needs ~10-50 Mbps
   - Check network speed

### Issue: SSL Certificate Warnings

**Symptoms:**
- Browser shows "Your connection is not private"
- "NET::ERR_CERT_AUTHORITY_INVALID"

**This is normal for self-signed certificates.**

**Solution:**
- Click "Advanced"
- Click "Proceed to [IP address] (unsafe)"
- Or install the certificate on the client device

---

## Debug Mode

Enable debug mode for detailed logging:

### Linux/macOS
```bash
export DEBUG=DEBUG
python run.py
```

### Windows
```powershell
$env:DEBUG="DEBUG"
python run.py
```

### Save Debug Output
```bash
# Linux/macOS
DEBUG=DEBUG python run.py 2>&1 | tee debug_output.txt

# Windows
$env:DEBUG="DEBUG"; python run.py 2>&1 | Tee-Object debug_output.txt
```

### Debug Output Includes

- Module import details
- mDNS service registration
- UxPlay stdout (line-by-line)
- UDP packet reception
- Frame capture details
- WebRTC negotiation
- AirPlay authentication steps

### Useful Debug Filters

```bash
# Watch for connection attempts
tail -f debug_output.txt | grep -E "offer|authenticated|connected"

# Watch for errors
tail -f debug_output.txt | grep -i "error\|fail\|exception"

# Watch video capture
tail -f debug_output.txt | grep -i "frame\|capture\|udp"
```

---

## Performance Monitoring

### Expected Performance

**WebRTC (Chrome/Chromebook):**
- Frame rate: 15-30 FPS
- Latency: 100-500ms
- Resolution: Original screen resolution

**AirPlay with UxPlay + GStreamer:**
- Frame rate: 15-30 FPS
- Latency: 200-800ms
- Resolution: 1280x720 RGB

### Console Messages to Monitor

**Good signs:**
```
✓ mDNS discovery enabled
✓ UxPlay started successfully
✓ GStreamer detected - will use advanced video capture
✓ iOS device authenticated: [device name]
✓ Screen mirroring started: [device name]
Captured frame: (720, 1280, 3)
Connection state: connected
```

**Warning signs:**
```
GStreamer not detected - using basic capture
UDP listener failed
mDNS discovery failed
Connection state: failed
Port already in use
```

---

## Quick Command Reference

```bash
# Run with debug output
DEBUG=DEBUG python run.py

# Check ports in use
netstat -tuln | grep -E ":8080|:7000|:7100|:5000"

# Monitor connections
watch -n 1 'netstat -an | grep ESTABLISHED | grep -E ":8080|:7000"'

# Test mDNS (Linux)
avahi-browse -a | grep "Desktop Casting"

# Test GStreamer
gst-launch-1.0 --version
gst-launch-1.0 videotestsrc ! autovideosink

# Check firewall
sudo ufw status  # Linux
Get-NetFirewallProfile  # Windows PowerShell
```

---

## Testing Checklist

Before reporting issues, verify:

- [ ] Server starts without errors
- [ ] Server IP is correct
- [ ] Client and server on same network
- [ ] Firewall allows required ports (8080, 7000, 7100, 5353)
- [ ] Can ping server from client device
- [ ] Can access server URL in browser
- [ ] Tried both automatic discovery and manual URL
- [ ] Checked debug output for specific errors
- [ ] UxPlay installed (for iOS screen mirroring)
- [ ] GStreamer installed (for real video capture)

---

## Need More Help?

- **Installation issues**: See [INSTALLATION.md](INSTALLATION.md)
- **Build problems**: See [BUILD.md](BUILD.md)
- **Runtime errors**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **iOS mirroring setup**: See [INSTALL_UXPLAY.md](INSTALL_UXPLAY.md)
- **Chrome casting info**: See [CHROME_CASTING.md](CHROME_CASTING.md)
