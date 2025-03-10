import sys
from rich import print
from . import clear_screen, banner, text_ascii

menu_options = {
    '1': ("HOST SCANNER PRO", "bold cyan"),
    '2': ("HOST SCANNER", "bold blue"),
    '3': ("CIDR SCANNER", "bold yellow"),
    '4': ("SUBFINDER", "bold magenta"),
    '5': ("IP LOOKUP", "bold cyan"),
    '6': ("TXT TOOLKIT", "bold magenta"),
    '7': ("OPEN PORT", "bold white"),
    '8': ("DNS RECORDS", "bold green"),
    '9': ("HOST INFO", "bold blue"),
    '10': ("HELP", "bold yellow"),
    '11': ("UPDATE", "bold magenta"),
    '12': ("EXIT", "bold red")
}

def main_menu():
    while True:
        clear_screen()
        banner()
        print('\n'.join(f"[{color}] [{key}]{' ' if len(key)==1 else ''} {desc}" 
                       for key, (desc, color) in menu_options.items()))

        choice = input("\n \033[36m[-]  Your Choice: \033[0m")
        if choice not in menu_options:
            continue
            
        if choice == '12':
            sys.exit()
            
        clear_screen()
        text_ascii(menu_options[choice][0], color="bold magenta")
        try:
            module = __import__('bugscanx.utils.handler', fromlist=[f'run_{choice}'])
            getattr(module, f'run_{choice}')()
        except KeyboardInterrupt:
            print("\n\n[yellow] Operation cancelled by user.")
        print("\n[yellow] Press Enter to continue...", end="")
        input()