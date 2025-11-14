# Diagnostic script to identify build issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Python Version:" -ForegroundColor Yellow
python --version
Write-Host ""

# Check pip version
Write-Host "Pip Version:" -ForegroundColor Yellow
python -m pip --version
Write-Host ""

# Try installing each package individually to find the problematic one
Write-Host "Testing individual package installations..." -ForegroundColor Yellow
Write-Host ""

$packages = @(
    "aiohttp==3.9.1",
    "Pillow==10.1.0",
    "numpy==1.24.3",
    "opencv-python==4.8.1.78",
    "websockets==12.0",
    "av==11.0.0",
    "aiortc==1.6.0",
    "pyinstaller==6.3.0"
)

$failed = @()

foreach ($package in $packages) {
    Write-Host "Testing: $package" -ForegroundColor Gray
    $result = python -m pip install --dry-run --no-deps $package 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  FAILED" -ForegroundColor Red
        $failed += $package
    } else {
        Write-Host "  OK" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($failed.Count -eq 0) {
    Write-Host "All packages can be installed!" -ForegroundColor Green
} else {
    Write-Host "Failed packages:" -ForegroundColor Red
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Solution: Try installing with relaxed version constraints" -ForegroundColor Yellow
}
