# Quick Fix for iPhone Mirroring

## The Issue
You're seeing a GStreamer error and no video. This is because of a race condition where Python tries to read video frames before UxPlay is ready.

## Solution 1: Wait for iPhone to Connect First (Simplest)

The shared memory socket (`/tmp/uxplay_frames`) is only created **after** an iPhone connects. Try this:

```bash
# 1. Start the application
cd ~/Documents/github/reciever
python3 run.py

# 2. WAIT for it to fully start (you'll see "Running on https://...")

# 3. Connect your iPhone AFTER the app is running
#    Control Center → Screen Mirroring → "Desktop Casting Receiver"

# 4. Check logs - you should see:
#    "✓ Shared memory socket found after X.Xs"
#    "✓ GStreamer pipeline started successfully"
#    "✓ iOS device authenticated: [your iPhone name]"
#    "✓ Screen mirroring started: [your iPhone name]"
```

## Solution 2: Clean Start

If that doesn't work, clean up and restart:

```bash
# 1. Kill everything
pkill -9 python3
pkill -9 uxplay

# 2. Clean shared memory
rm -f /tmp/uxplay_frames

# 3. Wait 5 seconds
sleep 5

# 4. Start fresh
cd ~/Documents/github/reciever
DCR_LOG_LEVEL=DEBUG python3 run.py

# 5. Connect iPhone after "Running on https://..." appears
```

## Solution 3: Test UxPlay Directly

To verify UxPlay works without Python:

```bash
# 1. Test UxPlay standalone
uxplay -n "Test" -p

# 2. Connect iPhone (Control Center → Screen Mirroring → "Test")

# 3. You should see video in a window

# 4. If this works, Python integration is the issue
# 5. If this doesn't work, UxPlay itself has a problem
```

## What the Latest Fix Does

The code now:
1. ✅ Waits up to 10 seconds for UxPlay to create the shared memory socket
2. ✅ Checks if the socket exists before trying to read
3. ✅ Handles GStreamer pipeline startup errors gracefully
4. ✅ Better error handling if frames fail to capture

## Expected Log Output (Success)

```
INFO - Starting shared memory frame capture...
INFO - Waiting for UxPlay to create shared memory at /tmp/uxplay_frames...
INFO - ✓ Shared memory socket found after 2.5s
DEBUG - GStreamer pipeline: shmsrc socket-path=/tmp/uxplay_frames...
INFO - ✓ GStreamer pipeline started successfully
INFO - ✓ iOS device authenticated: iPhone
INFO - ✓ Screen mirroring started: iPhone
DEBUG - Frame captured and distributed to 1 client(s)
```

## If You Still See Errors

### Check if GStreamer bindings are really installed:
```bash
python3 -c "
from gi.repository import Gst, GLib
print('✓ GStreamer bindings OK')
Gst.init(None)
print('✓ Gst.init() OK')
"
```

### Check UxPlay command:
```bash
# Find the UxPlay process
ps aux | grep uxplay

# Should see something like:
# uxplay -n Desktop Casting Receiver -p -vs videoconvert ! ... ! shmsink socket-path=/tmp/uxplay_frames ...
```

### Check if shmsink plugin exists:
```bash
gst-inspect-1.0 shmsink
```

If that command fails, install:
```bash
sudo apt-get install gstreamer1.0-plugins-bad
```

## Alternative: Use Browser Method

If AirPlay continues to have issues, use the browser method:

1. On iPhone, open Safari
2. Visit: `https://192.168.1.49:8080`
3. Accept certificate warning
4. Click "Start Streaming"
5. Allow camera access
6. Video works via WebRTC (not AirPlay)

This bypasses UxPlay/GStreamer entirely!

## Still Not Working?

Run with full debug:
```bash
cd ~/Documents/github/reciever
DCR_LOG_LEVEL=DEBUG python3 run.py 2>&1 | tee iphone-debug.log
```

Then connect iPhone and share the `iphone-debug.log` file.

## Summary

**Most likely cause:** You connected iPhone before the app finished starting
**Quick fix:** Start app first, THEN connect iPhone
**Alternative:** Use browser method (Safari → https://192.168.1.49:8080)
