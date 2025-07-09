import ipaddress
from rich import print
from bugscanx.utils.prompts import get_input, get_confirm


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


def get_cidr_ranges_from_input(cidr_input):
    return [c.strip() for c in cidr_input.split(',')]


def get_common_inputs():
    default_filename = "results.txt"
    output = get_input(
        "Enter output filename",
        default=default_filename
    )
    threads = get_input(
        "Enter threads",
        validators="number",
        default="50"
    )
    return output, threads


def get_host_input():
    filename = get_input("Enter filename", input_type="file", validators="file", mandatory=False)
    if not filename:
        cidr = get_input("Enter CIDR range(s)", validators="cidr", mandatory=False)
        if not cidr:
            cidr_file = get_input(
                "Enter CIDR file", input_type="file", validators="file")
            cidr = read_cidrs_from_file(cidr_file) if cidr_file else None
        return None, cidr
    return filename, None


def get_input_direct(no302=False):
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", validators="number", default="80").split(',')
    timeout = get_input("Enter timeout (seconds)", validators="number", default="3")
    output, threads = get_common_inputs()
    method_list = get_input(
        "Select HTTP method(s)",
        input_type="choice",
        multiselect=True, 
        choices=[
            "GET", "HEAD", "POST", "PUT",
            "DELETE", "OPTIONS", "TRACE", "PATCH"
        ],
        transformer=lambda result: ', '.join(result) if isinstance(result, list) else result
    )
    
    if cidr:
        try:
            cidr_ranges = get_cidr_ranges_from_input(cidr)
        except AttributeError:
            cidr_ranges = cidr
        from .scanners.direct import CIDRDirectScanner        
        scanner = CIDRDirectScanner(
            method_list=method_list,
            cidr_ranges=cidr_ranges,
            port_list=port_list,
            no302=no302,
            timeout=int(timeout),
            output_file=output
        )
    else:
        from .scanners.direct import HostDirectScanner
        scanner = HostDirectScanner(
            method_list=method_list,
            input_file=filename,
            port_list=port_list,
            no302=no302,
            timeout=int(timeout),
            output_file=output
        )
    
    return scanner, threads


def get_input_proxy():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    target_url = get_input("Enter target url", default="in1.wstunnel.site", validators="required")
    default_payload = (
        "GET / HTTP/1.1[crlf]"
        "Host: [host][crlf]"
        "Connection: Upgrade[crlf]"
        "Upgrade: websocket[crlf][crlf]"
    )
    payload = get_input("Enter payload", default=default_payload, validators="required")
    port_list = get_input("Enter port(s)", validators="number", default="80").split(',')
    output, threads = get_common_inputs()
    
    if cidr:
        try:
            cidr_ranges = get_cidr_ranges_from_input(cidr)
        except AttributeError:
            cidr_ranges = cidr
        from .scanners.proxy_check import CIDRProxyScanner
        scanner = CIDRProxyScanner(
            cidr_ranges=cidr_ranges,
            port_list=port_list,
            target=target_url,
            payload=payload,
            output_file=output
        )
    else:
        from .scanners.proxy_check import HostProxyScanner
        scanner = HostProxyScanner(
            input_file=filename,
            port_list=port_list,
            target=target_url,
            payload=payload,
            output_file=output
        )
    
    return scanner, threads


def get_input_proxy2():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", validators="number", default="80").split(',')
    output, threads = get_common_inputs()
    method_list = get_input(
        "Select HTTP method(s)",
        input_type="choice",
        multiselect=True, 
        choices=[
            "GET", "HEAD", "POST", "PUT",
            "DELETE", "OPTIONS", "TRACE", "PATCH"
        ],
        transformer=lambda result: ', '.join(result) if isinstance(result, list) else result
    )
    
    proxy = get_input("Enter proxy", instruction="(proxy:port)", validators="required")
    
    use_auth = get_confirm(" Use proxy authentication?")
    proxy_username = None
    proxy_password = None
    
    if use_auth:
        proxy_username = get_input("Enter proxy username", validators="required")
        proxy_password = get_input("Enter proxy password", validators="required")
    
    if cidr:
        try:
            cidr_ranges = get_cidr_ranges_from_input(cidr)
        except AttributeError:
            cidr_ranges = cidr
        from .scanners.proxy_request import CIDRProxy2Scanner
        scanner = CIDRProxy2Scanner(
            method_list=method_list,
            cidr_ranges=cidr_ranges,
            port_list=port_list,
            output_file=output
        ).set_proxy(proxy, proxy_username, proxy_password)
    else:
        from .scanners.proxy_request import HostProxy2Scanner
        scanner = HostProxy2Scanner(
            method_list=method_list,
            input_file=filename,
            port_list=port_list,
            output_file=output
        ).set_proxy(proxy, proxy_username, proxy_password)

    return scanner, threads


def get_input_ssl():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    output, threads = get_common_inputs()
    
    if cidr:
        try:
            cidr_ranges = get_cidr_ranges_from_input(cidr)
        except AttributeError:
            cidr_ranges = cidr
        from .scanners.ssl import CIDRSSLScanner
        scanner = CIDRSSLScanner(
            cidr_ranges=cidr_ranges,
            output_file=output
        )
    else:
        from .scanners.ssl import HostSSLScanner
        scanner = HostSSLScanner(
            input_file=filename,
            output_file=output
        )
    
    return scanner, threads


def get_input_ping():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", validators="number", default="443").split(',')
    output, threads = get_common_inputs()
    
    if cidr:
        try:
            cidr_ranges = get_cidr_ranges_from_input(cidr)
        except AttributeError:
            cidr_ranges = cidr
        from .scanners.ping import CIDRPingScanner
        scanner = CIDRPingScanner(
            port_list=port_list,
            cidr_ranges=cidr_ranges,
            output_file=output
        )
    else:
        from .scanners.ping import HostPingScanner
        scanner = HostPingScanner(
            input_file=filename,
            port_list=port_list,
            output_file=output
        )
    
    return scanner, threads


def get_user_input():
    mode = get_input(
        "Select scanning mode",
        "choice", 
        choices=[
            "Direct", "DirectNon302", "ProxyTest",
            "ProxyRoute", "Ping", "SSL"
        ]
    )
    
    input_handlers = {
        'Direct': lambda: get_input_direct(no302=False),
        'DirectNon302': lambda: get_input_direct(no302=True),
        'ProxyTest': get_input_proxy,
        'ProxyRoute': get_input_proxy2,
        'Ping': get_input_ping,
        'SSL': get_input_ssl
    }
    
    scanner, threads = input_handlers[mode]()
    return scanner, threads


def main():
    scanner, threads = get_user_input()
    scanner.threads = int(threads)
    scanner.start()
