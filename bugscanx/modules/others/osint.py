import concurrent.futures

import requests
from requests.exceptions import RequestException

from rich.console import Console
from rich.table import Table

from bugscanx.utils import get_input

console = Console()

HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]

def check_http_method(url, method):
    try:
        response = requests.request(method, url, timeout=5)
        headers = {
            "Server": response.headers.get("Server", "N/A"),
            "Connection": response.headers.get("Connection", "N/A"),
            "Content-Type": response.headers.get("Content-Type", "N/A"),
            "Content-Length": response.headers.get("Content-Length", "N/A"),
        }
        return method, response.status_code, headers
    except RequestException as e:
        return method, None, str(e)

def check_http_methods(url):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(check_http_method, url, method) for method in HTTP_METHODS]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results

def osint_main():
    host = get_input("Enter the host (e.g., example.com)")
    protocol = get_input("Enter the protocol", "choice", choices=["http", "https"])
    url = f"{protocol}://{host}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        http_methods_future = executor.submit(check_http_methods, url)

    http_methods_results = http_methods_future.result()
    
    http_table = Table(title="HTTP Methods Information")

    http_table.add_column("HTTP Method", justify="center", style="cyan", no_wrap=True)
    http_table.add_column("Status Code", justify="center", style="magenta")
    http_table.add_column("Server", justify="left", style="green")
    http_table.add_column("Connection", justify="left", style="green")
    http_table.add_column("Content-Type", justify="left", style="green")
    http_table.add_column("Content-Length", justify="left", style="green")

    for method, status_code, headers in http_methods_results:
        if isinstance(headers, dict):
            http_table.add_row(method, str(status_code), headers["Server"], headers["Connection"], headers["Content-Type"], headers["Content-Length"])
        else:
            http_table.add_row(method, str(status_code), headers, "N/A", "N/A", "N/A")

    console.print(http_table)
