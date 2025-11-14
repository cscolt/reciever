@echo off
echo ========================================
echo SSL Certificate Generator (Simple)
echo ========================================
echo.

REM Try using Python cryptography
python -c "import cryptography" >nul 2>&1
if errorlevel 1 (
    echo Installing cryptography package...
    pip install cryptography
    if errorlevel 1 (
        echo ERROR: Failed to install cryptography
        echo Please run: generate_ssl_cert.ps1
        pause
        exit /b 1
    )
)

echo Generating SSL certificates...
echo.

python -c "import socket, ipaddress; from cryptography import x509; from cryptography.x509.oid import NameOID; from cryptography.hazmat.primitives import hashes; from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; from cryptography.hazmat.backends import default_backend; from datetime import datetime, timedelta; private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend()); hostname = socket.gethostname(); local_ip = socket.gethostbyname(hostname); subject = issuer = x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'), x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'State'), x509.NameAttribute(NameOID.LOCALITY_NAME, 'City'), x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Desktop Casting'), x509.NameAttribute(NameOID.COMMON_NAME, local_ip)]); cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(private_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname), x509.DNSName('localhost'), x509.IPAddress(ipaddress.ip_address(local_ip))]), critical=False).sign(private_key, hashes.SHA256(), default_backend()); open('key.pem', 'wb').write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())); open('cert.pem', 'wb').write(cert.public_bytes(serialization.Encoding.PEM)); print(f'\nSUCCESS! Certificates generated for {local_ip}')"

if exist cert.pem (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Files created:
    echo   cert.pem - SSL certificate
    echo   key.pem  - Private key
    echo.
    echo These files need to be in the same folder as the executable.
    echo.
    echo You can now start the Desktop Casting Receiver!
    echo.
) else (
    echo.
    echo ERROR: Failed to generate certificates
    echo Try running: generate_ssl_cert.ps1
    echo.
)

pause
