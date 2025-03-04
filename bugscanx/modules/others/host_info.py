import socket
import ssl
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.exceptions import RequestException
from rich import print

from bugscanx.utils import get_input

HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]

def check_http_method(url, method):
    try:
        response = requests.request(method, url, timeout=5)
        return method, response.status_code, dict(response.headers)
    except RequestException as e:
        return method, None, str(e)

def print_result(method, status_code, headers):
    print(f"\n[bold yellow]{'='*50}[/bold yellow]")
    print(f"[bold cyan]HTTP Method:[/bold cyan] {method}")
    print(f"[bold magenta]Status Code:[/bold magenta] {status_code}")
    
    if isinstance(headers, dict):
        print("[bold green]Headers:[/bold green]")
        for header_name, header_value in headers.items():
            print(f"  {header_name}: {header_value}")
    else:
        print(f"[bold red]Error:[/bold red] {headers}")

def result_printer(result_queue):
    while True:
        result = result_queue.get()
        if result is None:
            break
        method, status_code, headers = result
        print_result(method, status_code, headers)
        result_queue.task_done()

def check_http_methods(url):
    result_queue = queue.Queue()
    printer_thread = threading.Thread(target=result_printer, args=(result_queue,))
    printer_thread.start()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(check_http_method, url, method) for method in HTTP_METHODS]
        for future in as_completed(futures):
            result_queue.put(future.result())
    
    result_queue.put(None)
    printer_thread.join()

def get_host_ips(hostname):
    try:
        ips = socket.getaddrinfo(hostname, None)
        unique_ips = list(set(ip[4][0] for ip in ips))
        return unique_ips
    except socket.gaierror as e:
        return [f"Error resolving hostname: {e}"]

def get_sni_info(hostname, port=443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return {
                    'version': ssock.version(),
                    'cipher': ssock.cipher(),
                    'cert': ssock.getpeercert()
                }
    except Exception as e:
        return f"Error getting SNI info: {e}"

def osint_main():
    host = get_input("Enter the host (e.g., example.com)")
    protocol = get_input("Enter the protocol", "choice", choices=["http", "https"])
    url = f"{protocol}://{host}"

    print("\n[bold cyan]Target Information[/bold cyan]")
    print(f"[bold white]Hostname:[/bold white] {host}")
    print(f"[bold white]Target URL:[/bold white] {url}\n")
    
    ip_addresses = get_host_ips(host)
    print("[bold white]IP Addresses:[/bold white]")
    for ip in ip_addresses:
        print(f"  → {ip}")

    print("\n[bold cyan]HTTP Methods Information[/bold cyan]")
    check_http_methods(url)

    if protocol == "https":
        print("\n[bold cyan]SNI Information[/bold cyan]")
        sni_info = get_sni_info(host)
        if isinstance(sni_info, dict):
            print(f"\n[bold white]SSL Version:[/bold white] {sni_info['version']}")
            print(f"[bold white]Cipher Suite:[/bold white] {sni_info['cipher'][0]}")
            print(f"[bold white]Cipher Bits:[/bold white] {sni_info['cipher'][1]}")
            
            cert = sni_info['cert']
            print("\n[bold white]Certificate Details:[/bold white]")
            for key, value in cert.items():
                if isinstance(value, list):
                    print(f"\n[bold green]{key}:[/bold green]")
                    for item in value:
                        print(f"  → {item}")
                else:
                    print(f"[bold green]{key}:[/bold green] {value}")
        else:
            print(f"[bold red]{sni_info}[/bold red]")
