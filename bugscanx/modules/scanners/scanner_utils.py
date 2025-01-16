from pathlib import Path
from colorama import Fore
from bugscanx.modules import get_input, not_empty_validator


def file_manager(start_dir, max_up_levels=None):
    current_dir = Path(start_dir).resolve()
    levels_up = 0

    while True:
        items = list(current_dir.iterdir())
        files = [f for f in items if f.is_file() and f.suffix == '.txt']
        directories = [d for d in items if d.is_dir()]

        if not files and not directories:
            print(Fore.RED + " No .txt files or directories found.")
            return None

        print(Fore.CYAN + f"\n Current Directory: {current_dir}")

        for idx, item in enumerate(directories + files, 1):
            icon = "📂" if item.is_dir() else "📄"
            color = Fore.YELLOW if item.is_dir() else Fore.WHITE
            print(f"  {idx}. {icon} {color}{item.name}")

        print(Fore.LIGHTBLUE_EX + "\n 0. Back to the previous folder")

        selection = get_input(prompt=" Enter the number or filename", validator=not_empty_validator)

        if selection == '0':
            if max_up_levels is not None and levels_up >= max_up_levels:
                print(Fore.RED + " Maximum directory level reached.")
            elif current_dir.parent == current_dir:
                print(Fore.RED + " Already at the root directory.")
            else:
                current_dir = current_dir.parent
                levels_up += 1
            continue

        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(directories + files):
                selected_item = (directories + files)[index]
                if selected_item.is_dir():
                    current_dir, levels_up = selected_item, 0
                else:
                    return selected_item
            continue

        file_path = current_dir / selection
        if file_path.is_file() and file_path.suffix == '.txt':
            return file_path

        print(Fore.RED + " Invalid selection. Please try again.")