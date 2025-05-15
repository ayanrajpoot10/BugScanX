import os
import re
import socket
import ipaddress
from rich import print
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from bugscanx.utils.common import get_input, get_confirm

def read_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"[red] Error reading file {file_path}: {e}[/red]")
        return []

def write_lines(file_path, lines):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(f"{line}\n" for line in lines)
        return True
    except Exception as e:
        print(f"[red] Error writing to file {file_path}: {e}[/red]")
        return False

def split_file():
    file_path = get_input("Enter filename", "file")
    parts = int(get_input("Number of parts", "number"))
    lines = read_lines(file_path)
    if not lines:
        return
    
    lines_per_file = len(lines) // parts
    file_base = os.path.splitext(file_path)[0]
    created_files = []
    
    for i in range(parts):
        start_idx = i * lines_per_file
        end_idx = None if i == parts - 1 else (i + 1) * lines_per_file
        part_file = f"{file_base}_part_{i + 1}.txt"
        
        if write_lines(part_file, lines[start_idx:end_idx]):
            created_files.append((part_file, len(lines[start_idx:end_idx])))
    
    if created_files:
        print(f"[green] Split '{os.path.basename(file_path)}' into {len(created_files)} parts:[/green]")
        for file_path, line_count in created_files:
            print(f"[green] - {os.path.basename(file_path)}: {line_count} lines[/green]")

def merge_files():
    directory = get_input("Enter directory path", default=os.getcwd())
    
    if get_confirm(" Merge all txt files?"):
        files_to_merge = [f for f in os.listdir(directory) if f.endswith('.txt')]
    else:
        filenames = get_input("Files to merge (comma-separated)")
        files_to_merge = [f.strip() for f in filenames.split(',') if f.strip()]
    
    if not files_to_merge:
        print("[red] No files found to merge[/red]")
        return
    
    output_file = get_input("Enter output filename")
    output_path = os.path.join(directory, output_file)
    lines = []
    for filename in files_to_merge:
        file_path = os.path.join(directory, filename)
        lines.extend(read_lines(file_path))
    
    if write_lines(output_path, lines):
        print(f"[green] Successfully merged {len(files_to_merge)} files into '{output_file}'[/green]")
        print(f"[green] - Total lines: {len(lines)}[/green]")
        print(f"[green] - Output location: {directory}[/green]")

def clean_file():
    input_file = get_input("Enter filename", "file")
    domain_output_file = get_input("Enter domains output filename")
    ip_output_file = get_input("Enter IP output filename")
    
    content = read_lines(input_file)
    if not content:
        return
    
    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b'
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    
    domains = sorted(set(re.findall(domain_pattern, '\n'.join(content))))
    ips = sorted(set(re.findall(ip_pattern, '\n'.join(content))))
    
    domains_success = write_lines(domain_output_file, domains)
    ips_success = write_lines(ip_output_file, ips)
    
    if domains_success or ips_success:
        print(f"[green] TXT Cleaner results for '{os.path.basename(input_file)}':[/green]")
        if domains_success:
            print(f"[green] - Extracted {len(domains)} unique domains to '{os.path.basename(domain_output_file)}'[/green]")
        if ips_success:
            print(f"[green] - Extracted {len(ips)} unique IP addresses to '{os.path.basename(ip_output_file)}'[/green]")

def remove_duplicates():
    file_path = get_input("Enter filename", "file")
    lines = read_lines(file_path)
    if not lines:
        return
    
    unique_lines = sorted(set(lines))
    duplicates_removed = len(lines) - len(unique_lines)
    
    if write_lines(file_path, unique_lines):
        print(f"[green] Successfully removed duplicates from '{os.path.basename(file_path)}':[/green]")
        print(f"[green] - Original count: {len(lines)} lines[/green]")
        print(f"[green] - Unique count: {len(unique_lines)} lines[/green]")
        print(f"[green] - Duplicates removed: {duplicates_removed} lines[/green]")

def filter_by_tlds():
    file_path = get_input("Enter filename", "file")
    tlds_input = get_input("Enter TLDs ", instruction="(e.g. com, org)")
    
    domains = read_lines(file_path)
    if not domains:
        return
    
    tld_dict = defaultdict(list)
    for domain in domains:
        parts = domain.split('.')
        if len(parts) > 1:
            tld = parts[-1].lower()
            tld_dict[tld].append(domain)
    
    base_name = os.path.splitext(file_path)[0]
    target_tlds = [tld.strip().lstrip('.').lower() for tld in tlds_input.split(',')] if tlds_input.lower() != 'all' else list(tld_dict.keys())
    
    success_count = 0
    print(f"[green]Filtering domains by TLDs from '{os.path.basename(file_path)}':[/green]")
    
    for tld in target_tlds:
        if (tld in tld_dict):
            tld_file = f"{base_name}_{tld}.txt"
            if write_lines(tld_file, sorted(tld_dict[tld])):
                success_count += 1
                print(f"[green]- Created '{os.path.basename(tld_file)}' with {len(tld_dict[tld])} domains[/green]")
        else:
            print(f"[yellow]- No domains found with .{tld} TLD[/yellow]")

