import sys
from rich import print
from . import clear_screen, banner, text_ascii

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
    for key, (desc, color) in MENU_OPTIONS.items():
        padding = ' ' if len(key) == 1 else ''
        print(f"[{color}] [{key}]{padding} {desc}")

def run_menu_option(choice):
    if choice == '12':
        return False
        
    clear_screen()
    text_ascii(MENU_OPTIONS[choice][0], color="bold magenta")
    
    try:
        module = __import__('bugscanx.entrypoints.runner', fromlist=[f'run_{choice}'])
        getattr(module, f'run_{choice}')()
    except KeyboardInterrupt:
        print("\n[yellow] Operation cancelled by user.")
    
    print("\n[yellow] Press Enter to continue...", end="")
    input()
    return True

def main():
    try:
        while True:
            display_menu()
            choice = input("\n\033[36m [-]  Your Choice: \033[0m")
            
            if choice not in MENU_OPTIONS:
                continue
                
            if not run_menu_option(choice):
                break
                
    except KeyboardInterrupt:
        sys.exit()
