# Comprehensive Connectivity Diagnostic for Desktop Casting Receiver
# Run this in PowerShell to diagnose all issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Desktop Casting Receiver Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# 1. Check if we're in WSL
Write-Host "1. Checking environment..." -ForegroundColor Yellow
if (Test-Path /proc/version) {
    $wslCheck = Get-Content /proc/version | Select-String -Pattern "microsoft"
    if ($wslCheck) {
        Write-Host "   [ERROR] Running in WSL! This won't work." -ForegroundColor Red
        $issues += "Must run in Windows PowerShell (not WSL)"
    }
} else {
    Write-Host "   [OK] Running in native Windows" -ForegroundColor Green
}
Write-Host ""

# 2. Check executable exists
Write-Host "2. Checking if executable exists..." -ForegroundColor Yellow
$exePath = Join-Path $PSScriptRoot "dist\DesktopCastingReceiver\DesktopCastingReceiver.exe"
if (Test-Path $exePath) {
    $exeDate = (Get-Item $exePath).LastWriteTime
    Write-Host "   [OK] Executable found" -ForegroundColor Green
    Write-Host "   Built: $exeDate" -ForegroundColor Gray

    # Check if it's recent (within last hour)
    $hourAgo = (Get-Date).AddHours(-1)
    if ($exeDate -lt $hourAgo) {
        Write-Host "   [WARNING] Executable is old - may not have zeroconf fixes!" -ForegroundColor Yellow
        $warnings += "Executable needs to be rebuilt"
    }
} else {
    Write-Host "   [ERROR] Executable not found!" -ForegroundColor Red
    $issues += "Must build executable first (run build_windows_easy.ps1)"
}
Write-Host ""

# 3. Check network configuration
Write-Host "3. Checking network configuration..." -ForegroundColor Yellow
try {
    $adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.InterfaceAlias -notlike "*Loopback*" -and
        $_.InterfaceAlias -notlike "*WSL*"
    }

    if ($adapters.Count -gt 0) {
        $mainIP = $adapters[0].IPAddress
        Write-Host "   [OK] Network configured" -ForegroundColor Green
        Write-Host "   Primary IP: $mainIP" -ForegroundColor White
        Write-Host "   Interface: $($adapters[0].InterfaceAlias)" -ForegroundColor Gray

        # List all adapters
        if ($adapters.Count -gt 1) {
            Write-Host "   Additional IPs:" -ForegroundColor Gray
            foreach ($adapter in $adapters[1..($adapters.Count-1)]) {
                Write-Host "     - $($adapter.IPAddress) ($($adapter.InterfaceAlias))" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   [ERROR] No network adapters found!" -ForegroundColor Red
        $issues += "No active network connection"
    }
} catch {
    Write-Host "   [ERROR] Cannot detect network: $_" -ForegroundColor Red
    $issues += "Network detection failed"
}
Write-Host ""

# 4. Check if ports are available
Write-Host "4. Checking if ports are available..." -ForegroundColor Yellow
$portsToCheck = @(
    @{Port=7000; Name="AirPlay"},
    @{Port=8080; Name="Web Interface"}
)

foreach ($portInfo in $portsToCheck) {
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $portInfo.Port)
        $listener.Start()
        $listener.Stop()
        Write-Host "   [OK] Port $($portInfo.Port) ($($portInfo.Name)) is available" -ForegroundColor Green
    } catch {
        Write-Host "   [WARNING] Port $($portInfo.Port) ($($portInfo.Name)) is in use" -ForegroundColor Yellow
        $warnings += "Port $($portInfo.Port) already in use - server may already be running"
    }
}
Write-Host ""

# 5. Check Windows Firewall rules
Write-Host "5. Checking Windows Firewall..." -ForegroundColor Yellow
$firewallRules = Get-NetFirewallRule -DisplayName "*DesktopCasting*","*Desktop Casting*" -ErrorAction SilentlyContinue

