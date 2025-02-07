import os
import sys
import time
import itertools
import threading
import subprocess
from rich.prompt import Confirm
from rich.console import Console
from importlib.metadata import version, PackageNotFoundError
PACKAGE_NAME = 'bugscan-x'
console = Console()

def get_current_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        console.print(f"[bold red]Package '{package_name}' not found.[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error retrieving version: {e}[/bold red]")
        return None

def get_latest_version(package_name):
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', package_name],
            capture_output=True, text=True, check=True, timeout=10
        )
        lines = result.stdout.splitlines()
        return lines[-1].split()[-1] if lines else None
    except subprocess.TimeoutExpired:
        console.print("[bold red]Timeout while checking for updates.[/bold red]")
        return None
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error checking for updates: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")
        return None

def is_update_available(package_name):
    current_version = get_current_version(package_name)
    if not current_version:
        return False
    latest_version = get_latest_version(package_name)
    if not latest_version:
        return False
    return latest_version > current_version

class AnimationThread:
    def __init__(self, message):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._animate)

    def _animate(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.stop_event.is_set():
                break
            console.print(f"[bold yellow] {self.message} {c}", end="\r")
            time.sleep(0.1)
        console.print(" " * (len(self.message) + 4), end="\r")

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
        console.print("[bold green]Update successful![/bold green]")
    except subprocess.CalledProcessError:
        console.print(f"[bold red]Failed to update '{package_name}'.[/bold red]")
    except subprocess.TimeoutExpired:
        console.print(f"[bold red]Update timed out.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error during update: {e}[/bold red]")
    finally:
        animation.stop()

def restart_program():
    try:
        console.print("[bold green]Restarting program...[/bold green]")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        console.print(f"[bold red]Failed to restart program: {e}[/bold red]")
        sys.exit(1)

def check_and_update():
    animation = AnimationThread("Checking for updates")
    animation.start()
    update_available = is_update_available(PACKAGE_NAME)
    animation.stop()

    if update_available:
        console.print("[bold yellow]An update is available.[/bold yellow]")
        if Confirm.ask("Do you want to update now?"):
            update_package(PACKAGE_NAME)
            restart_program()
    else:
        console.print("[bold green]No updates available.[/bold green]")

