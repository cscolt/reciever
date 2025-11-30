# Google Cast Setup Guide

This guide explains how to set up and use Google Cast functionality with Desktop Casting Receiver, allowing managed Chromebooks and Android devices to cast their screens even when blocked from visiting arbitrary URLs.

## Overview

The Cast implementation allows devices to connect using the Google Cast protocol, which appears as the "Cast" button in Chrome and Android. This is particularly useful for managed/enterprise devices where URL access is restricted but Cast functionality is enabled.

## How It Works

1. **Discovery**: Your receiver advertises itself as a Cast target using mDNS (Google Cast protocol)
2. **Connection**: Devices discover the receiver in their Cast menu
3. **Protocol**: Cast handles the connection protocol, WebRTC handles the actual video streaming
4. **Integration**: Cast streams appear alongside WebRTC and AirPlay streams in your monitoring GUI

## Architecture

```
Chromebook/Android Device
    ↓
Cast Button → Discovers "Desktop Casting Receiver" via mDNS
    ↓
User selects receiver and chooses "Cast Screen/Tab"
    ↓
Cast SDK establishes session
    ↓
WebRTC connection set up for video streaming
    ↓
Stream appears in Desktop Casting Receiver GUI
```

## Prerequisites

1. **Python Dependencies**: Already included in requirements.txt
   - `zeroconf` for mDNS discovery
   - `aiohttp` for HTTP server
   - `aiortc` for WebRTC

2. **Network**: All devices must be on the same local network

3. **Google Cast Developer Account** (required for full functionality):
   - Free account at https://cast.google.com/publish/

## Setup Steps

### Step 1: Register Your Cast Receiver Application

1. Go to https://cast.google.com/publish/
2. Sign in with your Google account
3. Click "Add New Application"
4. Choose "Custom Receiver"
5. Fill in the form:
   - **Name**: Desktop Casting Receiver (or your preferred name)
   - **Receiver Application URL**: This will be your server's Cast receiver URL
     - Format: `http://YOUR_SERVER_IP:8080/cast_receiver` (or `https://` if using SSL)
     - Example: `http://192.168.1.100:8080/cast_receiver`
   - **Category**: Education, Utilities, or appropriate category

6. Click "Save"
7. **Copy your Application ID** - it looks like: `ABCD1234` (8 alphanumeric characters)
8. **Publish your app**:
   - For testing: Leave as "Unpublished" and add test device serial numbers
   - For production: Submit for review (takes a few days)

### Step 2: Configure Your Server

The server automatically starts Cast discovery when you run it. No additional configuration needed!

```bash
# Start the server with Cast enabled (enabled by default)
python run.py
```

You should see:
```
✓ Google Cast discovery enabled - receiver will appear in Cast menus
  Cast receiver URL: http://192.168.1.100:8080/cast_receiver
```

### Step 3: Note Your Receiver URL

From the server logs, note your Cast receiver URL. You'll need this for:
1. Registering with Google Cast Developer Console (Step 1)
2. Testing the Cast sender page

### Step 4: Configure Test Devices (During Testing Phase)

If your app is "Unpublished" (during testing):

1. Get device serial numbers:
   - **Chrome**: Visit `chrome://cast/#devices` → find "Serial number"
   - **Android**: Settings → About Phone → Status → Serial Number

2. In Cast Developer Console:
   - Go to your app
   - Add serial numbers under "Cast SDK Additional Data"

3. Devices must be on the same Google account as the developer account

### Step 5: Test the Connection

#### Option A: Using Chrome's Built-in Cast Button

1. On a Chromebook or Chrome browser:
   - Click the **Cast button** in the Chrome toolbar (⏏️ icon)
   - Or right-click on any web page → "Cast..."
   - Or visit any site and look for the Cast icon

2. You should see "Desktop Casting Receiver" in the list

3. Select it → Choose "Cast tab" or "Cast screen"

4. Your screen should appear in the Desktop Casting Receiver monitoring GUI!

#### Option B: Using the Cast Sender Page

For testing or manual connections:

1. Visit: `http://YOUR_SERVER_IP:8080/cast_sender`

2. Enter:
   - Device name (e.g., "John's Laptop")
   - Your Cast Application ID from Step 1

3. Click "Initialize Cast SDK"

4. Click "Start Casting"

5. Select what to share (screen/window/tab)

6. Stream appears in the monitoring GUI

## Multiple Simultaneous Streams

The receiver supports up to 8 simultaneous Cast streams (configurable in `server.py`). Each Cast sender creates an independent stream that appears in the monitoring grid.

## Troubleshooting

### Receiver Not Appearing in Cast Menu

**Problem**: "Desktop Casting Receiver" doesn't show up when clicking Cast button

**Solutions**:
1. **Check network**: All devices must be on same network/VLAN
2. **Check firewall**: Port 8080 must be accessible
3. **Restart mDNS**: Restart the server application
4. **Check zeroconf**: Ensure `pip install zeroconf` is installed
5. **Check logs**: Look for "Cast discovery enabled" message
6. **Try manual discovery**: Some networks block mDNS - use Cast sender page instead

### "App Not Available" Error

**Problem**: Receiver appears but shows "App not available" when selected

**Solutions**:
1. **Verify App ID**: Ensure your Application ID is correct
2. **Check receiver URL**: Must match exactly what's in Google Cast Console
3. **Publish status**: For testing, ensure device serial number is registered
4. **SSL certificate**: If using HTTPS, ensure certificate is trusted

### Cast Connects But No Video

**Problem**: Cast session starts but no video stream appears

**Solutions**:
1. **Check permissions**: Grant screen capture permissions when prompted
2. **Check WebRTC**: Ensure port 8080 is open for WebRTC traffic
3. **Check browser console**: Look for WebRTC errors (F12 → Console)
4. **Try different source**: Try "Cast tab" instead of "Cast screen"

