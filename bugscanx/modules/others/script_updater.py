import os
import sys
import time
import subprocess
from rich.console import Console
from importlib.metadata import version
from bugscanx.utils.common import get_confirm

PACKAGE_NAME = "bugscan-x"
console = Console()

def check_for_updates():
    try:
        with console.status("[yellow]Checking for updates...", spinner="dots"):
            current_version = version(PACKAGE_NAME)
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'index', 'versions', PACKAGE_NAME],
                    capture_output=True, text=True, check=True, timeout=15
                )
                lines = result.stdout.splitlines()
                latest_version = lines[-1].split()[-1] if lines else "0.0.0"
                
                if not latest_version or latest_version <= current_version:
                    console.print(f"[green] You're up to date: {current_version}")
                    return False, None, None
                    
                return True, current_version, latest_version
                
            except subprocess.TimeoutExpired:
                console.print("[red] Update check timed out. Please check your internet connection.")
                return False, None, None
            except subprocess.CalledProcessError:
                console.print("[red] Failed to check updates")
                return False, None, None
    except Exception:
        console.print("[red] Error checking updates")
        return False, None, None

def install_update():
    try:
        with console.status("[yellow]Installing update...", spinner="point"):
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--upgrade', PACKAGE_NAME],
                    capture_output=True, text=True, check=True, timeout=60
                )
                console.print("[green] Update successful!")
                return True
            except subprocess.TimeoutExpired:
                console.print("[red] Installation timed out. Please try again.")
                return False
            except subprocess.CalledProcessError:
                console.print("[red] Installation failed")
                return False
    except Exception:
        console.print("[red] Error during installation")
        return False

def restart_application():
    console.print("[yellow] Restarting application...")
    time.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)

def check_and_update():
    try:
        has_update, current_version, latest_version = check_for_updates()
        if not has_update:
            return

        console.print(f"[yellow] Update available: {current_version} → {latest_version}")
        if not get_confirm(" Update now"):
            return

        if install_update():
            restart_application()
            
    except KeyboardInterrupt:
        console.print("[yellow] Update cancelled by user.")
    except Exception:
        console.print("[red] Error during update process")
