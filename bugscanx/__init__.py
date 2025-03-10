import threading

def import_modules_in_background():
    def import_task():
        try:
            from bugscanx.modules.scanners.pro import main_pro_scanner
            from bugscanx.modules.scrappers.subfinder import sub_finder
        except Exception:
            pass

    thread = threading.Thread(target=import_task, daemon=True)
    thread.start()

import_modules_in_background()

import os
from rich import print
from pyfiglet import Figlet
from rich.text import Text

def banner():
    banner_text = """
    [bold red]╔╗[/bold red] [turquoise2]╦ ╦╔═╗╔═╗╔═╗╔═╗╔╗╔═╗ ╦[/turquoise2]
    [bold red]╠╩╗[/bold red][turquoise2]║ ║║ ╦╚═╗║  ╠═╣║║║╔╩╦╝[/turquoise2]
    [bold red]╚═╝[/bold red][turquoise2]╚═╝╚═╝╚═╝╚═╝╩ ╩╝╚╝╩ ╚═[/turquoise2]
     [bold magenta]Dᴇᴠᴇʟᴏᴘᴇʀ: Aʏᴀɴ Rᴀᴊᴘᴏᴏᴛ
      Tᴇʟᴇɢʀᴀᴍ: @BᴜɢSᴄᴀɴX[/bold magenta]
    """
    print(banner_text)

figlet = Figlet(font="calvin_s")

def text_ascii(text, color="white", shift=2):
    ascii_banner = figlet.renderText(text)
    shifted_banner = "\n".join((" " * shift) + line for line in ascii_banner.splitlines())
    print(Text(shifted_banner, style=color))
    print()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')