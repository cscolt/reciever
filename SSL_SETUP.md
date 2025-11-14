# SSL Certificate Setup Guide

## Why You Need This

WebRTC screen sharing **requires HTTPS**. Browsers won't allow screen capture over plain HTTP for security reasons. That's why you're seeing:
```
WARNING:server:SSL certificates not found, falling back to HTTP
```

## Quick Setup (3 Steps)

### Step 1: Generate Certificates

**Option A - PowerShell (Recommended):**
```powershell
.\generate_ssl_cert.ps1
```

**Option B - Batch File:**
```cmd
generate_ssl_simple.bat
```

This creates two files:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

### Step 2: Copy Certificates to Executable Folder

```powershell
# Copy the certificates to where the executable is
Copy-Item cert.pem, key.pem .\dist\DesktopCastingReceiver\
```

**OR** if running from source:
```powershell
# The certificates are already in the right place (current directory)
# No copying needed!
```

### Step 3: Run the Application

```powershell
# If using executable
cd .\dist\DesktopCastingReceiver\
.\DesktopCastingReceiver.exe

# If running from source
python run.py
```

You should now see:
```
INFO:server:Starting server on https://0.0.0.0:8080
```

## Connecting from Chromebooks

1. On each Chromebook, open Chrome browser
2. Visit: `https://YOUR-COMPUTER-IP:8080`
3. You'll see a security warning (this is normal for self-signed certificates)
4. Click "Advanced" or "Show Details"
5. Click "Proceed to [IP]" or "Accept the Risk and Continue"
6. Enter a name and click "Start Sharing Screen"

## Troubleshooting

### Error: "Script execution is disabled"
```powershell
# Run this first
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "cryptography module not found"
```powershell
pip install cryptography
```

### Error: "OpenSSL not found"
- The scripts will automatically use Python's cryptography library as a fallback
- Or download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html

### Certificates Generated But Still HTTP
- Make sure `cert.pem` and `key.pem` are in the SAME folder as the .exe
- Check the console - it should say "Starting server on **https**://..."

## Running from Source (Development)

If you're running from source with `python run.py`:

1. Generate certificates in the project root:
   ```powershell
   .\generate_ssl_cert.ps1
   ```

2. Run:
   ```powershell
   python run.py
   ```

The certificates in the project root will be automatically used.

## Certificate Expiration

The generated certificates are valid for 365 days. After that, regenerate them by running the generation script again.
