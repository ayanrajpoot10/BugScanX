import ipaddress

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
