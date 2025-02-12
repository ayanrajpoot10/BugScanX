from pathlib import Path
from colorama import Fore
from bugscanx.utils import get_input, not_empty_validator

def file_manager(start_dir):
    current_dir = Path(start_dir).resolve()

    while True:
        items = sorted([i for i in current_dir.iterdir() if not i.name.startswith('.')],key=lambda x: (x.is_file(), x.name))
        directories = [d for d in items if d.is_dir()]
        files = [f for f in items if f.suffix == '.txt']

        short_dir = "\\".join(current_dir.parts[-3:])

        print(Fore.CYAN + f"\n Current Folder: {short_dir}" + Fore.RESET)

        for idx, item in enumerate(directories + files, 1):
            color = Fore.YELLOW if item.is_dir() else Fore.WHITE
            print(f"  {idx}. {color}{item.name}{Fore.RESET}")

        print(Fore.LIGHTBLUE_EX + "\n 0. Back to the previous folder")

        selection = get_input(" Enter the number or filename", validator=not_empty_validator)

        if selection == '0':
            if current_dir != current_dir.parent:
                current_dir = current_dir.parent
            else:
                print(Fore.RED + " Already at the root directory.")
            continue

        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(directories) + len(files):
                selected_item = (directories + files)[index]
                if selected_item.is_dir():
                    current_dir = selected_item
                else:
                    return selected_item
            continue

        file_path = current_dir / selection
        if file_path.is_file() and file_path.suffix == '.txt':
            return file_path

        print(Fore.RED + " Invalid selection. Please try again.")