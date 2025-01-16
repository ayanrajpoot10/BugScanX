import socket
import requests
from tqdm import tqdm
from pathlib import Path
from colorama import Fore
from threading import Lock
from bugscanx.modules.scanners import file_manager
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.modules import clear_screen, get_input, not_empty_validator, digit_validator, SUBSCAN_TIMEOUT, EXCLUDE_LOCATIONS

FILE_WRITE_LOCK = Lock()
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except (FileNotFoundError, IOError) as e:
        print(Fore.RED + f"Error reading file: {e}")
        return []

def get_scan_inputs():
    selected_file = file_manager(Path('.'), max_up_levels=3)
    hosts = read_file(selected_file)
    default_output = f"results_{selected_file.stem}.txt"
    output_file = get_input(" Enter output file name", default=default_output, validator=not_empty_validator)
    ports = get_input(" Enter ports (comma-separated)", default="80", validator=digit_validator)
    port_list = [port.strip() for port in ports.split(',') if port.strip().isdigit()]
    return hosts, port_list, output_file, 50

def check_http_response(host, port, timeout=SUBSCAN_TIMEOUT, exclude_locations=EXCLUDE_LOCATIONS):
    protocol = 'https' if port in ('443', '8443') else 'http'
    url = f"{protocol}://{host}:{port}"
    
    exclude_set = set(exclude_locations) if exclude_locations else set()
    
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        location = response.headers.get('Location', '')
        if exclude_set and any(exclude in location for exclude in exclude_set):
            return None

        ip_address = socket.gethostbyname(host)
        return response.status_code, response.headers.get('Server', 'N/A'), port, ip_address, host
    except (requests.RequestException, socket.gaierror, socket.timeout):
        return None

def perform_scan(hosts, ports, output_file, threads):
    clear_screen()
    print(Fore.GREEN + f"Scanning using HTTP method: HEAD on ports {', '.join(ports)}...\n")

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

        futures = {executor.submit(check_http_response, host, port): (host, port) for host in hosts for port in ports}

        for future in as_completed(futures):
            scanned += 1
            result = future.result()
            if result:
                responded += 1
                code, server, port, ip_address, host = result
                row = f"{Fore.GREEN}{code:<4}{Fore.RESET} {Fore.CYAN}{server:<15}{Fore.RESET} {Fore.YELLOW}{port:<5}{Fore.RESET} {Fore.MAGENTA}{ip_address:<15}{Fore.RESET} {Fore.LIGHTBLUE_EX}{host}{Fore.RESET}"
                pbar.write(row)
                with FILE_WRITE_LOCK:
                    with open(output_file, 'a') as file:
                        file.write(f"{code:<4} {server:<15} {port:<5} {ip_address:<15} {host}\n")
            pbar.update(1)

    print(Fore.GREEN + f"\n\nScan completed! {responded}/{scanned} hosts responded.")
    print(f"Results saved to {output_file}" + Fore.RESET)
