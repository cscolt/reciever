# All-in-one script to generate SSL certificates and set up the executable

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSL Setup for Desktop Casting Receiver" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if executable exists
$exePath = ".\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: Executable not found at:" -ForegroundColor Red
    Write-Host "  $exePath" -ForegroundColor White
    Write-Host ""
    Write-Host "Please build the executable first:" -ForegroundColor Yellow
    Write-Host "  .\build_windows_easy.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Executable found!" -ForegroundColor Green
Write-Host ""

# Step 2: Install cryptography if needed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -c "import cryptography" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing cryptography package..." -ForegroundColor Gray
    pip install cryptography
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to install cryptography" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Generate certificates
Write-Host "Generating SSL certificates..." -ForegroundColor Yellow

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
import os
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
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Setup Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "SSL certificates created and copied to:" -ForegroundColor Cyan
    Write-Host "  .\dist\DesktopCastingReceiver\cert.pem" -ForegroundColor White
    Write-Host "  .\dist\DesktopCastingReceiver\key.pem" -ForegroundColor White
    Write-Host ""
    Write-Host "Your local IP: $localIP" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Yellow
    Write-Host "  cd .\dist\DesktopCastingReceiver" -ForegroundColor White
    Write-Host "  .\DesktopCastingReceiver.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "On Chromebooks, visit:" -ForegroundColor Yellow
    Write-Host "  https://$localIP:8080" -ForegroundColor White
    Write-Host ""
    Write-Host "IMPORTANT:" -ForegroundColor Yellow
    Write-Host "  When you first visit the URL, you'll see a security warning." -ForegroundColor White
    Write-Host "  Click 'Advanced' then 'Proceed to $localIP' to continue." -ForegroundColor White
    Write-Host ""

    $response = Read-Host "Would you like to start the application now? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host ""
        Write-Host "Starting Desktop Casting Receiver..." -ForegroundColor Green
        Write-Host ""
        Start-Process ".\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe"
    }

} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: Failed to generate certificates" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error details: $result" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
