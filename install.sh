#!/bin/bash
# MAP-MINER Installer for Linux/macOS
# Run: curl -sL https://raw.githubusercontent.com/shayan-human/MAP-MINER/main/install.sh | bash

set -e

echo "Installing MAP-MINER..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install from https://python.org"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install -r turbo/requirements.txt -q
pip install playwright -q
python -m playwright install chromium -q

# Create global command
if [ ! -L /usr/local/bin/mapminer ]; then
    sudo ln -sf "$SCRIPT_DIR/mapminer" /usr/local/bin/mapminer 2>/dev/null || true
fi

echo ""
echo "✅ INSTALL COMPLETE!"
echo ""
echo "Run: mapminer"
echo "Then open http://localhost:8000"
