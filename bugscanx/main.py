import os
import sys
import time
import itertools
import threading
import subprocess
import contextlib
import importlib.util

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@contextlib.contextmanager
def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        yield
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def animate_installation(package):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if package['done']:
            break
        sys.stdout.write(f'\r\033[33m Installing {package["name"]} {c}\033[0m')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')

def install_requirements():
    required_packages = {
        'requests': 'requests',
        'rich': 'rich',
        'colorama': 'colorama',
        'pyfiglet': 'pyfiglet',
        'loguru': 'loguru',
        'tqdm': 'tqdm',
        'beautifulsoup4': 'bs4',
        'dnspython': 'dns',
        'multithreading': 'multithreading',
        'prompt_toolkit': 'prompt_toolkit',
        'InquirerPy': 'InquirerPy'
    }
    
    missing_packages = [pkg for pkg, mod in required_packages.items() if importlib.util.find_spec(mod) is None]
    if not missing_packages:
        return

    threads = []
    for package in missing_packages:
        package_info = {'name': package, 'done': False}
        t = threading.Thread(target=animate_installation, args=(package_info,))
        threads.append((t, package_info))
        t.start()
        
        with hide_cursor():
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        package_info['done'] = True
    
    for t, _ in threads:
        t.join()
    
    print("\033[32m All missing packages installed successfully.\033[0m")

install_requirements()

from bugscanx.utils import *
from rich.console import Console
from rich.traceback import install

console = Console()
install(console=console, width=80, extra_lines=1, show_locals=False, max_frames=1)

def main_menu():
    menu_options = {
        '1': ("HOST SCANNER PRO", run_host_checker, "bold cyan"),
        '2': ("HOST SCANNER", run_sub_scan, "bold blue"),
        '3': ("CIDR SCANNER", run_ip_scan, "bold yellow"),
        '4': ("SUBFINDER", run_sub_finder, "bold magenta"),
        '5': ("IP LOOKUP", run_ip_lookup, "bold cyan"),
        '6': ("TxT TOOLKIT", run_txt_toolkit, "bold magenta"),
        '7': ("OPEN PORT", run_open_port, "bold white"),
        '8': ("DNS RECORDS", run_dns_info, "bold green"),
        '9': ("OSINT", run_osint, "bold blue"),
        '10': ("HELP MENU", run_help_menu, "bold yellow"),
        '11': ("UPDATER", run_script_updater, "bold magenta"),
        '12': ("EXIT", lambda: sys.exit(), "bold red")
    }

    while True:
        clear_screen()
        banner()
        display_message()
        for key, (desc, _, color) in menu_options.items():
            if int(key) < 10:
                console.print(f"[{color}] [{key}]  {desc}")
            else:
                console.print(f"[{color}] [{key}] {desc}")

        choice = get_input(prompt="\n [-]  Enter your choice", validator=digit_range_validator)

        if choice in menu_options:
            clear_screen()
            text_ascii(menu_options[choice][0], font="calvin_s", color="bold magenta")
            menu_options[choice][1]()
            if choice != '12':
                console.input("[yellow]\n Press [bold]Enter[/bold] to continue...")

if __name__ == "__main__":
    main_menu()