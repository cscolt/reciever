# Chrome & Chromebook Screen/Tab Casting Guide

Desktop Casting Receiver supports **three casting modes** from Chrome/Chromebook:

## Casting Options

### 1. 🌐 Chrome Tab Casting (Recommended for Presentations)
Cast a single Chrome tab - perfect for presentations, videos, or web applications.

**Benefits:**
- Only shares one tab (other tabs stay private)
- Can include **tab audio** (great for videos/presentations)
- Better performance than full screen capture
- Recipient sees exactly what you're presenting

**How to cast a Chrome tab:**
1. Visit `https://<server-ip>:8080` in Chrome
2. Click "Start Sharing"
3. In the dialog, select the **"Chrome Tab"** option
4. Choose which tab to share
5. Check **"Share tab audio"** if you want audio (optional)
6. Click "Share"

### 2. 🪟 Window Casting
Cast a specific application window.

**How to cast a window:**
1. Visit `https://<server-ip>:8080` in Chrome
2. Click "Start Sharing"
3. Select the **"Window"** option
4. Choose which window to share
5. Click "Share"

### 3. 🖥️ Entire Screen Casting
Cast your entire screen (all monitors).

**How to cast entire screen:**
1. Visit `https://<server-ip>:8080` in Chrome
2. Click "Start Sharing"
3. Select the **"Entire Screen"** option
4. Choose which screen to share (if multiple monitors)
5. Click "Share"

## Chromebook-Specific Features

Chromebooks have excellent built-in support for screen sharing:
- **Fast performance** - Hardware-accelerated capture
- **Low latency** - Direct Chrome integration
- **Tab audio** - Capture audio from YouTube, Netflix, presentations, etc.
- **Battery efficient** - Optimized for Chromebook hardware

## Requirements

### For Chrome/Chromebook Casting:
- **Chrome version:** 72+ (for getDisplayMedia API)
- **Chrome version:** 94+ (for enhanced tab selection)
- **Connection:** HTTPS required (self-signed cert is okay)
- **Network:** Same WiFi network as the monitoring station

### For Tab Audio:
- **Chrome version:** 74+
- **Must select "Share tab audio"** checkbox in the sharing dialog
- Audio only works when casting a **Chrome tab** (not entire screen)

## Usage Examples

### Example 1: Share a YouTube Video with Audio
1. Open YouTube in a Chrome tab
2. Visit the casting page in another tab
3. Click "Start Sharing"
4. Select "Chrome Tab"
5. Choose the YouTube tab
6. ✅ **Check "Share tab audio"**
7. Click "Share"

Result: Recipient sees video with audio!

### Example 2: Present Google Slides
1. Open your Google Slides presentation
2. Visit the casting page in another tab
3. Click "Start Sharing"
4. Select "Chrome Tab"
5. Choose the Slides tab
6. Click "Share"
7. Switch back to Slides tab and present

Result: Recipients see your slides in real-time!

### Example 3: Share Your Entire Chromebook Screen
1. Visit the casting page
2. Click "Start Sharing"
3. Select "Entire Screen"
4. Click "Share"

Result: Recipients see everything on your screen!

## Troubleshooting

### Chrome won't show the sharing dialog
- **Cause:** Not using HTTPS or localhost
- **Solution:** Make sure you're accessing via `https://` (not `http://`)
- Accept the self-signed certificate warning in Chrome

### "Share tab audio" option is grayed out
- **Cause:** You selected "Entire Screen" or "Window" instead of "Chrome Tab"
- **Solution:** Audio only works with Chrome Tab sharing

### Casting is laggy or choppy
- **Try these:**
  1. Switch from "Entire Screen" to "Chrome Tab" (better performance)
  2. Close other tabs and applications
  3. Ensure you're on the same WiFi network (not cellular)
  4. Check WiFi signal strength

### "getDisplayMedia is not defined" error
- **Cause:** Very old Chrome version or not using HTTPS
- **Solution:** Update Chrome to version 72+ and use HTTPS

## Privacy Note

- **Chrome Tab casting:** Only the selected tab is shared (safest)
- **Window casting:** Only the selected window is shared
- **Entire Screen casting:** Everything on your screen is visible

Always double-check what you've selected before clicking "Share"!

## Advanced: Testing Your Setup

To verify screen/tab casting is working:

1. **Start the server:**
   ```bash
   # Windows
   .\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe

   # Linux/Mac
   ./dist/DesktopCastingReceiver/DesktopCastingReceiver
   ```

2. **Note the server IP address** shown in the console

3. **From Chrome/Chromebook:**
   - Navigate to `https://<server-ip>:8080`
   - Accept the certificate warning (click "Advanced" → "Proceed")
   - Enter your name
   - Click "Start Sharing"
   - Select "Chrome Tab"
   - Choose a tab with content (e.g., YouTube)
   - Check "Share tab audio" if desired
   - Click "Share"

4. **Check the monitoring station** - Your tab should appear in the viewer!

## What Gets Displayed

The web interface will show exactly what you're casting:

- **Chrome Tab** → Shows as "Chrome Tab" or "Chrome Tab + Audio"
- **Window** → Shows as "Window"
- **Entire Screen** → Shows as "Screen Sharing"

The monitoring station operator can see what mode you're using!
