import ipaddress
from rich import print

def get_hosts_from_cidr(cidr_input):
    hosts = []
    cidr_ranges = [c.strip() for c in cidr_input.split(',')]
    
    for cidr in cidr_ranges:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts.extend([str(ip) for ip in network.hosts()])
        except ValueError:
            continue
    return hosts

def validate_cidr(cidr):
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

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
            
        if valid_cidrs:
            print(f"[green] Successfully loaded {len(valid_cidrs)} valid CIDR ranges[/green]")
            
        return valid_cidrs
    except Exception as e:
        print(f"[bold red]Error reading file: {e}[/bold red]")
        return []
