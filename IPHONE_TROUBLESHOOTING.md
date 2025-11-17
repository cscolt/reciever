# iPhone Mirroring Troubleshooting Guide

## Quick Diagnostic
Run the diagnostic tool first:
```bash
python3 tests/test_iphone_connection.py
```

## Common Issues & Solutions

### Issue 1: iPhone Can't See Device in AirPlay Menu

**Symptoms:**
- "Desktop Casting Receiver" doesn't appear in Control Center → Screen Mirroring

**Solutions:**
1. **Check same network**: Ensure iPhone and computer are on same WiFi network
2. **Restart mDNS**:
   ```bash
   # Kill any running instances
   pkill -f python3.*run.py
   pkill -f uxplay

   # Wait 5 seconds
   sleep 5

   # Start fresh
   python3 run.py
   ```

3. **Check firewall**:
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 7100/tcp
   sudo ufw allow 7000/tcp
   sudo ufw allow 5353/udp

   # Or disable temporarily to test
   sudo ufw disable
   ```

4. **Verify UxPlay is advertising**:
   ```bash
   # Check if uxplay process is running
   ps aux | grep uxplay

   # Check logs for "raop" service
   journalctl -f | grep -i airplay
   ```

### Issue 2: Connection Fails / Drops Immediately

**Symptoms:**
- Device appears in AirPlay menu
- Connection starts but immediately drops
- Error message on iPhone

**Solutions:**
1. **Check SSL certificates**:
   ```bash
   # Regenerate if needed
   openssl req -x509 -newkey rsa:2048 -nodes \
       -out cert.pem -keyout key.pem -days 365 \
       -subj "/C=US/ST=State/L=City/O=Desktop Casting/CN=$(hostname -I | awk '{print $1}')"
   ```

2. **Check port conflicts**:
   ```bash
   # See what's using ports
   sudo lsof -i :7100
   sudo lsof -i :7000

   # Kill conflicting processes
   sudo kill <PID>
   ```

3. **Test UxPlay directly** (bypasses Python):
   ```bash
   # Run UxPlay standalone
   uxplay -n "Test Receiver" -p

   # Try connecting from iPhone
   # If this works, Python integration may have issue
   ```

### Issue 3: Connects But No Video Appears

**Symptoms:**
- Connection succeeds
- GUI shows stream as "active"
- But no video frames displayed

**Solutions:**
1. **Check GStreamer pipeline**:
   ```bash
   # Test GStreamer
   gst-launch-1.0 videotestsrc ! autovideosink

   # If that fails, reinstall
   sudo apt-get install --reinstall gstreamer1.0-tools gstreamer1.0-plugins-base
   ```

2. **Enable debug logging**:
   ```bash
   # Run with debug mode
   DCR_LOG_LEVEL=DEBUG python3 run.py

   # Watch for errors in output
   ```

3. **Check UxPlay video capture**:
   - The refactored code uses placeholder frames if GStreamer fails
   - Look for log messages about "placeholder" or "capture method"

### Issue 4: Browser Method Doesn't Work

**Symptoms:**
- Visiting https://192.168.1.49:8080 in iPhone Safari doesn't work
- Certificate errors
- Camera not accessible

**Solutions:**
1. **Accept SSL certificate**:
   - Visit the URL in Safari
   - Tap "Show Details" → "Visit this website"
   - **Important**: Must click "Visit Website" to trust certificate

2. **Enable camera permissions**:
   - Settings → Safari → Camera → Ask
   - Refresh the page

3. **Try different browser**:
   - Safari is recommended
   - Chrome on iOS has limited WebRTC support

## Testing Workflow

### Step 1: Start with Diagnostics
```bash
python3 tests/test_iphone_connection.py
```

### Step 2: Start Server with Debug Logging
```bash
DCR_LOG_LEVEL=DEBUG python3 run.py
```

### Step 3: Monitor Logs
Watch for these key messages:
- `✓ UxPlay started successfully` - AirPlay service started
- `✓ mDNS services advertised` - Discovery working
- `Authenticated <device>` - iPhone connected
- `raop_rtp_mirror starting mirroring` - Video stream started

### Step 4: Test Connection from iPhone

#### Method 1: AirPlay Screen Mirroring (Preferred)
1. Open Control Center (swipe down from top-right)
2. Tap "Screen Mirroring"
3. Select "Desktop Casting Receiver"
4. Enter code if prompted (usually not needed)
5. Check GUI - should show your iPhone screen

#### Method 2: Browser Camera Streaming (Fallback)
1. Open Safari on iPhone
2. Visit: `https://192.168.1.49:8080`
3. Accept certificate warning
4. Click "Start Streaming"
5. Allow camera access
6. Check GUI - should show camera feed

## Still Not Working?

### Collect Debug Info
```bash
# Run with full debugging
DCR_LOG_LEVEL=DEBUG python3 run.py 2>&1 | tee debug.log

# Try to connect from iPhone

# Save the logs
# The debug.log file will contain detailed information
```

### Check System-Wide Issues
```bash
# Check if avahi-daemon is running (needed for mDNS)
systemctl status avahi-daemon

# Restart if needed
sudo systemctl restart avahi-daemon

# Check network interfaces
ip addr show
```

### Network Configuration
```bash
# Get your IP
hostname -I

# Test mDNS resolution
avahi-browse -rt _airplay._tcp

# Should show "Desktop Casting Receiver"
```

## Known Limitations

1. **iOS Version**: Requires iOS 9+ for AirPlay, iOS 11+ for screen recording in browser
2. **Network**: Both devices must be on same subnet (check IP ranges match)
3. **Video Quality**: May be lower than native AirPlay due to GStreamer limitations
4. **Latency**: Expect 100-500ms delay (normal for AirPlay)

## Alternative: Use Old Version
If the refactored version has issues:
```bash
# Switch back to master branch
git checkout master

# Run old version
python3 viewer.py
```

## Report Issues
If none of these solutions work, please provide:
1. Output from `python3 tests/test_iphone_connection.py`
2. Debug logs from `DCR_LOG_LEVEL=DEBUG python3 run.py`
3. iPhone iOS version
4. Exact error messages
5. Whether UxPlay standalone works: `uxplay -n "Test" -p`
