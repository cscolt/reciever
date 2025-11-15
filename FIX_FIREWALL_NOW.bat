@echo off
REM Simple Firewall Fix - RIGHT-CLICK and "Run as Administrator"

echo ========================================
echo Desktop Casting Receiver Firewall Fix
echo ========================================
echo.

REM Check for admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
    echo.
) else (
    echo ERROR: Not running as Administrator!
    echo.
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

set EXE_PATH=%~dp0dist\DesktopCastingReceiver\DesktopCastingReceiver.exe

if not exist "%EXE_PATH%" (
    echo ERROR: Executable not found at:
    echo %EXE_PATH%
    echo.
    echo Build it first using build_windows_easy.ps1
    pause
    exit /b 1
)

echo Adding firewall rules for:
echo %EXE_PATH%
echo.

echo Adding rule for AirPlay (TCP 7000)...
netsh advfirewall firewall add rule name="Desktop Casting - AirPlay" dir=in action=allow program="%EXE_PATH%" protocol=TCP localport=7000 enable=yes

echo Adding rule for mDNS (UDP 5353)...
netsh advfirewall firewall add rule name="Desktop Casting - mDNS" dir=in action=allow program="%EXE_PATH%" protocol=UDP localport=5353 enable=yes

echo Adding rule for Web (TCP 8080)...
netsh advfirewall firewall add rule name="Desktop Casting - Web" dir=in action=allow program="%EXE_PATH%" protocol=TCP localport=8080 enable=yes

echo.
echo ========================================
echo SUCCESS! Firewall rules added.
echo ========================================
echo.
echo Now you can run the application:
echo   cd dist\DesktopCastingReceiver
echo   DesktopCastingReceiver.exe
echo.
pause
