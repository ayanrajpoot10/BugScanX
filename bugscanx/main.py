import sys
from rich import print
from bugscanx import banner, clear_screen, text_ascii

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

def print_menu():
    clear_screen()
    banner()
    for key, (desc, color) in menu_options.items():
        print(f"[{color}] [{key}]{' ' if len(key)==1 else ''} {desc}")
    return input("\n \033[36m[-]  Your Choice: \033[0m")

def execute_choice(choice):
    if choice == '12':
        sys.exit()
    
    clear_screen()
    text_ascii(menu_options[choice][0], color="bold magenta")
    try:
        module = __import__('bugscanx.utils', fromlist=[f'run_{choice}'])
        run_function = getattr(module, f'run_{choice}')
        run_function()
    except KeyboardInterrupt:
        print("\n\n[yellow] Operation cancelled by user.")
    print("\n[yellow] Press Enter to continue...", end="")
    input()

def main_menu():
    try:
        while True:
            choice = print_menu()
            if choice in menu_options:
                execute_choice(choice)
    except KeyboardInterrupt:
        sys.exit()