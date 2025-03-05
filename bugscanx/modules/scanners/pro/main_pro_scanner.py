import os
import json

from bugscanx.utils import get_input
from .direct_scanner import DirectScanner
from .proxy_scanner import ProxyScanner
from .ssl_scanner import SSLScanner
from .ping_scanner import PingScanner
from .udp_scanner import UdpScanner

def read_hosts(filename):
    with open(filename) as file:
        return [line.strip() for line in file]

def get_common_inputs(filename):
    output = get_input("Enter output filename", default=f"result_{os.path.basename(filename)}", validate_input=False)
    threads = get_input("Enter number of threads", "number", default="50")
    return output, threads

def get_input_direct():
    filename = get_input("Enter filename", "file")
    port_list = get_input("Enter ports", "number", default="80").split(',')
    output, threads = get_common_inputs(filename)
    method_list = get_input("Select HTTP method", "choice", multiselect=True, 
                           choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])
    
    scanner = DirectScanner()
    scanner.method_list = method_list
    scanner.host_list = read_hosts(filename)
    scanner.port_list = port_list
    
    return scanner, output, threads

def get_input_proxy():
    filename = get_input("Enter filename", "file")
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
    port_list = get_input("Enter ports", "number", default="80").split(',')
    output, threads = get_common_inputs(filename)
    bug = get_input("Enter bug (optional)", default="", validate_input=False)
    
    scanner = ProxyScanner()
    scanner.host_list = read_hosts(filename)
    scanner.target = target_url
    scanner.method = method
    scanner.path = path
    scanner.protocol = protocol
    scanner.bug = bug
    scanner.payload = payload
    scanner.port_list = port_list
    
    return scanner, output, threads

def get_input_ssl():
    filename = get_input("Enter filename", "file")
    output, threads = get_common_inputs(filename)
    
    scanner = SSLScanner()
    scanner.host_list = read_hosts(filename)
    
    return scanner, output, threads

def get_input_udp():
    filename = get_input("Enter filename", "file")
    output, threads = get_common_inputs(filename)
    
    scanner = UdpScanner()
    scanner.host_list = read_hosts(filename)
    scanner.udp_server_host = 'bugscanner.tppreborn.my.id'
    scanner.udp_server_port = '8853'
    
    return scanner, output, threads

def get_input_ping():
    filename = get_input("Enter filename", "file")
    port_list = get_input("Enter port list", "number", default="443").split(',')
    output, threads = get_common_inputs(filename)
    
    scanner = PingScanner()
    scanner.host_list = read_hosts(filename)
    scanner.port_list = port_list
    
    return scanner, output, threads

def get_user_input():
    mode = get_input("Select mode", "choice", choices=["direct", "proxy", "ping", "ssl", "udp"])
    
    input_handlers = {
        'direct': get_input_direct,
        'proxy': get_input_proxy,
        'ssl': get_input_ssl,
        'udp': get_input_udp,
        'ping': get_input_ping
    }
    
    scanner, output, threads = input_handlers[mode]()
    return scanner, output, threads, mode

def pro_main():
    scanner, output, threads, mode = get_user_input()
    scanner.threads = int(threads)
    scanner.start()

    if output:
        with open(output, 'a+') as file:
            if mode == 'proxy':
                json.dump(scanner.success_list(), file, indent=2)
            else:
                file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')
