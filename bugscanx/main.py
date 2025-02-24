import sys
from rich import print
from bugscanx.utils import *

def main_menu():  
    menu_options = {
        '1': ("HOST SCANNER PRO", run_host_scanner_pro, "bold cyan"),
        '2': ("HOST SCANNER", run_host_scanner, "bold blue"),
        '3': ("CIDR SCANNER", run_cidr_scanner, "bold yellow"),
        '4': ("SUBFINDER", run_sub_finder, "bold magenta"),
        '5': ("IP LOOKUP", run_ip_lookup, "bold cyan"),
        '6': ("TxT TOOLKIT", run_txt_toolkit, "bold magenta"),
        '7': ("OPEN PORT", run_open_port, "bold white"),
        '8': ("DNS RECORDS", run_dns_records, "bold green"),
        '9': ("OSINT", run_osint, "bold blue"),
        '10': ("HELP MENU", run_help_menu, "bold yellow"),
        '11': ("UPDATER", run_script_updater, "bold magenta"),
        '12': ("EXIT", lambda: sys.exit(), "bold red")
    }

    while True:
        clear_screen()
        banner()
        for key, (desc, _, color) in menu_options.items():
            print(f"[{color}] [{key}]{' ' if len(key)==1 else ''} {desc}")
       
        choice = get_input(" Your Choice", "number", min_value=1, max_value=12, qmark="\n [-]")

        if choice in menu_options:
            clear_screen()
            if choice != '12':
                text_ascii(menu_options[choice][0], font="calvin_s", color="bold magenta")
            menu_options[choice][1]()
            print("[yellow]\n Press Enter to continue...", end="")
            input()
