import ipaddress
from rich import print


def read_cidrs_from_file(filepath):
    valid_cidrs = []
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    ipaddress.ip_network(line, strict=False)
                    valid_cidrs.append(line)
                except ValueError:
                    pass
            
        return valid_cidrs
    except Exception as e:
        print(f"[bold red]Error reading file: {e}[/bold red]")
        return []
