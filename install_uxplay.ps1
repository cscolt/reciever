# UxPlay Installation Script for Windows
# Automates the process of installing UxPlay for iOS screen mirroring

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UxPlay Installation Script for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you install UxPlay, enabling iOS screen mirroring" -ForegroundColor Yellow
Write-Host "for Desktop Casting Receiver." -ForegroundColor Yellow
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "âš  Warning: Not running as administrator" -ForegroundColor Yellow
    Write-Host "Some installation steps may require administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check if UxPlay is already installed
$uxplayExists = Get-Command uxplay -ErrorAction SilentlyContinue
if ($uxplayExists) {
    Write-Host "âœ“ UxPlay is already installed!" -ForegroundColor Green
    & uxplay -h 2>&1 | Select-Object -First 1
    Write-Host ""
    $reinstall = Read-Host "Do you want to reinstall/update UxPlay? (y/N)"
    if ($reinstall -ne "y" -and $reinstall -ne "Y") {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Installation Requirements" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "UxPlay on Windows requires the following:" -ForegroundColor Yellow
Write-Host "  1. Visual Studio Build Tools (C++ compiler)" -ForegroundColor White
Write-Host "  2. CMake" -ForegroundColor White
Write-Host "  3. GStreamer development libraries" -ForegroundColor White
Write-Host "  4. Git" -ForegroundColor White
Write-Host ""
Write-Host "This is a complex setup process. We'll guide you through it." -ForegroundColor Yellow
Write-Host ""

# Check for Git
Write-Host "Checking for Git..." -ForegroundColor Yellow
$gitExists = Get-Command git -ErrorAction SilentlyContinue
if ($gitExists) {
    Write-Host "  âœ“ Git is installed" -ForegroundColor Green
} else {
    Write-Host "  âœ— Git is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "  Download from: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host ""
    $openGit = Read-Host "Open Git download page in browser? (Y/n)"
    if ($openGit -ne "n" -and $openGit -ne "N") {
        Start-Process "https://git-scm.com/download/win"
    }
    Write-Host ""
    Write-Host "Please install Git and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check for CMake
Write-Host "Checking for CMake..." -ForegroundColor Yellow
$cmakeExists = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmakeExists) {
    Write-Host "  âœ“ CMake is installed" -ForegroundColor Green
    $cmakeVersion = & cmake --version 2>&1 | Select-Object -First 1
    Write-Host "    $cmakeVersion" -ForegroundColor Gray
} else {
    Write-Host "  âœ— CMake is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install CMake:" -ForegroundColor Yellow
    Write-Host "  Download from: https://cmake.org/download/" -ForegroundColor White
    Write-Host "  Choose: Windows x64 Installer" -ForegroundColor White
    Write-Host "  During installation: Add CMake to system PATH" -ForegroundColor White
    Write-Host ""
    $openCmake = Read-Host "Open CMake download page in browser? (Y/n)"
    if ($openCmake -ne "n" -and $openCmake -ne "N") {
        Start-Process "https://cmake.org/download/"
    }
    Write-Host ""
    Write-Host "Please install CMake and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check for Visual Studio Build Tools
Write-Host "Checking for Visual Studio Build Tools..." -ForegroundColor Yellow
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$vsInstalled = $false

if (Test-Path $vsWhere) {
    $vsPath = & $vsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if ($vsPath) {
        $vsInstalled = $true
        Write-Host "  âœ“ Visual Studio Build Tools are installed" -ForegroundColor Green
    }
}

if (-not $vsInstalled) {
    Write-Host "  âœ— Visual Studio Build Tools are not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Visual Studio Build Tools are required to compile UxPlay." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download options:" -ForegroundColor Cyan
    Write-Host "  1. Visual Studio Build Tools (smaller, ~5 GB)" -ForegroundColor White
    Write-Host "     https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Visual Studio Community (full IDE, ~10 GB)" -ForegroundColor White
    Write-Host "     https://visualstudio.microsoft.com/vs/community/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "During installation, select: 'Desktop development with C++'" -ForegroundColor Yellow
    Write-Host ""

    $openVS = Read-Host "Open Visual Studio download page in browser? (Y/n)"
    if ($openVS -ne "n" -and $openVS -ne "N") {
        Start-Process "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    }
    Write-Host ""
    Write-Host "Please install Visual Studio Build Tools and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check for GStreamer
Write-Host "Checking for GStreamer..." -ForegroundColor Yellow
$gstreamPath = "C:\gstreamer\1.0\msvc_x86_64\bin"
$gstreamExists = Test-Path $gstreamPath

if ($gstreamExists) {
    Write-Host "  âœ“ GStreamer appears to be installed" -ForegroundColor Green
} else {
    Write-Host "  âš  GStreamer not found at default location" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "GStreamer is required for video processing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download GStreamer:" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://gstreamer.freedesktop.org/download/" -ForegroundColor White
    Write-Host "  2. Download: MSVC 64-bit runtime installer" -ForegroundColor White
    Write-Host "  3. Download: MSVC 64-bit development installer" -ForegroundColor White
    Write-Host "  4. Run both installers with default settings" -ForegroundColor White
    Write-Host ""

    $openGst = Read-Host "Open GStreamer download page in browser? (Y/n)"
    if ($openGst -ne "n" -and $openGst -ne "N") {
        Start-Process "https://gstreamer.freedesktop.org/download/"
    }
    Write-Host ""
    Write-Host "Please install GStreamer and run this script again." -ForegroundColor Yellow
    exit 1
}

# All dependencies met, proceed with installation
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All dependencies are installed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Downloading UxPlay" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create temporary directory
$tempDir = Join-Path $env:TEMP "uxplay_build_$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir | Out-Null
Write-Host "Using temporary directory: $tempDir" -ForegroundColor Gray

try {
    Set-Location $tempDir

    Write-Host "Cloning UxPlay repository..." -ForegroundColor Yellow
    git clone https://github.com/FDH2/UxPlay.git
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone UxPlay repository"
    }
    Set-Location UxPlay

    Write-Host "âœ“ Downloaded successfully" -ForegroundColor Green

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 2: Building UxPlay" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    New-Item -ItemType Directory -Path "build" -Force | Out-Null
    Set-Location build

    Write-Host "Configuring build with CMake..." -ForegroundColor Yellow
    Write-Host "This may take a few minutes..." -ForegroundColor Gray
    Write-Host ""

    # Find Visual Studio installation
    $vsPath = & $vsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath

    # Set up environment for Visual Studio
    $vcvarsall = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"

    # Run CMake
    cmake -G "Visual Studio 17 2022" -A x64 ..
    if ($LASTEXITCODE -ne 0) {
        # Try with different generator
        cmake -G "NMake Makefiles" ..
        if ($LASTEXITCODE -ne 0) {
            throw "CMake configuration failed"
        }
    }

    Write-Host ""
    Write-Host "Compiling UxPlay..." -ForegroundColor Yellow
    Write-Host "This may take several minutes..." -ForegroundColor Gray
    Write-Host ""

    cmake --build . --config Release
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed"
    }

    Write-Host ""
    Write-Host "âœ“ Build completed successfully" -ForegroundColor Green

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 3: Installing UxPlay" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Install to Program Files
    $installDir = "C:\Program Files\UxPlay"

    if (-not $isAdmin) {
        Write-Host "âš  Administrator privileges required for installation" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please choose an installation location:" -ForegroundColor Yellow
        Write-Host "  1. C:\Program Files\UxPlay (requires admin)" -ForegroundColor White
        Write-Host "  2. $env:LOCALAPPDATA\UxPlay (no admin required)" -ForegroundColor White
        Write-Host ""
        $choice = Read-Host "Enter choice (1 or 2)"

        if ($choice -eq "2") {
            $installDir = "$env:LOCALAPPDATA\UxPlay"
        }
    }

    Write-Host "Installing to: $installDir" -ForegroundColor Yellow

    # Create installation directory
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null

    # Copy executable
    $exePath = Get-ChildItem -Recurse -Filter "uxplay.exe" | Select-Object -First 1
    if ($exePath) {
        Copy-Item $exePath.FullName -Destination $installDir
        Write-Host "âœ“ Copied uxplay.exe to $installDir" -ForegroundColor Green
    } else {
        throw "Could not find uxplay.exe in build output"
    }

    # Add to PATH
    Write-Host ""
    Write-Host "Adding UxPlay to system PATH..." -ForegroundColor Yellow

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$installDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "User")
        Write-Host "âœ“ Added to PATH" -ForegroundColor Green
        Write-Host "  Note: You may need to restart your terminal" -ForegroundColor Gray
    } else {
        Write-Host "âœ“ Already in PATH" -ForegroundColor Green
    }

    # Update current session PATH
    $env:Path += ";$installDir"

    Write-Host ""
    Write-Host "âœ“ Installation completed successfully" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Installation Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Missing dependencies (see checks above)" -ForegroundColor White
    Write-Host "  - Network connection issues during git clone" -ForegroundColor White
    Write-Host "  - Build tool version incompatibilities" -ForegroundColor White
    Write-Host ""
    Write-Host "For help, visit: https://github.com/FDH2/UxPlay" -ForegroundColor Gray

    # Cleanup
    Set-Location $env:TEMP
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    exit 1
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Set-Location $env:TEMP
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "âœ“ Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Verify installation
$uxplayCommand = Get-Command uxplay -ErrorAction SilentlyContinue
if ($uxplayCommand) {
    Write-Host "UxPlay is ready to use!" -ForegroundColor Green
    Write-Host "Location: $($uxplayCommand.Source)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run your Desktop Casting Receiver application" -ForegroundColor White
    Write-Host "  2. On your iPhone/iPad: Control Center â†’ Screen Mirroring" -ForegroundColor White
    Write-Host "  3. Select 'Desktop Casting Receiver'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "âš  Warning: UxPlay command not found in PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You may need to:" -ForegroundColor Yellow
    Write-Host "  - Restart your terminal or PowerShell" -ForegroundColor White
    Write-Host "  - Manually add $installDir to your PATH" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
