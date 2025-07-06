import sys
from rich import print
from bugscanx import banner, text_ascii, handlers


MENU_OPTIONS = {
    '1': ("HOST SCANNER", "bold cyan"),
    '2': ("SUBFINDER", "bold magenta"),
    '3': ("IP LOOKUP", "bold cyan"),
    '4': ("FILE TOOLKIT", "bold magenta"),
    '5': ("PORT SCANNER", "bold white"),
    '6': ("DNS RECORD", "bold green"),
    '7': ("HOST INFO", "bold blue"),
    '8': ("HELP", "bold yellow"),
    '9': ("UPDATE", "bold magenta"),
    '0': ("EXIT", "bold red"),
}


def main():
    try:
        while True:
            menu = (
                f"[{color}] [{k}]{' ' if len(k)==1 else ''} {desc}"
                for k, (desc, color) in MENU_OPTIONS.items()
            )
            banner()
            print('\n'.join(menu))

            choice = input("\n \033[36m[-]  Your Choice: \033[0m")
            if choice not in MENU_OPTIONS:
                continue

            if choice == '0':
                return

            text_ascii(MENU_OPTIONS[choice][0])
            try:
                getattr(handlers, f'run_{choice}')()
                print("\n[yellow] Press Enter to continue...", end="")
                input()
            except KeyboardInterrupt:
                pass
    except (KeyboardInterrupt, EOFError):
        sys.exit()
