import ipaddress
from typing import List
from rich import print

def process_cidr(cidr: str) -> List[str]:
    """Convert a CIDR notation to a list of IP addresses"""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"[red] Invalid CIDR block {cidr}: {e}[/red]")
        return []

def process_input(input_str: str) -> List[str]:
    """Process an individual IP or CIDR and return a list of IPs"""
    if '/' in input_str:
        return process_cidr(input_str)
    else:
        return [input_str]

def process_file(file_path: str) -> List[str]:
    """Process a file containing IPs/CIDRs and return a list of IPs"""
    ips = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                ips.extend(process_input(line.strip()))
        return ips
    except Exception as e:
        print(f"[red] Error reading file {file_path}: {e}[/red]")
        return []
