import ipaddress
from rich import print


def get_hosts_from_cidr(cidr_input):
    """
    Legacy function for backward compatibility.
    WARNING: This loads all IPs into memory. Use cidr_hosts_generator for large ranges.
    """
    hosts = []
    cidr_ranges = [c.strip() for c in cidr_input.split(',')]
    
    for cidr in cidr_ranges:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts.extend([str(ip) for ip in network.hosts()])
        except ValueError:
            continue
    return hosts


# def cidr_hosts_generator(cidr_input):
#     """
#     Generator function that yields hosts from CIDR ranges without loading all in memory.
#     Use this for memory-efficient CIDR scanning.
#     """
#     cidr_ranges = [c.strip() for c in cidr_input.split(',')]
    
#     for cidr in cidr_ranges:
#         try:
#             network = ipaddress.ip_network(cidr, strict=False)
#             for ip in network.hosts():
#                 yield str(ip)
#         except ValueError:
#             continue


def get_total_cidr_hosts(cidr_input):
    """
    Calculate the total number of hosts in CIDR ranges without generating them.
    """
    total = 0
    cidr_ranges = [c.strip() for c in cidr_input.split(',')]
    
    for cidr in cidr_ranges:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            # For host addresses, subtract network and broadcast addresses
            total += max(0, network.num_addresses - 2)
        except ValueError:
            continue
    return total


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
