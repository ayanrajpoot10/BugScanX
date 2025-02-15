import os
import sys

from rich.console import Console
from rich.traceback import install

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bugscanx.utils import *

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

        choice = get_input("\n [-]  Enter your choice", validator=digit_range_validator)

        if choice in menu_options:
            clear_screen()
            text_ascii(menu_options[choice][0], font="calvin_s", color="bold magenta")
            menu_options[choice][1]()
            if choice != '12':
                console.input("[yellow]\n Press [bold]Enter[/bold] to continue...")

if __name__ == "__main__":
    main_menu()