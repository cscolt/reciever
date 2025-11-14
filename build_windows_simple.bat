@echo off
REM Simple Windows Build Script for Desktop Casting Receiver

echo ==========================================
echo Desktop Casting Receiver - Windows Builder
echo ==========================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or 3.12 from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv_build rmdir /s /q venv_build
python -m venv venv_build
call venv_build\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
echo This may take several minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    echo Common solutions:
    echo 1. Install Visual Studio Build Tools
    echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo 2. Use Python 3.11 or 3.12 instead of 3.14+
    echo.
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build
echo.
echo Building executable...
pyinstaller desktop_caster.spec --clean

if errorlevel 1 (
    echo.
    echo ==========================================
    echo BUILD FAILED!
    echo ==========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo BUILD SUCCESSFUL!
echo ==========================================
echo.
echo Executable location:
echo   dist\DesktopCastingReceiver\DesktopCastingReceiver.exe
echo.
echo To run:
echo   cd dist\DesktopCastingReceiver
echo   DesktopCastingReceiver.exe
echo.
pause
