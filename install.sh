#!/bin/bash
set -e
echo "Installing MAP-MINER..."

# Clone if not in MAP-MINER directory
if [ ! -d "turbo/requirements.txt" ]; then
    rm -rf ~/mapminer 2>/dev/null || true
    git clone https://github.com/shayan-human/MAP-MINER.git ~/mapminer
    cd ~/mapminer
fi

# Python check
command -v python3 >/dev/null || { echo "ERROR: Python 3 not found. Install from https://python.org"; exit 1; }

# Create venv & install
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing dependencies..."
pip install -r turbo/requirements.txt >/dev/null 2>&1
pip install playwright >/dev/null 2>&1
python -m playwright install chromium >/dev/null 2>&1

echo ""
echo "✅ INSTALL COMPLETE!"
echo ""
echo "Run these commands:"
echo "  cd ~/mapminer"
echo "  ./mapminer"
echo ""
echo "Then open http://localhost:8000"
