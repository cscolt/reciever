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
pip install --only-binary :all: aiohttp Pillow websockets pyinstaller
if ($LASTEXITCODE -ne 0) {
    pip install aiohttp Pillow websockets pyinstaller
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
    Write-Host "To run:" -ForegroundColor Cyan
    Write-Host "  cd dist\DesktopCastingReceiver" -ForegroundColor White
    Write-Host "  .\DesktopCastingReceiver.exe" -ForegroundColor White
    Write-Host ""

    # Offer to run the executable
    $response = Read-Host "Would you like to run the executable now? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
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
