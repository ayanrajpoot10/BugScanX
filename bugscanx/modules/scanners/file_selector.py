import sys
from pathlib import Path
from rich.console import Console
from bugscanx.utils.common import get_input

def file_manager(start_dir):
    current_dir = Path(start_dir).resolve()
    console = Console()
    previous_lines = 0

    while True:
        if previous_lines > 0:
            for _ in range(previous_lines):
                sys.stdout.write("\033[1A")
                sys.stdout.write("\033[2K")
            sys.stdout.flush()
        
        lines_printed = 0
        
        items = sorted([i for i in current_dir.iterdir() if not i.name.startswith('.')],key=lambda x: (x.is_file(), x.name))
        directories = [d for d in items if d.is_dir()]
        files = [f for f in items if f.suffix == '.txt']

        short_dir = "\\".join(current_dir.parts[-3:])

        console.print(f"[cyan] Current Folder: {short_dir}[/cyan]")
        lines_printed += 1

        for idx, item in enumerate(directories + files, 1):
            color = "yellow" if item.is_dir() else "white"
            console.print(f"  {idx}. [{color}]{item.name}[/{color}]")
            lines_printed += 1

        console.print("\n[blue] 0. Back to previous folder[/blue]")
        lines_printed += 2

        selection = get_input("Enter number or filename")
        lines_printed += 1
        
        previous_lines = lines_printed

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

        console.print("[bold red] Invalid selection. Please try again.[/bold red]")
        previous_lines += 1
