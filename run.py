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

LAST_INSTALL_FILE = SCRIPT_DIR / ".last_install"


def create_venv():
    print("Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True)


def get_venv_python():
    """Get path to venv Python executable with cross-platform support."""
    if sys.platform == "win32":
        # Use py launcher on Windows (handles multiple Python versions better)
        return "py"
    else:
        python_path = VENV_DIR / "bin" / "python"

    # Verify the venv Python exists
    if python_path.exists():
        return str(python_path)

    # Fallback to system Python if venv Python not found
    print(f"Warning: venv Python not found at {python_path}, using system Python")
    return sys.executable


def install_deps(force=False):
    """Install dependencies from requirements.txt if they have changed."""
    req_file = TURBO_DIR / "requirements.txt"
    marker_file = VENV_DIR / ".last_install"

    if not force and marker_file.exists():
        # Only skip if requirements haven't changed since last install
        if req_file.stat().st_mtime <= marker_file.stat().st_mtime:
            return

    print("Installing/Updating dependencies...")
    python = get_venv_python()
    try:
        subprocess.run(
            [str(python), "-m", "pip", "install", "-r", str(req_file)], check=True
        )
        subprocess.run([str(python), "-m", "pip", "install", "playwright"], check=True)
        subprocess.run(
            [str(python), "-m", "playwright", "install", "chromium"], check=True
        )

        # Mark successful installation
        marker_file.touch()
        print("Done! All dependencies are ready.")
    except Exception as e:
        print(f"Error during installation: {e}")
        sys.exit(1)


def install_system_deps():
    if sys.platform == "win32":
        print("System dependencies are handled automatically on Windows.")
        return

    print("Installing system dependencies for Playwright (requires sudo)...")
    python = get_venv_python()
    try:
        subprocess.run(
            [str(python), "-m", "playwright", "install-deps", "chromium"], check=True
        )
    except Exception as e:
        print(
            f"Warning: Could not install system dependencies: {e}. You may need to run 'sudo playwright install-deps' manually."
        )


def run_server():
    print("\nStarting server at http://localhost:8000\n")

    # Use py launcher on Windows, sys.executable on other platforms
    if sys.platform == "win32":
        python = "py"
    else:
        python = sys.executable

    # Ensure current directory is in PYTHONPATH for 'turbo' module discovery
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPT_DIR) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        # Use subprocess instead of execv to maintain control and handle environment correctly
        subprocess.run(
            [
                python,
                "-m",
                "uvicorn",
                "turbo.server:app",
                "--reload",
                "--reload-dir",
                str(TURBO_DIR),
                "--port",
                "8000",
                "--host",
                "0.0.0.0",
            ],
            cwd=str(SCRIPT_DIR),
            env=env,
        )
    except KeyboardInterrupt:
        print("\nStopping Map Miner...")
    except Exception as e:
        print(f"Error starting server: {e}")


def check_for_updates():
    """Attempt to pull the latest changes from Git before running."""
    if "--no-update" in sys.argv:
        return False

    print("Checking for updates...", end="", flush=True)
    git_dir = SCRIPT_DIR / ".git"
    if not git_dir.exists():
        print(" (not a git repo)")
        return False

    try:
        # Get hash before pull
        old_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=SCRIPT_DIR
        ).stdout.strip()

        # Try to pull
        subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=15,
        )

        # Get hash after pull
        new_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=SCRIPT_DIR
        ).stdout.strip()

        if old_hash != new_hash:
            print("\nUpdates pulled successfully!")
            return True
        else:
            print(" (up to date)")
            return False

    except Exception as e:
        print(f"\nWarning: Could not check for updates ({e}). Proceeding...")
    return False


def main():
    args = sys.argv[1:]
    do_setup = "--setup" in args

    if check_for_updates():
        print("Restarting script to apply updates...")
        # Remove --setup from args if present to avoid redundant setup on restart
        new_args = [a for a in sys.argv if a != "--setup"]
        os.execv(sys.executable, [sys.executable] + new_args)

    if not VENV_DIR.exists():
        create_venv()
        do_setup = True  # Force install if venv is new

    if do_setup:
        install_deps(force=True)
        install_system_deps()

    run_server()


if __name__ == "__main__":
    main()
