import os
import sys
import time
import threading
import itertools
import subprocess
from rich import print
from importlib.metadata import version
from bugscanx.utils import get_confirm

PACKAGE_NAME = "bugscan-x"

def get_current_version(package_name):
    try:
        return version(package_name)
    except Exception as e:
        print(f"[bold red]Error retrieving version: {e}[/bold red]")
        return None

def get_latest_version(package_name):
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', package_name],
            capture_output=True, text=True, check=True, timeout=10
        )
        lines = result.stdout.splitlines()
        return lines[-1].split()[-1] if lines else None
    except Exception as e:
        print(f"[bold red]Error while checking update: {e}[/bold red]")
        return None

def is_update_available(package_name):
    current_version = get_current_version(package_name)
    if not current_version:
        return False, None, None
    latest_version = get_latest_version(package_name)
    if not latest_version:
        return False, current_version, None
    return latest_version > current_version, current_version, latest_version

class AnimationThread:
    def __init__(self, message):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._animate)

    def _animate(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.stop_event.is_set():
                break
            print(f"[bold yellow] {self.message} {c}", end="\r")
            time.sleep(0.1)
        print(" " * (len(self.message) + 4), end="\r")

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

def update_package(package_name):
    animation = AnimationThread("Updating")
    animation.start()
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60
        )
        print("[bold green]Update successful![/bold green]")
    except subprocess.CalledProcessError:
        print(f"[bold red]Failed to update '{package_name}'.[/bold red]")
    except subprocess.TimeoutExpired:
        print(f"[bold red]Update timed out.[/bold red]")
    except Exception as e:
        print(f"[bold red]Unexpected error during update: {e}[/bold red]")
    finally:
        animation.stop()

def restart_program():
    try:
        print("[bold green]Restarting program...[/bold green]")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"[bold red]Failed to restart program: {e}[/bold red]")
        sys.exit(1)

def check_and_update():
    animation = AnimationThread("Checking for updates")
    animation.start()
    update_available, current_version, latest_version = is_update_available(PACKAGE_NAME)
    animation.stop()

    if update_available:
        print(f"[bold yellow]An update is available! Current version: {current_version}, Latest version: {latest_version}[/bold yellow]")
        if get_confirm("Would you like to update"):
            update_package(PACKAGE_NAME)
            restart_program()
    else:
        print(f"[bold green]No updates available. You are on the latest version: {current_version}[/bold green]")
