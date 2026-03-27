#!/bin/bash
cd "$(dirname "$0")/turbo"
source ../venv/bin/activate
python3 -m uvicorn server:app --reload --port 8000
