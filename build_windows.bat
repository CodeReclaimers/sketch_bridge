@echo off
REM Build script for SketchBridge on Windows
REM
REM Prerequisites:
REM   - Python 3.10 or later
REM   - pip install pyinstaller
REM   - All SketchBridge dependencies installed
REM
REM Usage:
REM   build_windows.bat
REM
REM Output:
REM   dist/SketchBridge/SketchBridge.exe

echo ============================================
echo Building SketchBridge for Windows
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        exit /b 1
    )
)

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -e . >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not install package in editable mode
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist\SketchBridge" rmdir /s /q "dist\SketchBridge"

REM Run PyInstaller
echo.
echo Running PyInstaller...
pyinstaller sketch_bridge.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ============================================
echo Build complete!
echo ============================================
echo.
echo Output: dist\SketchBridge\SketchBridge.exe
echo.
echo To distribute, copy the entire dist\SketchBridge folder.
echo.

REM Optionally run the built application
set /p RUN="Run SketchBridge now? (y/n): "
if /i "%RUN%"=="y" (
    start "" "dist\SketchBridge\SketchBridge.exe"
)
