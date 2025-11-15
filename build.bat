@echo off
REM Build script for Desktop Casting Receiver (Windows)

echo ==================================
echo Desktop Casting Receiver Builder
echo ==================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
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
    echo iOS Screen Mirroring Support
    echo ==================================
    echo.
    echo [OK] Built-in Python AirPlay receiver included!
    echo.
    echo Features:
    echo   - Native AirPlay protocol support
    echo   - Real cryptography (SRP-6a, Ed25519, ChaCha20)
    echo   - H.264 video decoding
    echo   - No external dependencies required
    echo.
    echo iOS devices will automatically discover this receiver
    echo in Control Center ^> Screen Mirroring
    echo.
) else (
    echo.
    echo ==================================
    echo Build failed!
    echo ==================================
    exit /b 1
)

pause
