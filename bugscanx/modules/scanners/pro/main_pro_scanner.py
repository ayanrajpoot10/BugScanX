import json
import os

from bugscanx.utils import get_input
from .direct_scanner import DirectScanner
from .proxy_scanner import ProxyScanner
from .ssl_scanner import SSLScanner
from .ping_scanner import PingScanner

def read_hosts(filename):
    with open(filename) as file:
        for line in file:
            yield line.strip()

def get_user_input():
    mode = get_input(" Select the mode", "choice", choices=["direct", "proxy", "ssl", "udp", "ping"], newline_before=True)
    if mode == 'direct':
        filename = get_input(" Enter the filename", "file")
        port_list = get_input(" Enter the port list", "number", default="80")
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(filename)}")
        threads = get_input(" Enter the number of threads", "number", default= "50")
        method_list = get_input(" Select the http method:", "choice", choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])
        return{
            'filename': filename,
            'method_list': method_list,
            'port_list': port_list,
            'output': output,
            'threads': threads,
            'mode': mode
        }
    elif mode == 'proxy':
        proxy_file = get_input(" Enter the file name of proxy file", "file")
        target_url = get_input(" Enter target url", default="in1.wstunnel.site")
        method = get_input(" Enter HTTP method", default="GET")
        path = get_input(" Enter path", default="/")
        protocol = get_input(" Enter protocol", default="HTTP/1.1")
        default_payload = (
            "[method] [path] [protocol][crlf]"
            "Host: [host][crlf]"
            "Connection: Upgrade[crlf]"
            "Upgrade: websocket[crlf][crlf]"
        )
        payload = get_input(" Enter payload", default=default_payload)
        port_list = get_input(" Enter the port list", "number", default="80")
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(proxy_file)}")
        threads = get_input(" Enter the number of threads", "number", default="50")
        bug = get_input(" Enter bug (optional)", default="", validate_input=False)
        return {
            'proxy_file': proxy_file,
            'output': output,
            'threads': threads,
            'target_url': target_url,
            'method': method,
            'path': path,
            'protocol': protocol,
            'bug': bug,
            'payload': payload,
            'port_list': port_list,
            'mode': mode
        }

    elif mode == 'ssl':
        filename = get_input(" Enter the filename", "file")
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(filename)}")
        threads = get_input(" Enter the number of threads", "number", default= "50")
        return{
            'filename': filename,
            'output': output,
            'threads': threads,
            'mode': mode
        }
    
    elif mode == 'udp':
        filename = get_input(" Enter the filename", "file")
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(filename)}")
        threads = get_input(" Enter the number of threads", "number", default= "50")
        return{
            'filename': filename,
            'output': output,
            'threads': threads,
            'mode': mode
        }

    elif mode == 'ping':
        filename = get_input(" Enter the filename", "file")
        port_list = get_input(" Enter the port list", "number", default="80")
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(filename)}")
        threads = get_input(" Enter the number of threads", "number", default="50")
        return {
            'filename': filename,
            'port_list': port_list,
            'output': output,
            'threads': threads,
            'mode': mode
        }

def main():
    user_input = get_user_input()

    if user_input['mode'] == 'direct':

        method_list = user_input['method_list'].split(',')
        host_list = read_hosts(user_input['filename'])
        port_list = user_input['port_list'].split(',')

        scanner = DirectScanner()
        scanner.method_list = method_list
        scanner.host_list = host_list
        scanner.port_list = port_list

    elif user_input['mode'] == 'proxy':

        proxy_list = list(read_hosts(user_input['proxy_file']))
        port_list = user_input['port_list'].split(',')

        scanner = ProxyScanner()
        scanner.proxy_list = proxy_list
        scanner.target = user_input['target_url']
        scanner.method = user_input['method']
        scanner.path = user_input['path']
        scanner.protocol = user_input['protocol']
        scanner.bug = user_input['bug']
        scanner.payload = user_input['payload']
        scanner.port_list = port_list

    elif user_input['mode'] == 'ssl':

        host_list = read_hosts(user_input['filename'])

        scanner = SSLScanner()
        scanner.host_list = host_list


    elif user_input['mode'] == 'udp':
        from .udp_scanner import UdpScanner
        host_list = read_hosts(user_input['filename'])
        scanner = UdpScanner()
        scanner.host_list = host_list
        scanner.udp_server_host = 'bugscanner.tppreborn.my.id'
        scanner.udp_server_port = '8853'

    elif user_input['mode'] == 'ping':

        host_list = read_hosts(user_input['filename'])
        port_list = user_input['port_list'].split(',')

        scanner = PingScanner()
        scanner.host_list = host_list
        scanner.port_list = port_list

    scanner.threads = int(user_input['threads'])
    scanner.start()

    if user_input['output']:
        with open(user_input['output'], 'a+') as file:
            if user_input['mode'] == 'proxy':
                json.dump(scanner.success_list(), file, indent=2)
            else:
                file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')
