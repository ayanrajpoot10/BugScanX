import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

from bugscanx.utils.common import get_input

console = Console()

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143,
    443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080,
    8443, 8888
]


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
    except socket.gaierror:
        console.print(
            "\n[bold red] Failed to resolve hostname",
            "\n[bold red] Please check your target and try again.",
        )
        return

    scan_type = get_input(
        "Select scan type",
        "choice",
        choices=["Common ports", "All ports (1-65535)"]
    )
    ports = COMMON_PORTS if scan_type == "Common ports" else range(1, 65535)
    
    console.print(
        f"\n[bold green] Target Info:[/]\n"
        f" • Host: {target}\n"
        f" • IP: {ip}\n"
    )
    console.print(f"[bold blue] Starting scan...[/]\n")
    
    open_ports = []
    with Progress(
        TextColumn("[bold blue]│[/] {task.description}"),
        BarColumn(complete_style="green"),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(" Scanning ports", total=len(ports))
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]
            for future in as_completed(futures):
                if result := future.result():
                    open_ports.append(result)
                    progress.console.print(f" [green]✓[/] Port {result} is open")
                progress.advance(task)

    open_ports = sorted(open_ports)
    
    console.print("\n[bold green] Scan Results:[/]\n")
    if open_ports:
        console.print("[cyan] Open Ports:[/]\n")
        for port in open_ports:
            console.print(f" • Port {port}")
        
        with open(f"{target}_open_ports.txt", "w") as f:
            f.write("\n".join(f"Port {port} is open" for port in open_ports))
        console.print(f"\n[dim] Results saved to {target}_open_ports.txt[/]\n")
    else:
        console.print("\n[yellow] No open ports found.[/]\n")
