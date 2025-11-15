# Generate Self-Signed SSL Certificate for Desktop Casting Receiver
# This creates cert.pem and key.pem files needed for HTTPS

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSL Certificate Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if OpenSSL is available
$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $opensslPath) {
    Write-Host "OpenSSL not found. Trying to use Windows certutil..." -ForegroundColor Yellow
    Write-Host ""

    # Get local IP
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

    if (-not $localIP) {
        $localIP = "localhost"
    }

    Write-Host "Your local IP: $localIP" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Manual Certificate Creation Required" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OpenSSL is not installed. You have two options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Install OpenSSL (Recommended)" -ForegroundColor Cyan
    Write-Host "  1. Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
    Write-Host "     Get: Win64 OpenSSL v3.x.x Light MSI" -ForegroundColor White
    Write-Host "  2. Install it" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Use Pre-made Certificates" -ForegroundColor Cyan
    Write-Host "  I can create certificates using Python's built-in tools..." -ForegroundColor White
    Write-Host ""

    $response = Read-Host "Try creating certificates with Python? (Y/n)"
    if ($response -eq "n" -or $response -eq "N") {
        Write-Host "Cancelled. Install OpenSSL and run this script again." -ForegroundColor Red
        exit 1
    }

    # Create Python script to generate certificates
    Write-Host ""
    Write-Host "Generating certificates with Python..." -ForegroundColor Yellow

    $pythonScript = @'
import ssl
import socket
from datetime import datetime, timedelta
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

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
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Desktop Casting"),
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
            x509.IPAddress(__import__('ipaddress').ip_address(local_ip)),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write private key
    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("SUCCESS")
    print(f"Certificates generated for IP: {local_ip}")

except ImportError:
    print("ERROR: cryptography package not installed")
    print("Install with: pip install cryptography")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
'@

    $pythonScript | Out-File -Encoding UTF8 "temp_cert_gen.py"

    # Try to generate with Python
    $result = python temp_cert_gen.py 2>&1
    Remove-Item "temp_cert_gen.py" -ErrorAction SilentlyContinue

    if ($result -match "SUCCESS") {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Certificates Generated Successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Files created:" -ForegroundColor Cyan
        Write-Host "  cert.pem - SSL certificate" -ForegroundColor White
        Write-Host "  key.pem  - Private key" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now start the server with HTTPS support!" -ForegroundColor Green
        exit 0
    } elseif ($result -match "cryptography package not installed") {
        Write-Host ""
        Write-Host "Installing cryptography package..." -ForegroundColor Yellow
        pip install cryptography

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Retrying certificate generation..." -ForegroundColor Yellow
            $pythonScript | Out-File -Encoding UTF8 "temp_cert_gen.py"
            $result = python temp_cert_gen.py 2>&1
            Remove-Item "temp_cert_gen.py" -ErrorAction SilentlyContinue

            if ($result -match "SUCCESS") {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "Certificates Generated Successfully!" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Files created:" -ForegroundColor Cyan
                Write-Host "  cert.pem - SSL certificate" -ForegroundColor White
                Write-Host "  key.pem  - Private key" -ForegroundColor White
                Write-Host ""
                Write-Host "You can now start the server with HTTPS support!" -ForegroundColor Green
                exit 0
            }
        }

        Write-Host ""
        Write-Host "Failed to generate certificates." -ForegroundColor Red
        Write-Host "Please install OpenSSL or contact support." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host ""
        Write-Host "Failed to generate certificates: $result" -ForegroundColor Red
        Write-Host "Please install OpenSSL." -ForegroundColor Yellow
        exit 1
    }

} else {
    Write-Host "OpenSSL found: $($opensslPath.Source)" -ForegroundColor Green
    Write-Host ""

    # Get local IP
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

    if (-not $localIP) {
        $localIP = "127.0.0.1"
    }

    Write-Host "Generating certificate for IP: $localIP" -ForegroundColor Cyan
    Write-Host ""

    # Create config file for SAN (Subject Alternative Names)
    $configContent = @"
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=State
L=City
O=Desktop Casting
CN=$localIP

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = $localIP
DNS.1 = localhost
"@

    $configContent | Out-File -Encoding ASCII "openssl_temp.cnf"

    # Generate private key and certificate
    Write-Host "Generating private key and certificate..." -ForegroundColor Yellow

    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -config openssl_temp.cnf -extensions v3_req 2>&1 | Out-Null

    # Clean up config file
    Remove-Item "openssl_temp.cnf" -ErrorAction SilentlyContinue

    if ((Test-Path "cert.pem") -and (Test-Path "key.pem")) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Certificates Generated Successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Files created:" -ForegroundColor Cyan
        Write-Host "  cert.pem - SSL certificate" -ForegroundColor White
        Write-Host "  key.pem  - Private key" -ForegroundColor White
        Write-Host ""
        Write-Host "Certificate details:" -ForegroundColor Cyan
        Write-Host "  IP Address: $localIP" -ForegroundColor White
        Write-Host "  Valid for: 365 days" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT: Chromebooks will show a security warning!" -ForegroundColor Yellow
        Write-Host "To connect:" -ForegroundColor Yellow
        Write-Host "  1. Visit https://$localIP:8080" -ForegroundColor White
        Write-Host "  2. Click 'Advanced' or 'Show details'" -ForegroundColor White
        Write-Host "  3. Click 'Proceed to $localIP' or 'Accept the risk'" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now start the Desktop Casting Receiver!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "ERROR: Failed to generate certificates" -ForegroundColor Red
        Write-Host "Check if OpenSSL is properly installed" -ForegroundColor Yellow
        exit 1
    }
}
