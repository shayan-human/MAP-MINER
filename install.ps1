# MAP-MINER Windows Installer
# Run: irm https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "Installing MAP-MINER..." -ForegroundColor Cyan

$REPO_URL = "https://github.com/shayan-human/MAP-MINER.git"
$INSTALL_DIR = "$HOME\mapminer"

# Check if not in MAP-MINER directory
if (-not (Test-Path "turbo\requirements.txt")) {
    Write-Host "Cloning MAP-MINER repository..." -ForegroundColor Yellow
    if (Test-Path $INSTALL_DIR) {
        Remove-Item -Recurse -Force $INSTALL_DIR
    }
    git clone $REPO_URL $INSTALL_DIR
    Set-Location $INSTALL_DIR
    Write-Host "Cloned to $INSTALL_DIR" -ForegroundColor Green
}

$ScriptDir = Get-Location

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create venv
$venvDir = Join-Path $ScriptDir "venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvDir
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& $venvPip install -r (Join-Path $ScriptDir "turbo\requirements.txt") -q

# Install Playwright
Write-Host "Installing Playwright browser..." -ForegroundColor Yellow
& $venvPip install playwright -q
& $venvPython -m playwright install chromium -q

# Create mapminer.bat
$batContent = "@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
cd turbo
python -m uvicorn turbo.server:app --reload --port 8000
"
$batPath = Join-Path $ScriptDir "mapminer.bat"
Set-Content -Path $batPath -Value $batContent -Encoding ASCII

# Add to PATH (optional)
$envPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($envPath -notlike "*$ScriptDir*") {
    Write-Host ""
    Write-Host "To run from anywhere, add this to PATH: $ScriptDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Run: mapminer.bat" -ForegroundColor Cyan
Write-Host "Then open http://localhost:8000" -ForegroundColor White
