import socket
import ssl
import queue
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
from rich import print
from bugscanx.utils.common import get_input

HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]

CDN_PROVIDERS = {
    "Cloudflare": ["cf-ray", "cf-cache-status"],
    "Akamai": ["x-akamai-transformed", "akamai-cache-status"],
    "Fastly": ["fastly-debug", "x-served-by"],
    "Amazon CloudFront": ["x-amz-cf-id"],
    "Google Cloud CDN": ["x-goog-cache-status"],
    "Microsoft Azure CDN": ["x-azure-ref"],
    "StackPath": ["x-stackpath-xxid"],
    "Sucuri": ["x-sucuri-id"]
}

def check_cdn(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        
        detected_cdns = []
        for provider, indicators in CDN_PROVIDERS.items():
            if any(header.lower() in map(str.lower, headers.keys()) for header in indicators):
                detected_cdns.append(provider)
        
        return detected_cdns, headers
    except RequestException as e:
        return None, str(e)

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
        return unique_ips, None
    except socket.gaierror as e:
        return [], f"Error resolving hostname: {e}"

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

def main():
    host = get_input("Enter host")
    protocol = get_input("Select protocol", "choice", choices=["http", "https"])
    url = f"{protocol}://{host}"

    print("\n[bold cyan]Target Information[/bold cyan]")
    print(f"[bold white]Hostname:[/bold white] {host}")
    print(f"[bold white]Target URL:[/bold white] {url}\n")
    
    ip_addresses, dns_error = get_host_ips(host)
    
    if dns_error:
        print(f"\n[bold red] Invalid host. Please check the hostname and try again.[/bold red]")
        return
    
    print("[bold white]IP Addresses:[/bold white]")
    for ip in ip_addresses:
        print(f"  → {ip}")
    
    print("\n[bold cyan]CDN Information[/bold cyan]")
    detected_cdns, cdn_response = check_cdn(url)
    if detected_cdns is None:
        print(f"[bold red]Error checking CDN: {cdn_response}[/bold red]")
    else:
        if detected_cdns:
            print("[bold white]CDN Providers Detected:[/bold white]")
            for cdn in detected_cdns:
                print(f"  → {cdn}")
        else:
            print("[bold white]No known CDN detected.[/bold white]")

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
