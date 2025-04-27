import sys
from argparse import ArgumentParser
from importlib import import_module, metadata
from rich import print
from bugscanx import clear_screen, banner, text_ascii

MENU_OPTIONS = {
    '1':  ("HOST SCANNER PRO", "bold cyan"),
    '2':  ("HOST SCANNER", "bold blue"),
    '3':  ("CIDR SCANNER", "bold yellow"),
    '4':  ("SUBFINDER", "bold magenta"),
    '5':  ("IP LOOKUP", "bold cyan"),
    '6':  ("TXT TOOLKIT", "bold magenta"),
    '7':  ("OPEN PORT", "bold white"),
    '8':  ("DNS RECORDS", "bold green"),
    '9':  ("HOST INFO", "bold blue"),
    '10': ("HELP", "bold yellow"),
    '11': ("UPDATE", "bold magenta"),
    '12': ("EXIT", "bold red")
}

def display_menu():
    banner()
    print("\n".join(f"[{color}] [{k}]{' ' if len(k)==1 else ''} {desc}" 
          for k, (desc, color) in MENU_OPTIONS.items()))

def run_option(choice, from_menu=True):
    if choice == '12':
        return False
    if choice not in MENU_OPTIONS:
        return True
        
    clear_screen()
    text_ascii(MENU_OPTIONS[choice][0], color="bold magenta")
    
    try:
        getattr(import_module('bugscanx.entrypoints.runner'), f'run_{choice}')()
        if from_menu:
            print("\n[yellow] Press Enter to continue...", end="")
            input()
    except KeyboardInterrupt:
        print("\n[yellow] Operation cancelled by user.")
    return True

def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-u', '--update', action='store_true')
    parser.add_argument('option', nargs='?')
    args = parser.parse_args()

    if args.version:
        print(f"[bold cyan]BugScanX version {metadata.version('bugscan-x')}[/bold cyan]")
        return
    if args.update:
        return run_option('11', from_menu=False)
    if args.option:
        return 0 if run_option(args.option, from_menu=False) else 1

    try:
        while True:
            display_menu()
            if not run_option(input("\n\033[36m [-]  Your Choice: \033[0m"), from_menu=True):
                break
    except KeyboardInterrupt:
        sys.exit(0)
