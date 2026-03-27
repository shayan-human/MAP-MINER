#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r turbo/requirements.txt -q

cd turbo
python3 -m uvicorn server:app --reload --port 8000
