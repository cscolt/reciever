# Easy Windows Build Script - No Visual Studio Required!
# This script uses pre-built wheels to avoid compilation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Desktop Casting Receiver - Easy Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Create/activate virtual environment
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv_build") {
    Write-Host "Removing old build venv..." -ForegroundColor Gray
    Remove-Item -Recurse -Force venv_build
}

Write-Host "Creating new virtual environment..." -ForegroundColor Gray
python -m venv venv_build

Write-Host "Activating virtual environment..." -ForegroundColor Gray
& .\venv_build\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies without compilation
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "Using pre-built wheels (no compilation needed)..." -ForegroundColor Gray
Write-Host ""

# Install packages that don't require compilation first
Write-Host "Installing basic packages..." -ForegroundColor Gray
pip install --only-binary :all: aiohttp Pillow websockets pyinstaller zeroconf srp cryptography
if ($LASTEXITCODE -ne 0) {
    pip install aiohttp Pillow websockets pyinstaller zeroconf srp cryptography
}

Write-Host ""
Write-Host "Installing numpy and opencv..." -ForegroundColor Gray
pip install --only-binary :all: numpy opencv-python
if ($LASTEXITCODE -ne 0) {
    pip install numpy opencv-python
}

# Try to install av with pre-built wheel
Write-Host ""
Write-Host "Installing av (video library)..." -ForegroundColor Gray
Write-Host "Attempting to use pre-built wheel..." -ForegroundColor Gray

$avInstalled = $false

# Try installing av with --only-binary flag
pip install --only-binary av av 2>$null
if ($LASTEXITCODE -eq 0) {
    $avInstalled = $true
    Write-Host "  av installed successfully!" -ForegroundColor Green
} else {
    # Try without the flag (pip might find a wheel)
    Write-Host "  Trying alternative method..." -ForegroundColor Gray
    pip install av 2>$null
    if ($LASTEXITCODE -eq 0) {
        $avInstalled = $true
        Write-Host "  av installed successfully!" -ForegroundColor Green
    }
}

if (-not $avInstalled) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "WARNING: Could not install 'av' package" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The 'av' package is required by aiortc for video processing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "1. Install Visual Studio Build Tools (5+ GB download)" -ForegroundColor White
    Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Download pre-built wheel from:" -ForegroundColor White
    Write-Host "   https://github.com/PyAV-Org/PyAV/releases" -ForegroundColor Gray
    Write-Host "   Look for: av-*-cp312-cp312-win_amd64.whl" -ForegroundColor Gray
    Write-Host "   Then run: pip install path\to\downloaded.whl" -ForegroundColor Gray
    Write-Host ""

    $response = Read-Host "Would you like to try opening the PyAV releases page? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://github.com/PyAV-Org/PyAV/releases"
    }

    Write-Host ""
    Write-Host "Build cancelled. Install 'av' package and run this script again." -ForegroundColor Red
    exit 1
}

# Install aiortc
Write-Host ""
Write-Host "Installing aiortc (WebRTC library)..." -ForegroundColor Gray
pip install aiortc
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to install aiortc!" -ForegroundColor Red
    Write-Host "This might require Visual Studio Build Tools." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "All dependencies installed successfully!" -ForegroundColor Green

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
}

# Build with PyInstaller
Write-Host ""
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
Write-Host ""

pyinstaller desktop_caster.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  .\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe" -ForegroundColor White
    Write-Host ""

    # iOS Screen Mirroring Information
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "iOS Screen Mirroring Support" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "[OK] Built-in Python AirPlay receiver included!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Features:" -ForegroundColor Cyan
    Write-Host "  - Native AirPlay protocol support" -ForegroundColor White
    Write-Host "  - Real cryptography (SRP-6a, Ed25519, ChaCha20)" -ForegroundColor White
    Write-Host "  - H.264 video decoding" -ForegroundColor White
    Write-Host "  - No external dependencies required" -ForegroundColor White
    Write-Host ""
    Write-Host "iOS devices will automatically discover this receiver" -ForegroundColor Yellow
    Write-Host "in Control Center > Screen Mirroring" -ForegroundColor Yellow
    Write-Host ""

    # Offer to set up SSL certificates
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Optional: SSL Certificate Setup" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "SSL certificates enable HTTPS connections, which are required for:" -ForegroundColor Yellow
    Write-Host "  - Screen sharing on many browsers" -ForegroundColor White
    Write-Host "  - Camera access on mobile devices" -ForegroundColor White
    Write-Host "  - AirPlay screen mirroring from iOS devices" -ForegroundColor White
    Write-Host ""

    $sslResponse = Read-Host "Would you like to generate SSL certificates now? (Y/n)"
    if ($sslResponse -ne "n" -and $sslResponse -ne "N") {
        Write-Host ""
        Write-Host "Generating SSL certificates..." -ForegroundColor Yellow

        # Check if cryptography is installed
        python -c "import cryptography" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing cryptography package..." -ForegroundColor Gray
            pip install cryptography
        }

        # Generate certificates using embedded Python script
        $pythonScript = @'
import socket
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import os

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Get hostname and IP
hostname = socket.gethostname()
try:
    local_ip = socket.gethostbyname(hostname)
except:
    local_ip = '127.0.0.1'

# Create certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'State'),
    x509.NameAttribute(NameOID.LOCALITY_NAME, 'City'),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Desktop Casting'),
    x509.NameAttribute(NameOID.COMMON_NAME, local_ip),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.utcnow()
).not_valid_after(
    datetime.utcnow() + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName(hostname),
        x509.DNSName('localhost'),
        x509.IPAddress(ipaddress.ip_address(local_ip)),
    ]),
    critical=False,
).sign(private_key, hashes.SHA256(), default_backend())

# Write to dist folder
dist_path = r'.\dist\DesktopCastingReceiver'

with open(os.path.join(dist_path, 'key.pem'), 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open(os.path.join(dist_path, 'cert.pem'), 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f'SUCCESS|{local_ip}')
'@

        $tempScript = "temp_ssl_setup.py"
        $pythonScript | Out-File -Encoding UTF8 $tempScript
        $result = python $tempScript 2>&1
        Remove-Item $tempScript -ErrorAction SilentlyContinue

        if ($result -match 'SUCCESS\|(.+)') {
            $localIP = $Matches[1]
            Write-Host ""
            Write-Host "SSL certificates created successfully!" -ForegroundColor Green
            Write-Host "  cert.pem and key.pem in .\dist\DesktopCastingReceiver\" -ForegroundColor White
            Write-Host ""
            Write-Host "Your local IP: $localIP" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Devices can connect via:" -ForegroundColor Yellow
            Write-Host "  https://$localIP:8080" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "Warning: SSL certificate generation failed" -ForegroundColor Yellow
            Write-Host "You can generate them later using: .\setup_ssl_for_exe.ps1" -ForegroundColor Gray
        }
    }

    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Cyan
    Write-Host "  cd dist\DesktopCastingReceiver" -ForegroundColor White
    Write-Host "  .\DesktopCastingReceiver.exe" -ForegroundColor White
    Write-Host ""

    # Offer to run the executable
    $runResponse = Read-Host "Would you like to run the executable now? (y/N)"
    if ($runResponse -eq "y" -or $runResponse -eq "Y") {
        Write-Host ""
        Write-Host "Starting Desktop Casting Receiver..." -ForegroundColor Green
        Start-Process ".\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe"
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for errors." -ForegroundColor Yellow
    exit 1
}
