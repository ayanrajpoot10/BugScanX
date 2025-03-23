import os
import sys
import time
import subprocess
from rich.console import Console
from importlib.metadata import version
from bugscanx.utils.common import get_confirm

PACKAGE_NAME = "bugscan-x"
console = Console()

def check_and_update():
    try:
        with console.status("[yellow]Checking for updates...", spinner="dots") as status:
            current_version = version(PACKAGE_NAME)
            
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'index', 'versions', PACKAGE_NAME],
                    capture_output=True, text=True, check=True, timeout=15
                )
                lines = result.stdout.splitlines()
                latest_version = lines[-1].split()[-1] if lines else "0.0.0"
            except subprocess.TimeoutExpired:
                console.print("[red] Update check timed out. Please check your internet connection.")
                return
            except subprocess.CalledProcessError as e:
                console.print(f"[red] Failed to check updates: {e.stderr}")
                return
        
        if not latest_version or latest_version <= current_version:
            console.print(f"[green] You're up to date: {current_version}")
            return
            
        console.print(f"[yellow] Update available: {current_version} → {latest_version}")
        if not get_confirm(" Update now"):
            return
            
        with console.status("[yellow] Installing update...", spinner="point") as status:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--upgrade', PACKAGE_NAME],
                    capture_output=True, text=True, check=True, timeout=60
                )
                console.print("[green] Update successful!")
            except subprocess.TimeoutExpired:
                console.print("[red] Installation timed out. Please try again.")
                return
            except subprocess.CalledProcessError as e:
                console.print(f"[red] Installation failed: {e.stderr}")
                return
        
        console.print("[yellow] Restarting application...")
        time.sleep(1)
        
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except KeyboardInterrupt:
        console.print("\n[yellow] Update cancelled by user.")
    except Exception as e:
        console.print(f"[red] Error during update process: {str(e)}")
