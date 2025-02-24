import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.utils import get_input
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

file_write_lock = threading.Lock()

console = Console()

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723,
    3306, 3389, 5900, 8080, 8443, 8888
]

def check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        return port if result == 0 else None

def open_port_checker():
    target = get_input("\n Enter the IP address or hostname to scan")

    try:
        ip = socket.gethostbyname(target)
        console.print(f" Scanning target: {ip} ({target})", style="bold green")
    except socket.gaierror:
        console.print(" Error resolving IP for the provided hostname.", style="bold red")
        return

    choice = get_input("\n Select scan type:\n"
                       " 1. Scan common ports\n"
                       " 2. Scan all ports (1-65535)\n"
                       " Enter your choice (1 or 2)")
    if choice == "1":
        ports = COMMON_PORTS
        console.print(" Starting scan on common ports...", style="bold green")
    elif choice == "2":
        ports = range(1, 65536)
        console.print(" Starting scan on all ports (this may take time)...", style="bold green")
    else:
        console.print(" Invalid choice. Exiting.", style="bold red")
        return

    open_ports = []
    max_threads = 100

    total_ports = len(ports)
    console.print(f" Scanning {total_ports} ports...", style="bold yellow")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_port, ip, port): port for port in ports}
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning ports...", total=total_ports)
            for i, future in enumerate(as_completed(futures), start=1):
                port = futures[future]
                try:
                    result = future.result()
                    if result is not None:
                        open_ports.append(result)
                        console.print(f" Port {result} is open", style="bold green")
                except Exception as e:
                    console.print(f" Error scanning port {port}: {e}", style="bold red")

                progress.update(task, advance=1)

    console.print(" Scan complete!", style="bold green")
    if open_ports:
        console.print(" Open ports:", style="bold cyan")
        for port in open_ports:
            console.print(f"- Port {port}", style="bold cyan")
    else:
        console.print(" No open ports found.", style="bold red")

    output_file = f"{target}_open_ports.txt"
    with open(output_file, "w") as file:
        for port in open_ports:
            file.write(f"Port {port} is open\n")
    console.print(f" Results saved to {output_file}", style="bold green")

