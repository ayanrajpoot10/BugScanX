import concurrent.futures
import socket

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

def check_http_methods(url):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(check_http_method, url, method) for method in HTTP_METHODS]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results

def get_host_ips(hostname):
    try:
        ips = socket.getaddrinfo(hostname, None)
        unique_ips = list(set(ip[4][0] for ip in ips))
        return unique_ips
    except socket.gaierror as e:
        return [f"Error resolving hostname: {e}"]

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        http_methods_future = executor.submit(check_http_methods, url)

    http_methods_results = http_methods_future.result()
    
    print("\n[bold cyan]HTTP Methods Information[/bold cyan]")
    
    for method, status_code, headers in http_methods_results:
        print(f"\n[bold yellow]{'='*50}[/bold yellow]")
        print(f"[bold cyan]HTTP Method:[/bold cyan] {method}")
        print(f"[bold magenta]Status Code:[/bold magenta] {status_code}")
        
        if isinstance(headers, dict):
            print("[bold green]Headers:[/bold green]")
            for header_name, header_value in headers.items():
                print(f"  {header_name}: {header_value}")
        else:
            print(f"[bold red]Error:[/bold red] {headers}")
