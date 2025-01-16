import requests
import ipaddress
from tqdm import tqdm
from pathlib import Path
from colorama import Fore
from threading import Lock
from bugscanx.modules import *
from rich.console import Console
from bugscanx.modules.scanners import file_manager
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.modules.utils.utils import SUBSCAN_TIMEOUT, EXCLUDE_LOCATIONS

file_write_lock = Lock()
console = Console()

def get_cidrs_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            cidr_list = [line.strip() for line in file if line.strip()]
            ip_list = []
            for cidr in cidr_list:
                try:
                    network = ipaddress.ip_network(cidr, strict=False)
                    ip_list.extend([str(ip) for ip in network.hosts()])
                except ValueError as e:
                    console.print(f"[red] Invalid CIDR '{cidr}': {e}[/red]")
            return ip_list
    except Exception as e:
        console.print(f"[red] Error reading file: {e}[/red]")
        return []

def get_cidrs_from_input():
    cidr_input = get_input(prompt=" Enter CIDR blocks (comma-separated)", validator=cidr_validator)
    cidr_list = [cidr.strip() for cidr in cidr_input.split(',')]
    ip_list = []
    for cidr in cidr_list:
        network = ipaddress.ip_network(cidr, strict=False)
        ip_list.extend([str(ip) for ip in network.hosts()])
    return ip_list

def get_scan_inputs():
    while True:
        input_choice = get_input(prompt="\n input 1 for manual CIDR input or 2 for file input", validator=choice_validator).lower()
        
        if input_choice == '2':
            selected_file = file_manager(Path.cwd(), max_up_levels=3)
            if selected_file:
                hosts = get_cidrs_from_file(selected_file)
                if hosts:
                    break
                else:
                    console.print("[red] No valid IPs found in the CIDR file. Please try again.[/red]")
        elif input_choice == '1':
            hosts = get_cidrs_from_input()
            if hosts:
                break

    ports_input = get_input(prompt=" Enter port list", default="80", validator=digit_validator)
    ports = ports_input.split(',') if ports_input else ["80"]

    output_file = get_input(" Enter output file name", default="scan_results.txt")

    threads = int(get_input(" Enter number of threads", default="50", validator=digit_validator))

    http_method = create_prompt("list", " Select the http method", "selection", choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])

    return hosts, ports, output_file, threads, http_method

def check_http_response(host, port, method):
    protocol = "https" if port in ['443', '8443'] else "http"
    url = f"{protocol}://{host}:{port}"
    try:
        response = requests.request(method, url, timeout=SUBSCAN_TIMEOUT, allow_redirects=True)
        location = response.headers.get('Location', '')
        if any(exclude in location for exclude in EXCLUDE_LOCATIONS):
            return None
        server_header = response.headers.get('Server', 'N/A')
        return response.status_code, server_header, port, host
    except requests.exceptions.RequestException:
        return None

def perform_scan(hosts, ports, output_file, threads, method):
    clear_screen()
    print(Fore.GREEN + f" Scanning using HTTP method: {method}...")

    headers = f"{Fore.GREEN}{'Code':<4}{Fore.RESET} {Fore.CYAN}{'Server':<15}{Fore.RESET} {Fore.YELLOW}{'Port':<5}{Fore.RESET} {Fore.MAGENTA}{'IP Address':<15}{Fore.RESET} {Fore.LIGHTBLUE_EX}{'Host'}{Fore.RESET}"
    separator = f"{Fore.GREEN}{'----':<4}{Fore.RESET} {Fore.CYAN}{'------':<15}{Fore.RESET} {Fore.YELLOW}{'----':<5}{Fore.RESET} {Fore.MAGENTA}{'---------':<15}{Fore.RESET} {Fore.LIGHTBLUE_EX}{'----'}{Fore.RESET}"
    
    with open(output_file, 'w') as file:
        file.write(f"{'Code':<4} {'Server':<15} {'Port':<5} {'IP Address':<15} {'Host'}\n")
        file.write(f"{'----':<4} {'------':<15} {'----':<5} {'---------':<15} {'----'}\n")

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
                code, server, port, ip_address, host = result
                row = f"{Fore.GREEN}{code:<4}{Fore.RESET} {Fore.CYAN}{server:<15}{Fore.RESET} {Fore.YELLOW}{port:<5}{Fore.RESET} {Fore.MAGENTA}{ip_address:<15}{Fore.RESET} {Fore.LIGHTBLUE_EX}{host}{Fore.RESET}"
                pbar.write(row)
                with file_write_lock:
                    with open(output_file, 'a') as file:
                        file.write(f"{code:<4} {server:<15} {port:<5} {ip_address:<15} {host}\n")
            pbar.update(1)

    print(f"\n\n{Fore.GREEN} Scan completed! {responded}/{scanned} hosts responded.")
    print(f" Results saved to {output_file}.{Fore.RESET}")
