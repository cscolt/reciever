# Windows PowerShell Launcher for Desktop Casting Receiver
# Run this in Windows PowerShell (not WSL) for AirPlay to work properly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Desktop Casting Receiver - Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in WSL
$isWSL = Test-Path /proc/version
if ($isWSL) {
    $wslCheck = Get-Content /proc/version | Select-String -Pattern "microsoft"
    if ($wslCheck) {
        Write-Host "WARNING: You're running this in WSL!" -ForegroundColor Red
        Write-Host "AirPlay mDNS broadcasts won't work from WSL2." -ForegroundColor Red
        Write-Host ""
        Write-Host "Please run this in Windows PowerShell instead:" -ForegroundColor Yellow
        Write-Host "  1. Open Windows PowerShell (not WSL terminal)" -ForegroundColor White
        Write-Host "  2. cd to this directory" -ForegroundColor White
        Write-Host "  3. Run: .\run_windows.ps1" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

# Find Python installation
Write-Host "Locating Python installation..." -ForegroundColor Yellow

$pythonPaths = @(
    ".\venv_py312\Scripts\python.exe",
    ".\venv\Scripts\python.exe",
    "C:\Users\control\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\control\AppData\Local\Programs\Python\Python314\python.exe",
    "python.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path -ErrorAction SilentlyContinue) {
        $pythonExe = $path
        break
    }
    # Try to find in PATH
    if ($path -eq "python.exe") {
        $found = Get-Command python -ErrorAction SilentlyContinue
        if ($found) {
            $pythonExe = "python"
            break
        }
    }
}

if (-not $pythonExe) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or activate a virtual environment." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Python: $pythonExe" -ForegroundColor Green
Write-Host ""

# Check network configuration
Write-Host "Network Configuration:" -ForegroundColor Yellow
try {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*WSL*"} | Select-Object -First 1).IPAddress
    $hostname = $env:COMPUTERNAME
    Write-Host "  Hostname: $hostname" -ForegroundColor White
    Write-Host "  IP Address: $ip" -ForegroundColor White
    Write-Host ""
    Write-Host "iOS devices should discover 'Desktop Casting Receiver' at this IP" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "  Unable to determine IP address" -ForegroundColor Yellow
    Write-Host ""
}

# Check firewall
Write-Host "Firewall Check:" -ForegroundColor Yellow
$firewallRules = Get-NetFirewallRule -DisplayName "*Python*","*AirPlay*" -ErrorAction SilentlyContinue
if ($firewallRules) {
    Write-Host "  Found firewall rules for Python/AirPlay" -ForegroundColor Green
} else {
    Write-Host "  No firewall rules found" -ForegroundColor Yellow
    Write-Host "  If AirPlay doesn't work, add firewall rule:" -ForegroundColor Yellow
    Write-Host "    Run as Administrator:" -ForegroundColor White
    Write-Host "    netsh advfirewall firewall add rule name=`"AirPlay`" dir=in action=allow protocol=TCP localport=7000" -ForegroundColor Gray
}
Write-Host ""

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$missingDeps = @()

$deps = @("aiohttp", "aiortc", "opencv-python", "numpy", "zeroconf", "srp", "cryptography", "av")
foreach ($dep in $deps) {
    $check = & $pythonExe -c "import $($dep.Replace('-','_'))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "  Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & $pythonExe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  All dependencies installed" -ForegroundColor Green
}
Write-Host ""

# Start the application
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Desktop Casting Receiver" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "On your iOS device:" -ForegroundColor Cyan
Write-Host "  1. Open Control Center (swipe down from top-right)" -ForegroundColor White
Write-Host "  2. Tap 'Screen Mirroring'" -ForegroundColor White
Write-Host "  3. Select 'Desktop Casting Receiver'" -ForegroundColor White
Write-Host ""
Write-Host "For other devices:" -ForegroundColor Cyan
Write-Host "  Visit: https://$ip:8080" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

& $pythonExe run.py
