# MAP-MINER Windows Installer
# Run: irm https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "Installing MAP-MINER..." -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Get script directory
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

# Create venv
$venvDir = Join-Path $ScriptDir "venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvDir
}

# Activate venv
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& $venvPip install -r (Join-Path $ScriptDir "turbo\requirements.txt") -q

# Install Playwright
Write-Host "Installing Playwright browser..." -ForegroundColor Yellow
& $venvPip install playwright -q
& $venvPython -m playwright install chromium -q

# Create mapminer.bat for Windows
$batContent = "@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
cd turbo
python -m uvicorn turbo.server:app --reload --port 8000
"
$batPath = Join-Path $ScriptDir "mapminer.bat"
Set-Content -Path $batPath -Value $batContent -Encoding ASCII

Write-Host ""
Write-Host "✅ INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor White
Write-Host "  mapminer.bat" -ForegroundColor Cyan
Write-Host "  OR" -ForegroundColor White
Write-Host "  .\mapminer.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then open http://localhost:8000 in your browser" -ForegroundColor White
