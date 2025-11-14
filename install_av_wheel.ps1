# Script to download and install pre-built av wheel for Python 3.12

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PyAV Wheel Installer for Python 3.12" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = & python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow

if ($pythonVersion -notmatch "3\.12") {
    Write-Host ""
    Write-Host "WARNING: This script is for Python 3.12" -ForegroundColor Yellow
    Write-Host "Your version: $pythonVersion" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 0
    }
}

Write-Host ""
Write-Host "Checking for pre-built av wheels..." -ForegroundColor Yellow
Write-Host ""

# Try to install av using pip (it will fetch from PyPI if available)
Write-Host "Attempting to install av from PyPI..." -ForegroundColor Gray
python -m pip install av --prefer-binary

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! av package installed" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run: .\build_windows_easy.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Failed to install av automatically" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation required:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Install Visual Studio Build Tools" -ForegroundColor Cyan
    Write-Host "  Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor White
    Write-Host "  Install: Desktop development with C++" -ForegroundColor White
    Write-Host "  Then run: pip install av" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Download pre-built wheel" -ForegroundColor Cyan
    Write-Host "  1. Visit: https://github.com/PyAV-Org/PyAV/releases" -ForegroundColor White
    Write-Host "  2. Download: av-*-cp312-cp312-win_amd64.whl" -ForegroundColor White
    Write-Host "  3. Install: pip install path\to\wheel.whl" -ForegroundColor White
    Write-Host ""

    $response = Read-Host "Open PyAV releases page in browser? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://github.com/PyAV-Org/PyAV/releases"
    }
}
