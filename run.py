#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TURBO_DIR = SCRIPT_DIR / "turbo"
VENV_DIR = SCRIPT_DIR / "venv"
REQUIREMENTS = TURBO_DIR / "requirements.txt"

def create_venv():
    print("Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True)
    
def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def get_venv_activate():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "activate.bat"
    return VENV_DIR / "bin" / "activate"

def install_deps():
    print("Installing dependencies...")
    python = get_venv_python()
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "playwright"], check=True)
    subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
    # Add system dependencies for playwright on Linux
    if sys.platform != "win32":
        print("Installing system dependencies for Playwright...")
        try:
            subprocess.run([str(python), "-m", "playwright", "install-deps", "chromium"], check=True)
        except Exception as e:
            print(f"Warning: Could not install system dependencies: {e}. You may need to run 'sudo playwright install-deps' manually.")

def run_server():
    print("\nStarting server at http://localhost:8000\n")
    python = get_venv_python()
    os.execv(str(python), [str(python), "-m", "uvicorn", "turbo.server:app", "--reload", "--port", "8000"])

def main():
    if not VENV_DIR.exists():
        create_venv()
    
    install_deps()
    run_server()

if __name__ == "__main__":
    main()
