import threading
import requests
from tqdm import tqdm
from rich import print
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.utils.common import get_input, clear_screen, is_cidr
from bugscanx.utils.config import SUBSCAN_TIMEOUT, EXCLUDE_LOCATIONS
from bugscanx.utils.cidr import get_hosts_from_cidr, read_cidrs_from_file

file_write_lock = threading.Lock()

def get_cidrs_input():
    input_type = get_input("Select input mode", "choice", choices=["Manual", "File"])
    
    if input_type == "File":
        filepath = get_input("Enter path to CIDR list file", "file")
        cidr_list = read_cidrs_from_file(filepath)
        if not cidr_list:
            print("[bold red] No valid CIDR ranges found in file.[/bold red]")
            return []
        ip_list = get_hosts_from_cidr(','.join(cidr_list))
    else:
        cidr_input = get_input("Enter CIDR range(s)", validators=[is_cidr])
        ip_list = get_hosts_from_cidr(cidr_input)
    
    if ip_list:
        print(f"[green] Found {len(ip_list)} valid IP addresses to scan[/green]")
    return ip_list

def check_http_response(host, port, method):
    protocol = "https" if port in ['443', '8443'] else "http"
    url = f"{protocol}://{host}:{port}"
    try:
        response = requests.request(method, url, timeout=SUBSCAN_TIMEOUT, allow_redirects=True)
        location = response.headers.get('Location', '').strip()
        if location in EXCLUDE_LOCATIONS:
            return None
        server_header = response.headers.get('Server', 'N/A')
        return response.status_code, server_header, port, host
    except requests.exceptions.RequestException:
        return None

def perform_scan(hosts, ports, output_file, threads, method):
    clear_screen()
    print(f"[bold green]Scanning using HTTP method: {method}...\n[/bold green]")
    headers = (f"[green]{'Code':<4}[/green] [cyan]{'Server':<15}[/cyan] [yellow]{'Port':<5}[/yellow] [magenta]{'IP Address'}[/magenta]")  
    separator = (f"[green]{'----':<4}[/green] [cyan]{'------':<15}[/cyan] [yellow]{'----':<5}[/yellow] [magenta]{'---------'}[/magenta]")  
    
    if output_file:
        output_path = Path(output_file)
        if not output_path.exists():
            with open(output_file, 'a') as file:
                file.write(f"{'Code':<4} {'Server':<15} {'Port':<5} {'IP Address'}\n")
                file.write(f"{'----':<4} {'------':<15} {'----':<5} {'---------'}\n")

    print(headers)
    print(separator)

    total_tasks = len(hosts) * len(ports)
    scanned, responded = 0, 0

    with tqdm(total=total_tasks, desc="Progress", unit="task", unit_scale=True) as pbar, \
         ThreadPoolExecutor(max_workers=threads) as executor:

        futures = {executor.submit(check_http_response, host, port, method): (host, port) for host in hosts for port in ports}

        for future in as_completed(futures):
            scanned += 1
            result = future.result()
            if result:
                responded += 1
                code, server, port, ip_address = result
                row = f"\033[32m{code:<4}\033[0m \033[36m{server:<15}\033[0m \033[33m{port:<5}\033[0m \033[35m{ip_address}\033[0m"
                pbar.write(row)
                if output_file:
                    with file_write_lock:
                        with open(output_file, 'a') as file:
                            file.write(f"{code:<4} {server:<15} {port:<5} {ip_address}\n")
            pbar.update(1)

    print(f"[bold green]\n Scan completed! {responded}/{scanned} IPs responded.[/bold green]")
    if output_file:
        print(f"[bold green] Results saved to {output_file}.[/bold green]")

def main():
    hosts = get_cidrs_input()
    if not hosts:
        return
    ports_input = get_input("Enter port(s)", "number", default="80")
    ports = ports_input.split(',')
    output_file = get_input("Enter output filename", default="scan_results.txt", validate_input=False)
    threads = int(get_input("Enter threads", "number", default="50"))
    http_method = get_input("Select the http method", "choice", choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])

    perform_scan(hosts, ports, output_file, threads, http_method)
