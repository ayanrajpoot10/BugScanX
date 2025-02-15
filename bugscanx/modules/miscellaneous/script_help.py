from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def show_help():

    help_text = """

## Features Overview

1. **HOST SCANNER PRO (Option 1)**
   - Perform host scans using a TXT file as input.
   - Customize scans with options like specific ports and methods (direct, SSL, proxy, and UDP).
   - In direct mode, support for various HTTP methods (e.g., GET, HEAD, PATCH).
   - Efficient multithreading for scanning multiple hosts simultaneously.

2. **SUB SCANNER (Option 2)**
   - Simplified host scanning for beginners, you can consider it as lite version of option 1.
   - Use an interactive file manager to select a TXT file and initiate scans effortlessly.

3. **CIDR SCANNER (Option 3)**
   - Scan IP ranges using CIDR blocks as input.
   - Provides similar functionality to Option 2, tailored for CIDR-based input.

4. **SUBFINDER (Option 4)**
   - Enumerate subdomains of a target domain from various sources.
   - Also support txt file input for mass enumration.
   - Ideal for expanding reconnaissance efforts.

5. **IP LOOKUP (Option 5)**
   - Perform reverse IP lookups to identify domains and subdomains hosted on a given IP.
   - Supports CIDR input for bulk analysis.

6. **TXT TOOLKIT (Option 6)**
   - A versatile toolkit for managing TXT files.
   - Includes options for splitting large files, merging multiple files, and more.

7. **OPEN PORT (Option 7)**
   - Check for open ports on a target host.
   - Identify active services and potential entry points.

8. **DNS RECORDS (Option 8)**
   - Retrieve DNS records for a domain (A, MX, CNAME, TXT, etc.).
   - Useful for analyzing domain configurations and detecting misconfigurations.

9. **OSINT (Option 9)**
   - Gather useful information on a target host.
   - Expand your reconnaissance capabilities.

10. **HELP MENU (Option 10)**
    - Access this help documentation at any time.

11. **UPDATER (Option 11)**
      - Update the BugScanX script to the latest version.
      - Stay current with new features and bug fixes.

12. **EXIT (Option 12)**
    - Exit the application gracefully.

## Usage Instructions

1. Launch the script in your terminal using: `bugscanx`.
2. Follow the interactive menu to choose a feature.
3. Provide the required inputs (e.g., file paths, domains, IPs) as prompted.
4. View results directly in the terminal for immediate insights.

    """
    console.print(
        Panel(
            Markdown(help_text),
            border_style="bold green",
            expand=True,
        )
    )

    console.print(
        Panel(
            Text("Thank you for choosing BugScanX!\nStay updated with our latest releases and features by visiting: https://t.me/BugScanX"),
            border_style="bold blue",
            expand=True,
        )
    )
