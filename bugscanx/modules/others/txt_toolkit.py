import os
import re
import socket
import ipaddress
from rich import print
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from bugscanx.utils import get_input, get_confirm

def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"[red] Error reading file {file_path}: {e}[/red]")
        return []

def write_file_lines(file_path, lines):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(f"{line}\n" for line in lines)
        print(f"[green] Successfully wrote to file[/green]")
        return True
    except Exception as e:
        print(f"[red] Error writing to file {file_path}: {e}[/red]")
        return False

def get_file_input():
    return get_input("File path", "file")

def split_txt_file():
    file_path = get_file_input()
    parts = int(get_input("Number of parts", "number"))
    lines = read_file_lines(file_path)
    
    if not lines:
        return
    
    lines_per_file = len(lines) // parts
    file_base = os.path.splitext(file_path)[0]
    
    for i in range(parts):
        start_idx = i * lines_per_file
        end_idx = None if i == parts - 1 else (i + 1) * lines_per_file
        part_lines = lines[start_idx:end_idx]
        part_file = f"{file_base}_part_{i + 1}.txt"
        write_file_lines(part_file, part_lines)

def merge_txt_files():
    directory = get_input("Directory path", default=os.getcwd())
    
    if get_confirm(" Merge all txt files?"):
        files_to_merge = [f for f in os.listdir(directory) if f.endswith('.txt')]
    else:
        filenames = get_input("Files to merge (comma-separated)")
        files_to_merge = [f.strip() for f in filenames.split(',') if f.strip()]
    
    if not files_to_merge:
        print("[red] No files found to merge[/red]")
        return
    
    output_file = get_input("Output filename")
    output_path = os.path.join(directory, output_file)
    
    try:
        with open(output_path, 'w', encoding="utf-8") as outfile:
            for filename in files_to_merge:
                file_path = os.path.join(directory, filename)
                outfile.write('\n'.join(read_file_lines(file_path)) + "\n")
        print(f"[green] Files merged into '{output_file}' in directory '{directory}'.[/green]")
    except Exception as e:
        print(f"[red] Error merging files: {e}[/red]")

def remove_duplicate_domains():
    file_path = get_file_input()
    lines = read_file_lines(file_path)
    
    if not lines:
        return
    
    unique_lines = sorted(set(lines))
    write_file_lines(file_path, unique_lines)
    print(f"[green] Removed {len(lines) - len(unique_lines)} duplicates from {file_path}[/green]")

def txt_cleaner():
    input_file = get_file_input()
    domain_output_file = get_input("Domain output file")
    ip_output_file = get_input("IP output file")
    
    content = read_file_lines(input_file)
    if not content:
        return
    
    domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b')
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    
    domains = set()
    ips = set()
    
    for line in content:
        domains.update(domain_pattern.findall(line))
        ips.update(ip_pattern.findall(line))
    
    write_file_lines(domain_output_file, sorted(domains))
    write_file_lines(ip_output_file, sorted(ips))

def convert_subdomains_to_domains():
    file_path = get_file_input()
    output_file = get_input("Output file")
    
    subdomains = read_file_lines(file_path)
    if not subdomains:
        return

    root_domains = set()
    for subdomain in subdomains:
        parts = subdomain.split('.')
        if len(parts) >= 2:
            root_domains.add('.'.join(parts[-2:]))
    
    write_file_lines(output_file, sorted(root_domains))

def separate_domains_by_extension():
    file_path = get_file_input()
    extensions_input = get_input("Extensions (comma-separated) or 'all'")
    
    domains = read_file_lines(file_path)
    if not domains:
        return
    
    extensions_dict = defaultdict(list)
    for domain in domains:
        ext = domain.split('.')[-1].lower()
        extensions_dict[ext].append(domain)
    
    base_name = os.path.splitext(file_path)[0]
    target_extensions = [ext.strip() for ext in extensions_input.lower().split(',')] if extensions_input.lower() != 'all' else list(extensions_dict.keys())
    
    for ext in target_extensions:
        if ext in extensions_dict:
            ext_file = f"{base_name}_{ext}.txt"
            write_file_lines(ext_file, sorted(extensions_dict[ext]))
        else:
            print(f"[yellow] No domains found with .{ext} extension[/yellow]")

def filter_by_keywords():
    file_path = get_file_input()
    keywords = [k.strip().lower() for k in get_input("Keywords (comma-separated)").split(',')]
    output_file = get_input("Output file")
    
    lines = read_file_lines(file_path)
    if not lines:
        return
    
    filtered_domains = [domain for domain in lines if any(keyword in domain.lower() for keyword in keywords)]
    write_file_lines(output_file, filtered_domains)

def cidr_to_ip():
    cidr_input = get_input("CIDR range")
    output_file = get_input("Output file")
    
    try:
        network = ipaddress.ip_network(cidr_input.strip(), strict=False)
        ip_addresses = [str(ip) for ip in network.hosts()]
        write_file_lines(output_file, ip_addresses)
        print(f"[green]{len(ip_addresses)} IP addresses saved to '{output_file}'[/green]")
    except ValueError as e:
        print(f"[red]Invalid CIDR range: {cidr_input} - {str(e)}[/red]")

def resolve_domain(domain):
    try:
        ip = socket.gethostbyname_ex(domain.strip())[2][0]
        return domain, ip
    except (socket.gaierror, socket.timeout):
        return domain, None

def domains_to_ip():
    file_path = get_file_input()
    output_file = get_input("Output file")
    
    domains = read_file_lines(file_path)
    if not domains:
        return
        
    ip_addresses = set()
    total_domains = len(domains)
    resolved_count = 0

    socket.setdefaulttimeout(1)
    
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        transient=True
    ) as progress:
        task = progress.add_task("[yellow]Resolving", total=total_domains)
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_to_domain = {executor.submit(resolve_domain, domain): domain for domain in domains}
            for future in as_completed(future_to_domain):
                domain, ip = future.result()
                if ip:
                    ip_addresses.add(ip)
                progress.update(task, advance=1)
                resolved_count += 1
    
    if ip_addresses:
        write_file_lines(output_file, sorted(ip_addresses))
        print(f"[green] Successfully resolved domains to IP addresses[/green]")
    else:
        print("[red] No domains could be resolved[/red]")

def txt_toolkit_main():
    options = {
        "1": ("Split File", split_txt_file, "bold cyan"),
        "2": ("Merge Files", merge_txt_files, "bold blue"),
        "3": ("Remove Duplicate", remove_duplicate_domains, "bold yellow"),
        "4": ("Subdomains to Domains", convert_subdomains_to_domains, "bold magenta"),
        "5": ("TXT Cleaner", txt_cleaner, "bold cyan"),
        "6": ("Filter by Extension", separate_domains_by_extension, "bold magenta"),
        "7": ("Filter by Keywords", filter_by_keywords, "bold yellow"),
        "8": ("CIDR to IP", cidr_to_ip, "bold green"),
        "9": ("Domains to IP", domains_to_ip, "bold blue"),
        "0": ("Back", lambda: None, "bold red")
    }
    
    print("\n".join(f"[{color}] [{key}] {desc}" for key, (desc, _, color) in options.items()))
    choice = input("\n \033[36m[-]  Your Choice: \033[0m")
    
    if choice in options:
        options[choice][1]()
        if choice == '0':
            return
