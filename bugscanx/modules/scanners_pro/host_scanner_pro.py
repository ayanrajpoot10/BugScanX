import os
import json
from bugscanx.utils.cidr import get_hosts_from_cidr
from bugscanx.utils.common import get_input, get_confirm, is_cidr
from .scanners.direct import DirectScanner
from .scanners.proxy_check import ProxyScanner
from .scanners.proxy_request import Proxy2Scanner
from .scanners.ssl import SSLScanner
from .scanners.ping import PingScanner

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
    output = get_input("Enter output filename", default=default_filename, validate_input=False)
    threads = get_input("Enter threads", "number", default="50", allow_comma_separated=False)
    return output, threads

def get_host_input():
    filename = get_input("Enter filename", "file", mandatory=False)
    if not filename:
        cidr = get_input("Enter CIDR range(s)", validators=[is_cidr])
        return None, cidr
    return filename, None

def list_to_comma_separated(result):
    return ', '.join(result) if isinstance(result, list) else result

def get_input_direct(no302=False):
    filename, cidr = get_host_input()
    port_list = get_input("Enter port(s)", "number", default="80").split(',')
    output, threads = get_common_inputs(filename or cidr)
    method_list = get_input("Select HTTP method(s)", "choice", multiselect=True, 
                           choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"],
                           transformer=list_to_comma_separated)
    
    scanner = DirectScanner()
    scanner.method_list = method_list
    scanner.host_list = read_hosts(filename, cidr)
    scanner.port_list = port_list
    scanner.no302 = no302
    scanner.is_cidr_input = cidr is not None
    
    return scanner, output, threads

def get_input_proxy():
    filename, cidr = get_host_input()
    target_url = get_input("Enter target url", default="in1.wstunnel.site")
    method = get_input("Enter HTTP method", default="GET")
    path = get_input("Enter path", default="/")
    protocol = get_input("Enter protocol", default="HTTP/1.1")
    default_payload = (
        "[method] [path] [protocol][crlf]"
        "Host: [host][crlf]"
        "Connection: Upgrade[crlf]"
        "Upgrade: websocket[crlf][crlf]"
    )
    payload = get_input("Enter payload", default=default_payload)
    port_list = get_input("Enter port(s)", "number", default="80").split(',')
    output, threads = get_common_inputs(filename or cidr)
    bug = get_input("Enter bug", default="", validate_input=False, instruction="(optional)")
    
    scanner = ProxyScanner()
    scanner.host_list = read_hosts(filename, cidr)
    scanner.target = target_url
    scanner.method = method
    scanner.path = path
    scanner.protocol = protocol
    scanner.bug = bug
    scanner.payload = payload
    scanner.port_list = port_list
    
    return scanner, output, threads

def get_input_proxy2():
    filename, cidr = get_host_input()
    port_list = get_input("Enter port(s)", "number", default="80").split(',')
    output, threads = get_common_inputs(filename or cidr)
    method_list = get_input("Select HTTP method(s)", "choice", multiselect=True, 
                           choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"],
                           transformer=list_to_comma_separated)
    
    proxy = get_input("Enter proxy", instruction="(proxy:port)")
    
    use_auth = get_confirm(" Use proxy authentication?")
    proxy_username = None
    proxy_password = None
    
    if use_auth:
        proxy_username = get_input("Enter proxy username")
        proxy_password = get_input("Enter proxy password")
    
    scanner = Proxy2Scanner()
    scanner.set_proxy(proxy, proxy_username, proxy_password)
    scanner.method_list = method_list
    scanner.host_list = read_hosts(filename, cidr)
    scanner.port_list = port_list
    scanner.is_cidr_input = cidr is not None
    
    return scanner, output, threads

def get_input_ssl():
    filename, cidr = get_host_input()
    tls_version = get_input("Select TLS version", "choice", 
                           choices=list(SSLScanner.TLS_VERSIONS.keys()),
                           default="TLS 1.2")
    output, threads = get_common_inputs(filename or cidr)
    
    scanner = SSLScanner()
    scanner.host_list = read_hosts(filename, cidr)
    scanner.tls_version = SSLScanner.TLS_VERSIONS[tls_version]
    
    return scanner, output, threads

def get_input_ping():
    filename, cidr = get_host_input()
    port_list = get_input("Enter port(s)", "number", default="443").split(',')
    output, threads = get_common_inputs(filename or cidr)
    
    scanner = PingScanner()
    scanner.host_list = read_hosts(filename, cidr)
    scanner.port_list = port_list
    scanner.is_cidr_input = cidr is not None
    
    return scanner, output, threads

def get_user_input():
    mode = get_input("Select scanning mode", "choice", 
                    choices=["Direct", "Direct-no302", "Proxy-check", "Proxy-request", "Ping", "SSL"])
    
    input_handlers = {
        'Direct': lambda: get_input_direct(no302=False),
        'Direct-no302': lambda: get_input_direct(no302=True),
        'Proxy-check': get_input_proxy,
        'Proxy-request': get_input_proxy2,
        'Ping': get_input_ping,
        'SSL': get_input_ssl
    }
    
    scanner, output, threads = input_handlers[mode]()
    return scanner, output, threads, mode

def main():
    scanner, output, threads, mode = get_user_input()
    scanner.threads = int(threads)
    scanner.start()

    if output:
        with open(output, 'a+') as file:
            if mode == 'Proxy-check':
                json.dump(scanner.success_list(), file, indent=2)
            else:
                file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')
