# Build script for SketchBridge on Windows (PowerShell)
#
# Prerequisites:
#   - Python 3.10 or later
#   - pip install pyinstaller
#   - All SketchBridge dependencies installed
#
# Usage:
#   .\build_windows.ps1
#
# Output:
#   dist/SketchBridge/SketchBridge.exe

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Building SketchBridge for Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if PyInstaller is available
$pyinstallerInstalled = python -c "import PyInstaller" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}

# Install/update dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -e . 2>&1 | Out-Null

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist\SketchBridge") {
    Remove-Item -Recurse -Force "dist\SketchBridge"
}

# Run PyInstaller
Write-Host ""
Write-Host "Running PyInstaller..." -ForegroundColor Yellow
pyinstaller sketch_bridge.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output: dist\SketchBridge\SketchBridge.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "To distribute, copy the entire dist\SketchBridge folder."
Write-Host ""

# Show folder size
$folderSize = (Get-ChildItem -Recurse "dist\SketchBridge" | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Distribution size: $([math]::Round($folderSize, 1)) MB" -ForegroundColor Cyan
Write-Host ""

# Optionally run the built application
$run = Read-Host "Run SketchBridge now? (y/n)"
if ($run -eq "y") {
    Start-Process "dist\SketchBridge\SketchBridge.exe"
}
