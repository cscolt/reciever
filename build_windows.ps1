# Windows Build Script for Desktop Casting Receiver
# This script automates the build process on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Desktop Casting Receiver - Windows Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Extract major.minor version
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $majorVersion = [int]$Matches[1]
    $minorVersion = [int]$Matches[2]

    if ($majorVersion -eq 3 -and $minorVersion -ge 14) {
        Write-Host ""
        Write-Host "WARNING: Python 3.14+ detected!" -ForegroundColor Red
        Write-Host "Many packages don't have pre-built wheels for Python 3.14 yet." -ForegroundColor Red
        Write-Host ""
        Write-Host "RECOMMENDED SOLUTIONS:" -ForegroundColor Yellow
        Write-Host "1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "2. Use py launcher: py -3.11 build_windows.ps1" -ForegroundColor Yellow
        Write-Host "3. Install Visual Studio Build Tools (see README)" -ForegroundColor Yellow
        Write-Host ""
        $response = Read-Host "Continue anyway? Some packages may fail to install (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "Build cancelled." -ForegroundColor Red
            exit 1
        }
    }
}

# Create/activate virtual environment
Write-Host ""
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

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
Write-Host ""

# First try with flexible requirements
if (Test-Path "requirements-flexible.txt") {
    Write-Host "Using flexible requirements for Python 3.12+ compatibility..." -ForegroundColor Gray
    pip install -r requirements-flexible.txt
} else {
    pip install -r requirements.txt
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common causes:" -ForegroundColor Yellow
    Write-Host "1. Missing Visual Studio Build Tools" -ForegroundColor Yellow
    Write-Host "   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
    Write-Host "   Install 'Desktop development with C++' workload" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Python version compatibility" -ForegroundColor Yellow
    Write-Host "   Python 3.11 or 3.12 recommended" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Network issues" -ForegroundColor Yellow
    Write-Host "   Check your internet connection" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To see detailed error, run manually:" -ForegroundColor Cyan
    Write-Host "  .\venv_build\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Dependencies installed successfully!" -ForegroundColor Green

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
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Missing dependencies" -ForegroundColor Yellow
    Write-Host "- Incorrect Python version" -ForegroundColor Yellow
    Write-Host "- Missing build tools" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
