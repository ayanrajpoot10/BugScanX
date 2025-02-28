from pathlib import Path
from rich import print
from bugscanx.utils import get_input

def file_manager(start_dir):
    current_dir = Path(start_dir).resolve()

    while True:
        items = sorted([i for i in current_dir.iterdir() if not i.name.startswith('.')],key=lambda x: (x.is_file(), x.name))
        directories = [d for d in items if d.is_dir()]
        files = [f for f in items if f.suffix == '.txt']

        short_dir = "\\".join(current_dir.parts[-3:])

        print(f"\n[cyan] Current Folder: {short_dir}[/cyan]")

        for idx, item in enumerate(directories + files, 1):
            color = "yellow" if item.is_dir() else "white"
            print(f"  {idx}. [{color}]{item.name}[/{color}]")

        print("\n[blue] 0. Back to previous folder[/blue]")

        selection = get_input("Enter number or filename")

        if selection == '0':
            current_dir = current_dir.parent

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

        print("[bold red] Invalid selection. Please try again.[/bold red]")