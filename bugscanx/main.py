import sys
from rich import print
from .utils import *

def main_menu():  
    try:
        menu_options = {
            '1': ("HOST SCANNER PRO", run_1, "bold cyan"),
            '2': ("HOST SCANNER", run_2, "bold blue"),
            '3': ("CIDR SCANNER", run_3, "bold yellow"),
            '4': ("SUBFINDER", run_4, "bold magenta"),
            '5': ("IP LOOKUP", run_5, "bold cyan"),
            '6': ("TXT TOOLKIT", run_6, "bold magenta"),
            '7': ("OPEN PORT", run_7, "bold white"),
            '8': ("DNS RECORDS", run_8, "bold green"),
            '9': ("HOST INFO", run_9, "bold blue"),
            '10': ("HELP", run_10, "bold yellow"),
            '11': ("UPDATE", run_11, "bold magenta"),
            '12': ("EXIT", lambda: sys.exit(), "bold red")
        }

        while True:
            clear_screen()
            banner()
            for key, (desc, _, color) in menu_options.items():
                print(f"[{color}] [{key}]{' ' if len(key)==1 else ''} {desc}")

            choice = get_input("Your Choice", "number", qmark="\n [-]")

            if choice in menu_options:
                clear_screen()
                if choice != '12':
                    text_ascii(menu_options[choice][0], color="bold magenta")
                try:
                    menu_options[choice][1]()
                except KeyboardInterrupt:
                    print("\n\n[yellow] Operation cancelled by user.")
                print("\n[yellow] Press Enter to continue...", end="")
                input()
    except KeyboardInterrupt:
        sys.exit()