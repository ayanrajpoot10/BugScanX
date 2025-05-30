import os
import json

from bugscanx.utils.cidr import get_hosts_from_cidr
from bugscanx.utils.common import get_input, get_confirm, is_cidr
from .scanners import (
    DirectScanner,
    ProxyScanner,
    Proxy2Scanner,
    SSLScanner,
    PingScanner,
)


def read_hosts(filename=None, cidr=None):
    if filename:
        with open(filename) as file:
            return [line.strip() for line in file]
    elif cidr:
        return get_hosts_from_cidr(cidr)
    return []


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
    
    scanner = DirectScanner(
        host_list=read_hosts(filename, cidr),
        port_list=port_list,
        method_list=method_list,
        is_cidr_input=cidr is not None,
        no302=no302
    )
    
    return scanner, output, threads


def get_input_proxy():
    filename, cidr = get_host_input()
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
    
    scanner = ProxyScanner(
        host_list=read_hosts(filename, cidr),
        port_list=port_list,
        target=target_url,
        payload=payload
    )
    
    return scanner, output, threads


def get_input_proxy2():
    filename, cidr = get_host_input()
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
    
    scanner = Proxy2Scanner(
        method_list=method_list,
        host_list=read_hosts(filename, cidr),
        port_list=port_list,
        is_cidr_input=cidr is not None
    ).set_proxy(proxy, proxy_username, proxy_password)

    return scanner, output, threads


def get_input_ssl():
    filename, cidr = get_host_input()
    output, threads = get_common_inputs(filename or cidr)
    
    scanner = SSLScanner(
        host_list=read_hosts(filename, cidr),
        is_cidr_input=cidr is not None
    )
    
    return scanner, output, threads


def get_input_ping():
    filename, cidr = get_host_input()
    port_list = get_input("Enter port(s)", "number", default="443").split(',')
    output, threads = get_common_inputs(filename or cidr)
    
    scanner = PingScanner(
        host_list=read_hosts(filename, cidr),
        port_list=port_list,
        is_cidr_input=cidr is not None
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
