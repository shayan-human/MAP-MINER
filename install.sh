#!/bin/bash
echo "Installing Map Miner Dependencies..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.10 or higher."
    exit
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements quietly
echo "Installing Python requirements..."
pip install --quiet -r turbo/requirements.txt

# Install Playwright browser
echo "Installing Playwright chromium..."
playwright install chromium

# Add to PATH for system-wide access
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -L /usr/local/bin/mapminer ]; then
    echo "Creating 'mapminer' command globally..."
    if ln -sf "$SCRIPT_DIR/mapminer" /usr/local/bin/mapminer 2>/dev/null; then
        echo "✅ Done! Run 'mapminer' from anywhere."
    else
        echo "⚠️ Need sudo permission. Running without global install."
        echo "   Use: sudo ln -sf $SCRIPT_DIR/mapminer /usr/local/bin/mapminer"
    fi
fi

echo ""
echo "🚀 Run 'mapminer' to start the server!"
