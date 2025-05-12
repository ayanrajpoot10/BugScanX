import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console
from bugscanx.utils.common import get_input

console = Console()

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888]

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return port if sock.connect_ex((ip, port)) == 0 else None
    except:
        return None

def main():
    target = get_input("Enter target")
    try:
        ip = socket.gethostbyname(target)
        console.print(f" Scanning target: {ip} ({target})", style="bold green")
    except socket.gaierror:
        console.print(" Error resolving IP for the provided hostname.", style="bold red")
        return

    scan_type = get_input("Select scan type", "choice", choices=["Common ports", "All ports (1-65535)"])
    ports = COMMON_PORTS if scan_type == "Common ports" else range(1, 65536)
    
    open_ports = []
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning ports", total=len(ports))
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]
            for future in as_completed(futures):
                if result := future.result():
                    open_ports.append(result)
                    console.print(f" Port {result} is open", style="bold green")
                progress.advance(task)

    console.print("\n Scan complete!", style="bold green")
    if open_ports:
        console.print(" Open ports:", style="bold cyan")
        console.print("\n".join(f"- Port {port}" for port in open_ports), style="bold cyan")
        
        with open(f"{target}_open_ports.txt", "w") as f:
            f.write("\n".join(f"Port {port} is open" for port in open_ports))
        console.print(f" Results saved to {target}_open_ports.txt", style="bold green")
    else:
        console.print(" No open ports found.", style="bold red")
