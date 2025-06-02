import os
import json

from bugscanx.utils.common import get_input, get_confirm, is_cidr


def get_cidr_ranges_from_input(cidr_input):
    return [c.strip() for c in cidr_input.split(',')]


def get_common_inputs(input_source):
    if isinstance(input_source, str) and '/' in input_source:
        first_cidr = input_source.split(',')[0].strip()
        default_filename = f"result_{first_cidr.replace('/', '-')}.txt"
    else:
        default_filename = f"result_{os.path.basename(str(input_source))}"
    output = get_input(
        "Enter output filename",
        default=default_filename,
        validate_input=False
    )
    threads = get_input(
        "Enter threads",
        "number",
        default="50",
        allow_comma_separated=False
    )
    return output, threads


def get_host_input():
    filename = get_input("Enter filename", "file", mandatory=False)
    if not filename:
        cidr = get_input("Enter CIDR range(s)", validators=[is_cidr])
        return None, cidr
    return filename, None


def get_input_direct(no302=False):
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", "number", default="443").split(',')
    output, threads = get_common_inputs(filename or cidr)
    method_list = get_input(
        "Select HTTP method(s)",
        "choice",
        multiselect=True, 
        choices=[
            "GET", "HEAD", "POST", "PUT",
            "DELETE", "OPTIONS", "TRACE", "PATCH"
        ],
        transformer=lambda result: ', '.join(result) if isinstance(result, list) else result
    )
    
    if cidr:
        cidr_ranges = get_cidr_ranges_from_input(cidr)
        from .scanners.direct import CIDRDirectScanner        
        scanner = CIDRDirectScanner(
            method_list=method_list,
            cidr_ranges=cidr_ranges,
            port_list=port_list,
            no302=no302
        )
    else:
        from .scanners.direct import HostDirectScanner
        scanner = HostDirectScanner(
            method_list=method_list,
            input_file=filename,
            port_list=port_list,
            no302=no302
        )
    
    return scanner, output, threads


def get_input_proxy():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    target_url = get_input("Enter target url", default="in1.wstunnel.site")
    default_payload = (
        "GET / HTTP/1.1[crlf]"
        "Host: [host][crlf]"
        "Connection: Upgrade[crlf]"
        "Upgrade: websocket[crlf][crlf]"
    )
    payload = get_input("Enter payload", default=default_payload)
    port_list = get_input("Enter port(s)", "number", default="80").split(',')
    output, threads = get_common_inputs(filename or cidr)
    
    if cidr:
        cidr_ranges = get_cidr_ranges_from_input(cidr)
        from .scanners.proxy_check import CIDRProxyScanner
        scanner = CIDRProxyScanner(
            cidr_ranges=cidr_ranges,
            port_list=port_list,
            target=target_url,
            payload=payload,
        )
    else:
        from .scanners.proxy_check import HostProxyScanner
        scanner = HostProxyScanner(
            input_file=filename,
            port_list=port_list,
            target=target_url,
            payload=payload,
        )
    
    return scanner, output, threads


def get_input_proxy2():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", "number", default="80").split(',')
    output, threads = get_common_inputs(filename or cidr)
    method_list = get_input(
        "Select HTTP method(s)",
        "choice",
        multiselect=True, 
        choices=[
            "GET", "HEAD", "POST", "PUT",
            "DELETE", "OPTIONS", "TRACE", "PATCH"
        ],
        transformer=lambda result: ', '.join(result) if isinstance(result, list) else result
    )
    
    proxy = get_input("Enter proxy", instruction="(proxy:port)")
    
    use_auth = get_confirm(" Use proxy authentication?")
    proxy_username = None
    proxy_password = None
    
    if use_auth:
        proxy_username = get_input("Enter proxy username")
        proxy_password = get_input("Enter proxy password")
    
    if cidr:
        cidr_ranges = get_cidr_ranges_from_input(cidr)
        from .scanners.proxy_request import CIDRProxy2Scanner
        scanner = CIDRProxy2Scanner(
            method_list=method_list,
            cidr_ranges=cidr_ranges,
            port_list=port_list,
        ).set_proxy(proxy, proxy_username, proxy_password)
    else:
        from .scanners.proxy_request import HostProxy2Scanner
        scanner = HostProxy2Scanner(
            method_list=method_list,
            input_file=filename,
            port_list=port_list,
        ).set_proxy(proxy, proxy_username, proxy_password)

    return scanner, output, threads


def get_input_ssl():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    output, threads = get_common_inputs(filename or cidr)
    
    if cidr:
        cidr_ranges = get_cidr_ranges_from_input(cidr)
        from .scanners.ssl import CIDRSSLScanner
        scanner = CIDRSSLScanner(
            cidr_ranges=cidr_ranges,
        )
    else:
        from .scanners.ssl import HostSSLScanner
        scanner = HostSSLScanner(
            input_file=filename,
        )
    
    return scanner, output, threads


def get_input_ping():
    filename, cidr = get_host_input()
    if filename is None and cidr is None:
        return None, None, None
        
    port_list = get_input("Enter port(s)", "number", default="443").split(',')
    output, threads = get_common_inputs(filename or cidr)
    
    if cidr:
        cidr_ranges = get_cidr_ranges_from_input(cidr)
        from .scanners.ping import CIDRPingScanner
        scanner = CIDRPingScanner(
            port_list=port_list,
            cidr_ranges=cidr_ranges,
        )
    else:
        from .scanners.ping import HostPingScanner
        scanner = HostPingScanner(
            input_file=filename,
            port_list=port_list,
        )
    
    return scanner, output, threads


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
    
    scanner, output, threads = input_handlers[mode]()
    return scanner, output, threads


def main():
    scanner, output, threads = get_user_input()
    scanner.threads = int(threads)
    scanner.start()

    if output:
        with open(output, 'a+') as file:
            json.dump(scanner.get_success(), file, indent=2)
