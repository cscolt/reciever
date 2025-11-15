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

    REM Check if UxPlay is installed
    where uxplay >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ==================================
        echo Optional: iOS Screen Mirroring
        echo ==================================
        echo.
        echo For iOS screen mirroring support, UxPlay needs to be installed.
        echo.
        echo UxPlay enables:
        echo   - True iOS screen mirroring via AirPlay
        echo   - Native protocol support (no browser needed)
        echo   - Better quality than camera fallback
        echo.
        echo Without UxPlay:
        echo   - iOS devices can still use camera streaming via browser
        echo   - Connect at http://^<your-ip^>:8080
        echo.
        set /p INSTALL_UXPLAY="Would you like to install UxPlay now? (y/N): "
        if /i "%INSTALL_UXPLAY%"=="y" (
            echo.
            echo Running UxPlay installation script...
            powershell -ExecutionPolicy Bypass -File ".\install_uxplay.ps1"
        ) else (
            echo.
            echo You can install UxPlay later by running:
            echo   powershell -ExecutionPolicy Bypass -File .\install_uxplay.ps1
            echo.
        )
    ) else (
        echo.
        echo UxPlay is already installed - iOS screen mirroring enabled!
        echo.
    )
) else (
    echo.
    echo ==================================
    echo Build failed!
    echo ==================================
    exit /b 1
)

pause
