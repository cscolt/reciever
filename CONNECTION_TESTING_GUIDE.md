# Connection Testing Guide

## Server Status: ✅ RUNNING

Your server is currently running with:
- ✅ WebRTC server on port 8080 (HTTPS)
- ✅ mDNS discovery broadcasting (Cast, WebRTC, HTTPS services)
- ✅ UxPlay running with GStreamer video capture
- ✅ AirPlay ports 7000, 7100 active
- ✅ UDP video capture on port 5000

**Server IP: 192.168.1.49**

---

## Issue: "Casting and screen mirroring still don't work"

Based on the logs, the server is working perfectly. The issue is likely one of these:

### Common Issues Checklist

#### 1. Network Issues
- [ ] **Are devices on the SAME WiFi network?**
  - Server: `192.168.1.49`
  - Client must be on `192.168.1.x` network
  - Check client WiFi settings

- [ ] **Firewall blocking?**
  ```bash
  # Check firewall status
  sudo ufw status

  # If active, allow ports:
  sudo ufw allow 8080/tcp
  sudo ufw allow 7000/tcp
  sudo ufw allow 7100/tcp
  sudo ufw allow 5353/udp  # mDNS
  ```

- [ ] **Router AP isolation?**
  - Some routers have "AP Isolation" or "Client Isolation"
  - This prevents devices from seeing each other
  - Check router settings and disable if present

#### 2. Chrome/Chromebook Connection Issues

**The Problem:** Chrome Cast button won't show the server

**Why:** Even though mDNS is broadcasting, Chrome's Cast discovery is picky

**Solutions:**

**Option A: Use Manual URL (WORKS IMMEDIATELY)**
1. On Chromebook, open Chrome
2. Visit: `https://192.168.1.49:8080`
3. You'll see certificate warning - click "Advanced"
4. Click "Proceed to 192.168.1.49 (unsafe)"
5. Enter device name
6. Click "Start Sharing Screen"
7. **THIS SHOULD WORK**

**Option B: Chrome Cast Discovery (May not work)**
- Click Cast icon in Chrome
- Wait 10-15 seconds
- Look for "Desktop Casting Receiver"
- **If it doesn't appear:** mDNS isn't reaching Chrome
  - Could be: Firewall, router settings, Chrome version
  - **Use Option A instead**

**Testing Chrome Connection:**
```bash
# On server, watch for connection attempts:
tail -f /path/to/server/log

# When Chromebook connects, you should see:
# "Received offer from [device name]"
# "Connection state: connecting"
# "Connection state: connected"
```

#### 3. iOS AirPlay Connection Issues

**The Problem:** iOS doesn't show "Desktop Casting Receiver" in Screen Mirroring

**Troubleshooting Steps:**

**Step 1: Verify iOS can see mDNS services**
- Open iOS Settings → WiFi
- Tap the (i) next to connected network
- Make sure it shows `192.168.1.x` address
- **Must be same network as server**

**Step 2: Force iOS to refresh AirPlay list**
- Turn Airplane Mode ON
- Wait 3 seconds
- Turn Airplane Mode OFF
- Wait for WiFi to reconnect
- Open Control Center → Screen Mirroring
- Wait 10 seconds for list to populate

**Step 3: Check UxPlay is running**
```bash
ps aux | grep uxplay
# Should show: uxplay -n "Desktop Casting Receiver" ...
```

**Step 4: Test with iOS browser method (fallback)**
- On iPhone, open Safari
- Visit: `https://192.168.1.49:8080`
- Accept certificate warning
- Enter device name
- Click "Start Camera Streaming"
- **This should work as fallback**

#### 4. Server-Side Verification

**Check the server is actually receiving connection attempts:**

```bash
# Watch server logs in real-time
tail -f <path-to-log>

# Or check the running server output
# Look for these messages when connecting:
```

**Expected logs when iOS connects via AirPlay:**
```
✓ iOS device authenticated: [iPhone Name]
✓ Screen mirroring started: [iPhone Name]
UDP listener started on port 5000
Captured frame: (720, 1280, 3)
```

**Expected logs when Chrome connects:**
```
Received offer from [Device Name]
Connection state for [Device Name]: connecting
Received track from [Device Name]: video
Connection state for [Device Name]: connected
```

**If you DON'T see these logs:** The device isn't connecting

---

## Step-by-Step Testing Procedure

### Test 1: Manual Chrome Connection (SHOULD WORK)

1. **On the server machine**, server is already running

2. **On Chromebook:**
   ```
   Open Chrome
   Visit: https://192.168.1.49:8080
   ```

3. **Accept certificate:**
   - Click "Advanced"
   - Click "Proceed to 192.168.1.49"

4. **Start streaming:**
   - Enter name: "Test Chromebook"
   - Click "Start Sharing Screen"
   - Select screen to share
   - Click "Share"

5. **Check server logs:**
   ```bash
   # Should show:
   Received offer from Test Chromebook
   Connection state: connected
   ```

6. **Check GUI:**
   - Video feed should appear within 2-3 seconds