if ($firewallRules) {
    Write-Host "   [OK] Found $($firewallRules.Count) firewall rule(s)" -ForegroundColor Green
    foreach ($rule in $firewallRules) {
        $enabled = if ($rule.Enabled) { "Enabled" } else { "DISABLED" }
        $color = if ($rule.Enabled) { "Gray" } else { "Red" }
        Write-Host "   - $($rule.DisplayName): $enabled" -ForegroundColor $color
    }
} else {
    Write-Host "   [ERROR] No firewall rules found!" -ForegroundColor Red
    Write-Host "   This will block ALL connections" -ForegroundColor Red
    $issues += "Windows Firewall is blocking connections"
}
Write-Host ""

# 6. Check if Python dependencies exist in venv_build
Write-Host "6. Checking build environment..." -ForegroundColor Yellow
$venvPath = Join-Path $PSScriptRoot "venv_build\Scripts\python.exe"
if (Test-Path $venvPath) {
    Write-Host "   [OK] Build environment exists" -ForegroundColor Green

    # Check for zeroconf
    $zeroconfCheck = & $venvPath -m pip list 2>&1 | Select-String "zeroconf"
    if ($zeroconfCheck) {
        Write-Host "   [OK] zeroconf installed in build venv" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] zeroconf NOT installed in build venv!" -ForegroundColor Red
        $issues += "Build environment missing zeroconf"
    }
} else {
    Write-Host "   [WARNING] Build environment not found" -ForegroundColor Yellow
    $warnings += "Need to create build environment"
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[SUCCESS] No issues found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your system appears to be configured correctly." -ForegroundColor White
    Write-Host "If it's still not working, try:" -ForegroundColor Yellow
    Write-Host "  1. Run the executable" -ForegroundColor White
    Write-Host "  2. Check what error messages appear" -ForegroundColor White
    Write-Host "  3. Look for zeroconf errors specifically" -ForegroundColor White
} else {
    if ($issues.Count -gt 0) {
        Write-Host "[CRITICAL ISSUES] These MUST be fixed:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  ! $issue" -ForegroundColor Red
        }
        Write-Host ""
    }

    if ($warnings.Count -gt 0) {
        Write-Host "[WARNINGS] These should be addressed:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  * $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    # Provide recommended fixes
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "RECOMMENDED FIXES" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    if ($issues -contains "Must run in Windows PowerShell (not WSL)") {
        Write-Host "1. EXIT WSL and open Windows PowerShell:" -ForegroundColor Yellow
        Write-Host "   - Press Win + X" -ForegroundColor White
        Write-Host "   - Select 'Windows PowerShell'" -ForegroundColor White
        Write-Host "   - Run this script again" -ForegroundColor White
        Write-Host ""
    }

    if ($issues -contains "Must build executable first (run build_windows_easy.ps1)") {
        Write-Host "2. Build the executable:" -ForegroundColor Yellow
        Write-Host "   .\build_windows_easy.ps1" -ForegroundColor White
        Write-Host ""
    }

    if ($warnings -contains "Executable needs to be rebuilt") {
        Write-Host "3. REBUILD the executable (has old code without zeroconf fixes):" -ForegroundColor Yellow
        Write-Host "   .\build_windows_easy.ps1" -ForegroundColor White
        Write-Host ""
    }

    if ($issues -contains "Windows Firewall is blocking connections") {
        Write-Host "4. Fix Windows Firewall (run as Administrator):" -ForegroundColor Yellow
        Write-Host "   .\fix_firewall.ps1" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Offer to run fix_firewall if needed
if ($issues -contains "Windows Firewall is blocking connections") {
    $response = Read-Host "Would you like to fix the firewall now? (Requires Administrator) (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host ""
        Write-Host "Checking for Administrator privileges..." -ForegroundColor Yellow
        $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
        $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

        if ($isAdmin) {
            Write-Host "Running firewall fix..." -ForegroundColor Yellow
            & "$PSScriptRoot\fix_firewall.ps1"
        } else {
            Write-Host ""
            Write-Host "ERROR: Not running as Administrator!" -ForegroundColor Red
            Write-Host ""
            Write-Host "To fix firewall:" -ForegroundColor Yellow
            Write-Host "1. Right-click PowerShell" -ForegroundColor White
            Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
            Write-Host "3. Run: .\fix_firewall.ps1" -ForegroundColor White
        }
    }
}

Write-Host ""
