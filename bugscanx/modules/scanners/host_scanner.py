import socket
import urllib3
import requests
from pathlib import Path
from threading import Lock
from tqdm import tqdm
from rich import print
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.utils.file_selector import file_manager
from bugscanx.utils.common import clear_screen, get_input
from bugscanx.utils.config import SUBSCAN_TIMEOUT, EXCLUDE_LOCATIONS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

file_write_lock = Lock()

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except (FileNotFoundError, IOError) as e:
        print(f"[red]Error reading file: {e}[/red]")
        return []

def check_http_response(host, port, timeout=SUBSCAN_TIMEOUT, exclude_locations=EXCLUDE_LOCATIONS):
    protocol = 'https' if port in ('443', '8443') else 'http'
    url = f"{protocol}://{host}:{port}"
    
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=False, verify=False)
        status_code = response.status_code
        server_header = response.headers.get('Server', 'N/A')

        if status_code == 302:
            location = response.headers.get('Location', '').strip()
            if location in exclude_locations:
                return None

        ip_address = socket.gethostbyname(host)
        return status_code, server_header, port, ip_address, host

    except (requests.RequestException, socket.gaierror, socket.timeout):
        return None

def perform_scan(hosts, ports, output_file, threads):
    clear_screen()
    print(f"[bold green]Scanning using HEAD method on port(s) {', '.join(ports)}...\n[/bold green]")

    headers = (f"[green]{'Code':<4}[/green] [cyan]{'Server':<15}[/cyan] [yellow]{'Port':<5}[/yellow] [magenta]{'IP Address':<15}[/magenta] [blue]{'Host'}[/blue]")  
    separator = (f"[green]{'----':<4}[/green] [cyan]{'------':<15}[/cyan] [yellow]{'----':<5}[/yellow] [magenta]{'---------':<15}[/magenta] [blue]{'----'}[/blue]")  
    
    if output_file:
        output_path = Path(output_file)
        if not output_path.exists():
            with open(output_file, 'a') as file:
                file.write(f"{'Code':<4} {'Server':<15} {'Port':<5} {'IP Address':<15} {'Host'}\n")
                file.write(f"{'----':<4} {'------':<15} {'----':<5} {'---------':<15} {'----'}\n")

    print(headers)
    print(separator)

    total_tasks = len(hosts) * len(ports)
    scanned, responded = 0, 0

    with tqdm(total=total_tasks, desc="Progress", unit="task", unit_scale=True) as pbar, \
         ThreadPoolExecutor(max_workers=threads) as executor:

        futures = {executor.submit(check_http_response, host, port): (host, port) for host in hosts for port in ports}

        for future in as_completed(futures):
            scanned += 1
            result = future.result()
            if result:
                responded += 1
                code, server, port, ip_address, host = result
                row = f"\033[32m{code:<4}\033[0m \033[36m{server:<15}\033[0m \033[33m{port:<5}\033[0m \033[35m{ip_address:<15}\033[0m \033[34m{host}\033[0m"
                pbar.write(row)
                if output_file:
                    with file_write_lock:
                        with open(output_file, 'a') as file:
                            file.write(f"{code:<4} {server:<15} {port:<5} {ip_address:<15} {host}\n")
            pbar.update(1)

    print(f"[bold green]\n Scan completed! {responded}/{scanned} hosts responded.[/bold green]")
    if output_file:
        print(f"[bold green] Results saved to {output_file}[/bold green]")

def main():
    selected_file = file_manager(Path('.'))
    hosts = read_file(selected_file)
    ports = get_input("Enter port(s)", "number", default="80")
    port_list = [port.strip() for port in ports.split(',') if port.strip().isdigit()]
    default_output = f"result_{selected_file.stem}.txt"
    output_file = get_input("Enter output filename", default=default_output, validate_input=False)

    perform_scan(hosts, port_list, output_file, 50)