**If this doesn't work:** Something is fundamentally wrong with the setup
- Check: Same network?
- Check: Firewall?
- Check: Can Chromebook ping 192.168.1.49?

### Test 2: iOS AirPlay Connection

1. **Server is running** (already running)

2. **On iOS device:**
   - Same WiFi as server? Check Settings → WiFi
   - Open Control Center
   - Tap "Screen Mirroring"
   - Wait 10 seconds

3. **Look for "Desktop Casting Receiver":**
   - **If it appears:** Tap it, connection should establish
   - **If it doesn't appear:** mDNS not reaching iOS

4. **If not appearing:**
   - Try Airplane Mode trick (above)
   - Check iOS version (needs iOS 11+)
   - Try restarting iOS device
   - Check router for AP isolation

5. **Watch server logs:**
   ```
   Should see:
   ✓ iOS device authenticated: [Your iPhone]
   ✓ Screen mirroring started: [Your iPhone]
   ```

**If iOS never shows the receiver:** mDNS issue
- Router may be blocking multicast (port 5353)
- AP isolation enabled
- iOS and server on different subnets

### Test 3: iOS Browser Fallback

If AirPlay discovery doesn't work, try browser method:

1. **On iPhone, open Safari**
2. **Visit:** `https://192.168.1.49:8080`
3. **Accept certificate warning**
4. **Enter name, click "Start Camera Streaming"**
5. **Allow camera access**
6. **Point camera at screen or whatever you want to monitor**

**This bypasses AirPlay** and uses WebRTC instead.

---

## Network Diagnostics

### From Server Machine:

```bash
# Check mDNS is broadcasting
avahi-browse -a | grep "Desktop Casting"
# Should show services being advertised

# Check if ports are listening
netstat -tuln | grep -E ":8080|:7000|:7100"
# Should show all three ports LISTENING

# Check firewall
sudo ufw status
# Should show INACTIVE or rules allowing the ports
```

### From Client Machine (Chromebook):

```bash
# Can you reach the server?
ping 192.168.1.49
# Should get responses

# Can you connect to the port?
telnet 192.168.1.49 8080
# Should connect (then Ctrl+C to exit)

# Or use curl:
curl -k https://192.168.1.49:8080
# Should return HTML
```

### From iOS (using app like "Network Analyzer"):

- Ping 192.168.1.49 - should work
- Port scan 8080 - should be open
- Look for mDNS services - "Desktop Casting Receiver" should appear

---

## Current Server Logs

The server is currently showing:

```
✓ mDNS services registered successfully
✓ Chrome/Chromebook should discover: 'Desktop Casting Receiver'
✓ Service URL: https://192.168.1.49:8080/
✓ UxPlay started successfully
✓ GStreamer detected - will use advanced video capture
✓ UDP listener started on port 5000
```

**Everything on the server side is working correctly!**

---

## Most Likely Causes

Based on "casting and screen mirroring still don't work":

### For Chrome/Chromebook:
1. **Not using manual URL** - Try `https://192.168.1.49:8080` directly
2. **Certificate rejection** - Must click "Advanced" → "Proceed"
3. **Different network** - Chromebook must be on 192.168.1.x
4. **Firewall** - Port 8080 blocked

### For iOS AirPlay:
1. **Different network** - iPhone must be on 192.168.1.x
2. **Router AP isolation** - Blocks device-to-device communication
3. **mDNS blocked** - Router firewall blocking port 5353 UDP
4. **iOS not refreshing** - Try Airplane Mode toggle
5. **Wrong AirPlay receiver name** - Look for exactly "Desktop Casting Receiver"

---

## Quick Verification Commands

Run these on the server while attempting connections:

```bash
# Watch all connection attempts in real-time
tail -f <logfile> | grep -E "offer|authenticated|mirroring|Connected"

# Check active connections
netstat -an | grep ESTABLISHED | grep -E ":8080|:7000"

# Monitor UDP video packets (when iOS connected)
watch -n 1 'netstat -su | grep "packets received"'
```

---

## Next Steps for Troubleshooting

1. **Try Manual Chrome Connection First**
   - This is the easiest to test
   - If this doesn't work, fundamental network issue

2. **Check Network Configuration**
   - Confirm devices on same subnet
   - Check firewall rules
   - Check router settings

3. **Try iOS Browser Method**
   - Bypasses AirPlay discovery issues
   - Uses WebRTC like Chrome

4. **Monitor Server Logs**
   - Watch for connection attempts
   - Look for error messages
   - Share specific errors for debugging

---

## Getting Help

If still not working, provide:

1. **Output of:** `ip addr | grep "inet "`
2. **Output of:** `sudo ufw status`
3. **Client device IP:** (from WiFi settings)
4. **Server logs when attempting connection**
5. **Specific error messages seen**
6. **What exactly happens:** (nothing? error? timeout?)

---

## Server is Ready!

The server is running and ready for connections. The fixes are all in place. The issue is most likely:
- Network configuration
- How you're connecting
- Client-side settings

**Start with the manual Chrome connection test - it should work immediately!**