### Managed Device Can't Cast

**Problem**: Chromebook shows Cast button but can't connect

**Solutions**:
1. **Admin console**: Check Chrome policy for Cast settings
2. **Allowed apps**: Your Cast App ID may need to be allowlisted
3. **Network policy**: Some MDM solutions block Cast protocol
4. **Contact admin**: May need to enable "Cast to local devices"

## URL Access Points

After setup, these URLs are available:

- **Cast Receiver** (for Google Cast Developer Console):
  - `http://YOUR_IP:8080/cast_receiver`
  - This is what you register with Google

- **Cast Sender** (for manual testing):
  - `http://YOUR_IP:8080/cast_sender`
  - Use this to test casting from any browser

- **WebRTC Client** (original method):
  - `http://YOUR_IP:8080/`
  - Direct WebRTC connection without Cast protocol

- **Server Status**:
  - `http://YOUR_IP:8080/status`
  - JSON endpoint showing active streams

## Comparing Methods

| Feature | WebRTC Direct | Google Cast | AirPlay |
|---------|--------------|-------------|---------|
| Chrome/Chromebook | ✅ (via URL) | ✅ (via Cast button) | ❌ |
| Android | ✅ (via URL) | ✅ (via Cast button) | ❌ |
| iOS/iPad | ⚠️ (camera only) | ❌ | ✅ |
| Works on managed devices | ❌ (URL blocked) | ✅ (Cast allowed) | ✅ |
| Requires registration | ❌ | ✅ (Google account) | ❌ |
| Screen mirroring | ✅ | ✅ | ✅ |
| Tab casting | ✅ | ✅ | ❌ |
| Multiple streams | ✅ | ✅ | ✅ |

## Network Configuration

### Firewall Rules

Ensure these ports are open:

- **8080/TCP**: HTTP server (or your configured port)
- **5353/UDP**: mDNS (for Cast discovery)
- **WebRTC**: Ephemeral UDP ports for media streaming

### Enterprise/School Networks

If deploying in an enterprise or school:

1. **Work with IT**: Get ports allowlisted
2. **Static IP**: Use a static IP for your server
3. **DNS**: Consider adding a local DNS entry
4. **MDM**: Add Cast App ID to allowed list
5. **VLAN**: Ensure devices and server are on same VLAN

## Advanced Configuration

### Changing Max Streams

Edit `server.py` line 119:

```python
stream_manager = StreamManager(max_streams=16)  # Change from 8 to 16
```

### Changing Server Port

Edit `server.py` line 288:

```python
def run_server(host='0.0.0.0', port=9000, ...):  # Change port
```

**Important**: Update Cast receiver URL in Google Cast Console!

### Disable Cast (Keep WebRTC Only)

Edit `server.py` line 288:

```python
def run_server(..., enable_cast=False):
```

Or start with:
```python
run_server(enable_cast=False)
```

### Custom Receiver Name

Edit `cast_discovery.py` or pass to `CastDiscovery`:

```python
cast_discovery = CastDiscovery("My Custom Receiver", port, protocol)
```

## Security Considerations

### SSL/HTTPS (Recommended)

Cast works with both HTTP and HTTPS, but HTTPS is recommended:

1. Generate certificates (see main README.md)
2. Place `cert.pem` and `key.pem` in the server directory
3. Server automatically uses HTTPS if certificates present
4. Update Cast receiver URL to use `https://`

### Network Isolation

- Use a dedicated VLAN for monitoring if possible
- Restrict access to the server port via firewall
- Consider VPN access for remote monitoring

### Data Privacy

- All streams are local (nothing sent to cloud)
- WebRTC connections are peer-to-peer
- Cast protocol is only for session management
- Consider enabling encryption for sensitive environments

## Support and Resources

- **Google Cast Documentation**: https://developers.google.com/cast/
- **Cast Developer Console**: https://cast.google.com/publish/
- **WebRTC Documentation**: https://webrtc.org/
- **Desktop Casting Receiver Issues**: https://github.com/your-repo/issues

## FAQ

**Q: Do I need to register with Google for testing?**
A: Yes, you need an Application ID. But you can test with "Unpublished" status by registering device serial numbers.

**Q: Can I use this in a classroom?**
A: Yes! This is perfect for classroom monitoring. Register your Cast app, allowlist it in your MDM, and students can cast without visiting URLs.

**Q: Does this work offline?**
A: Yes for local network. Cast discovery uses mDNS (local). Registration is one-time only.

**Q: How many devices can cast simultaneously?**
A: Default is 8 streams. Configurable up to your hardware limits.

**Q: What's the video quality?**
A: WebRTC adapts to network conditions. Typically 720p-1080p at 15-30 FPS.

**Q: Can I use this commercially?**
A: Check Google Cast terms of service. This software is open-source (check LICENSE).

## Example: School Deployment

**Scenario**: Monitor 6 student Chromebooks during a computer lab

**Setup**:
1. Register Cast app with "Education" category
2. Submit for Google approval (1-3 days)
3. Add Cast App ID to Chrome admin allowlist
4. Set up server on dedicated machine
5. Share instructions with students: "Click Cast → Select 'Lab Monitor' → Cast Screen"

**Benefits**:
- Works even with restricted browsing
- No URL to remember or type
- Appears as native Chrome feature
- Admin can push Cast target via policy

## Next Steps

1. ✅ Complete Google Cast registration
2. ✅ Test with one device
3. ✅ Add more devices
4. ✅ Configure your monitoring GUI layout
5. ✅ Deploy to your environment

For questions or issues, check the logs in the server console or create an issue on GitHub.
