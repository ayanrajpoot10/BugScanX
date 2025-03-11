import os
import sys
import time
import subprocess
from rich.console import Console
from importlib.metadata import version
from bugscanx.utils import get_confirm

PACKAGE_NAME = "bugscan-x"
console = Console()

def check_and_update():
    try:
        with console.status("[yellow] Checking for updates", spinner="dots") as status:
            current_version = version(PACKAGE_NAME)
            
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'index', 'versions', PACKAGE_NAME],
                capture_output=True, text=True, check=True, timeout=10
            )
            lines = result.stdout.splitlines()
            latest_version = lines[-1].split()[-1] if lines else None
        
        if not latest_version or latest_version <= current_version:
            console.print(f"[green] You're up to date: {current_version}")
            return
            
        console.print(f"[yellow] Update available: {current_version} → {latest_version}")
        if not get_confirm(" Update now"):
            return
            
        with console.status("[yellow] Updating", spinner="point") as status:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', PACKAGE_NAME],
                check=True, timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        
        console.print("[green] Updated. Restarting...")
        time.sleep(1)
        
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except Exception as e:
        console.print(f"[red] Update error: {e}")
