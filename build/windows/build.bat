@echo off
REM Windows Build Script for Desktop Casting Receiver v2.0
REM Updated for new refactored structure

cd /d "%~dp0\..\.."

echo ====================================
echo  Desktop Casting Receiver v2.0
echo  Windows Build Script
echo ====================================
echo.

REM Find Python installation
echo Locating Python...

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

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=python
    goto :found_python
)

echo ERROR: Could not find Python!
echo Please install Python 3.11+ from: https://www.python.org/downloads/
pause
exit /b 1

:found_python
for /f "tokens=*" %%i in ('%PYTHON_EXE% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Check for virtual environment
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
echo Building executable with PyInstaller...
pyinstaller build\desktop_caster.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo  Build Successful!
    echo ====================================
    echo.
    echo Executable location:
    echo   .\dist\DesktopCastingReceiver\DesktopCastingReceiver.exe
    echo.
    echo To run:
    echo   cd dist\DesktopCastingReceiver
    echo   DesktopCastingReceiver.exe
    echo.
    echo ====================================
    echo Feature Summary
    echo ====================================
    echo.
    echo [OK] WebRTC screen casting
    echo [OK] mDNS discovery
    echo [OK] iOS camera streaming
    echo.
    echo Note: Full iOS screen mirroring requires UxPlay
    echo       (Complex setup on Windows - use Linux for best results)
    echo.
) else (
    echo.
    echo ====================================
    echo  Build Failed!
    echo ====================================
    exit /b 1
)

pause