def filter_by_keywords():
    file_path = get_input("Enter filename", "file")
    keywords = [k.strip().lower() for k in get_input("Enter keyword(s)").split(',')]
    output_file = get_input("Enter output filename")
    
    lines = read_lines(file_path)
    if not lines:
        return
    
    filtered_lines = [line for line in lines if any(k in line.lower() for k in keywords)]
    
    if write_lines(output_file, filtered_lines):
        print(f"[green] Successfully filtered content by keywords:[/green]")
        print(f"[green] - Input lines: {len(lines)}[/green]")
        print(f"[green] - Matched lines: {len(filtered_lines)}[/green]")
        print(f"[green] - Keywords used: {', '.join(keywords)}[/green]")
        print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")

def cidr_to_ip():
    cidr_input = get_input("Enter CIDR range")
    output_file = get_input("Enter output filename")
    
    try:
        network = ipaddress.ip_network(cidr_input.strip(), strict=False)
        ip_addresses = [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"[red] Invalid CIDR range: {cidr_input} - {str(e)}[/red]")
        return
    
    if ip_addresses and write_lines(output_file, ip_addresses):
        print(f"[green] Successfully converted CIDR to IP addresses:[/green]")
        print(f"[green] - CIDR range: {cidr_input}[/green]")
        print(f"[green] - Total IPs: {len(ip_addresses)}[/green]")
        print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")

def domains_to_ip():
    file_path = get_input("Enter filename", "file")
    output_file = get_input("Enter output filename")
    
    domains = read_lines(file_path)
    if not domains:
        return

    ip_addresses = set()
    resolved_count = failed_count = 0
    socket.setdefaulttimeout(1)
    
    with Progress(SpinnerColumn(), *Progress.get_default_columns(), TimeElapsedColumn()) as progress:
        task = progress.add_task("[yellow]Resolving", total=len(domains))
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            def resolve_domain(domain):
                try:
                    ip = socket.gethostbyname_ex(domain.strip())[2][0]
                    return domain, ip
                except (socket.gaierror, socket.timeout):
                    return domain, None

            futures = [executor.submit(resolve_domain, domain) for domain in domains]
            for future in as_completed(futures):
                domain, ip = future.result()
                if ip:
                    ip_addresses.add(ip)
                    resolved_count += 1
                else:
                    failed_count += 1
                progress.update(task, advance=1)
    
    if ip_addresses and write_lines(output_file, sorted(ip_addresses)):
        print(f"[green] Successfully resolved domains to IP addresses:[/green]")
        print(f"[green] - Input domains: {len(domains)}[/green]")
        print(f"[green] - Successfully resolved: {resolved_count}[/green]")
        print(f"[green] - Failed to resolve: {failed_count}[/green]")
        print(f"[green] - Unique IP addresses: {len(ip_addresses)}[/green]")
        print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")
    else:
        print("[red] No domains could be resolved or there was an error writing to the output file[/red]")

def main():
    options = {
        "1": ("SPLIT FILE", split_file, "bold cyan"),
        "2": ("MERGE FILES", merge_files, "bold blue"),
        "3": ("CLEAN FILE", clean_file, "bold cyan"),
        "4": ("DEDUPLICATE", remove_duplicates, "bold yellow"),
        "5": ("FILTER BY TLD", filter_by_tlds, "bold magenta"),
        "6": ("FILTER BY KEYWORD", filter_by_keywords, "bold yellow"),
        "7": ("CIDR TO IP", cidr_to_ip, "bold green"),
        "8": ("DOMAIN TO IP", domains_to_ip, "bold blue"),
        "0": ("BACK", lambda: None, "bold red")
    }
    
    while True:
        print("\n".join(f"[{color}] [{key}] {desc}" for key, (desc, _, color) in options.items()))
        choice = input("\n \033[36m[-]  Your Choice: \033[0m").strip()

        if choice == '0':
            raise KeyboardInterrupt
        
        if choice not in options:
            from bugscanx import text_ascii
            text_ascii("FILE TOOLKIT")
            continue
            
        if choice in options:
            options[choice][1]()
            break
