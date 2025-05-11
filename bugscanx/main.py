import sys
from rich import print
from bugscanx import banner, text_ascii

MENU_OPTIONS = {
    '1': ("HOST SCANNER PRO", "bold cyan"),
    '2': ("HOST SCANNER", "bold blue"),
    '3': ("CIDR SCANNER", "bold yellow"),
    '4': ("SUBFINDER", "bold magenta"),
    '5': ("IP LOOKUP", "bold cyan"),
    '6': ("FILE TOOLKIT", "bold magenta"),
    '7': ("OPEN PORTS", "bold white"),
    '8': ("DNS RECORD", "bold green"),
    '9': ("HOST INFO", "bold blue"),
    '10': ("HELP", "bold yellow"),
    '11': ("UPDATE", "bold magenta"),
    '12': ("EXIT", "bold red")
}

def main():
    try:
        while True:
            banner()
            print('\n'.join(f"[{color}] [{k}]{' ' if len(k)==1 else ''} {desc}" 
                        for k, (desc, color) in MENU_OPTIONS.items()))

            choice = input("\n \033[36m[-]  Your Choice: \033[0m")
            if choice not in MENU_OPTIONS:
                continue
                
            if choice == '12':
                return
                
            text_ascii(MENU_OPTIONS[choice][0])
            try:
                module = __import__('bugscanx.handler.runner', fromlist=[f'run_{choice}'])
                getattr(module, f'run_{choice}')()
                print("\n[yellow] Press Enter to continue...", end="")
                input()
            except KeyboardInterrupt:
                pass
    except (KeyboardInterrupt, EOFError):
        sys.exit()
