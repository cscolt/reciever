@echo off
REM Build script for Desktop Casting Receiver (Windows)

echo ==================================
echo Desktop Casting Receiver Builder
echo ==================================
echo.

REM Find Windows Python installation
echo Locating Windows Python...

REM Prefer Python 3.12 over 3.14 due to better package compatibility
set PYTHON_EXE=
if exist "C:\Users\control\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=C:\Users\control\AppData\Local\Programs\Python\Python312\python.exe
    goto :found_python
)
if exist "C:\Users\control\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=C:\Users\control\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)
if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
    goto :found_python
)
if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
    goto :found_python
)

REM Try py launcher as fallback
py -3.12 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=py -3.12
    goto :found_python
)

py -3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=py -3.11
    goto :found_python
)

REM Last resort: use python in PATH
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=python
    goto :found_python
)

echo ERROR: Could not find Windows Python installation!
echo.
echo Please install Python 3.11 or 3.12 from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check 'Add Python to PATH' during installation.
pause
exit /b 1

:found_python
for /f "tokens=*" %%i in ('%PYTHON_EXE% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo Path: %PYTHON_EXE%
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Build with PyInstaller
echo.
echo Building executable...
pyinstaller desktop_caster.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================
    echo Build successful!
    echo ==================================
    echo.
    echo Executable location:
    echo   .\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe
    echo.
    echo To run:
    echo   cd dist\DesktopCastingReceiver
    echo   DesktopCastingReceiver.exe
    echo.
    echo ==================================
    echo NEW: Chrome/Chromebook Discovery
    echo ==================================
    echo.
    echo [OK] mDNS service advertisement included!
    echo.
    echo Chrome and Chromebook devices can now:
    echo   - Automatically discover this receiver
    echo   - Find it in Chrome Cast menu
    echo   - Or manually visit: http://^<your-ip^>:8080
    echo.
    echo ==================================
    echo iOS Screen Mirroring Support
    echo ==================================
    echo.
    echo Two methods available:
    echo.
    echo 1. UxPlay (RECOMMENDED - Real video capture)
    echo    Note: UxPlay installation on Windows is complex
    echo    See: https://github.com/FDH2/UxPlay
    echo    Requires: GStreamer, Bonjour, and compilation
    echo.
    echo 2. Python AirPlay (Built-in fallback)
    echo    [OK] Included with full crypto support
    echo    - SRP-6a authentication
    echo    - Ed25519 key exchange
    echo    - ChaCha20-Poly1305 encryption
    echo    - H.264 video decoding
    echo.
    echo iOS devices will discover 'Desktop Casting Receiver'
    echo in Control Center ^> Screen Mirroring
    echo.
    echo Note: For BEST iOS experience, use Linux with UxPlay + GStreamer
    echo.
) else (
    echo.
    echo ==================================
    echo Build failed!
    echo ==================================
    exit /b 1
)

pause
