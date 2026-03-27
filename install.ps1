# MAP-MINER Windows Installer
# Run: irm https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "Installing MAP-MINER..." -ForegroundColor Cyan

# Clone if not in MAP-MINER directory
if (-not (Test-Path "turbo\requirements.txt")) {
    $clonePath = "$HOME\mapminer"
    if (Test-Path $clonePath) { Remove-Item -Recurse -Force $clonePath }
    Write-Host "Cloning MAP-MINER repository..." -ForegroundColor Yellow
    git clone https://github.com/shayan-human/MAP-MINER.git $clonePath
    Set-Location $clonePath
}

# Check Python
try { python --version | Out-Null } catch { 
    Write-Host "ERROR: Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1 
}

# Create venv & install
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
$venvPip = "venv\Scripts\pip.exe"
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPip install -r turbo\requirements.txt *>$null 2>&1
& $venvPip install playwright *>$null 2>&1
venv\Scripts\python.exe -m playwright install chromium *>$null 2>&1

# Create mapminer.bat
@"
@echo off
cd /d %USERPROFILE%\mapminer
call venv\Scripts\activate.bat
cd turbo
python -m uvicorn turbo.server:app --reload --port 8000
"@ | Set-Content mapminer.bat -Encoding ASCII

Write-Host ""
Write-Host "✅ INSTALL COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Run these commands:" -ForegroundColor White
Write-Host "  cd %USERPROFILE%\mapminer" -ForegroundColor Cyan
Write-Host "  mapminer.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then open http://localhost:8000" -ForegroundColor White
