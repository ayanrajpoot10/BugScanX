import os
import re
import socket
import threading
from rich.console import Console
from collections import defaultdict
from bugscanx.modules import get_input
from concurrent.futures import ThreadPoolExecutor, as_completed

file_write_lock = threading.Lock()
console = Console()

def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except Exception as e:
        console.print(f"[red] Error reading file {file_path}: {e}[/red]")
        return []

def write_file_lines(file_path, lines):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except Exception as e:
        console.print(f"[red] Error writing to file {file_path}: {e}[/red]")

def split_txt_file(file_path, parts):
    lines = read_file_lines(file_path)
    if not lines:
        return

    lines_per_file = len(lines) // parts
    file_base = os.path.splitext(file_path)[0]
    for i in range(parts):
        part_lines = lines[i * lines_per_file: (i + 1) * lines_per_file] if i < parts - 1 else lines[i * lines_per_file:]
        part_file = f"{file_base}_part_{i + 1}.txt"
        write_file_lines(part_file, part_lines)
        console.print(f"[green] Created file: {part_file}[/green]")

def merge_txt_files(directory, merge_all, files_to_merge, output_file):
    if not os.path.isdir(directory):
        console.print("[yellow]The provided directory does not exist. Please check the path and try again.[/yellow]")
        return
    
    if merge_all == 'yes':
        files_to_merge = [f for f in os.listdir(directory) if f.endswith('.txt')]
    else:
        files_to_merge = [f for f in files_to_merge if os.path.isfile(os.path.join(directory, f))]
        
        if not files_to_merge:
            console.print("[yellow]No valid files were selected. Please check the filenames and try again.[/yellow]")
            return
    
    try:
        with open(os.path.join(directory, output_file), 'w', encoding="utf-8") as outfile:
            for filename in files_to_merge:
                with open(os.path.join(directory, filename), 'r', encoding="utf-8") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")
        console.print(f"[green] Files have been successfully merged into '{output_file}' in the directory '{directory}'.[/green]")
    except Exception as e:
        console.print(f"[red] Error merging files: {e}[/red]")

def remove_duplicate_domains(file_path):
    lines = read_file_lines(file_path)
    if not lines:
        return

    domains = set(lines)
    write_file_lines(file_path, sorted(domains))
    console.print(f"[green] Duplicates removed from {file_path}[/green]")

def txt_cleaner(input_file, domain_output_file, ip_output_file):
    file_contents = read_file_lines(input_file)
    if not file_contents:
        return

    domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b')
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    
    domains = set()
    ips = set()
    
    for line in file_contents:
        domains.update(domain_pattern.findall(line))
        ips.update(ip_pattern.findall(line))
    
    write_file_lines(domain_output_file, [f"{domain}\n" for domain in sorted(domains)])
    write_file_lines(ip_output_file, [f"{ip}\n" for ip in sorted(ips)])
    
    console.print(f"[green] Domains have been saved to '{domain_output_file}', and IP addresses have been saved to '{ip_output_file}'.[/green]")

def convert_subdomains_to_domains(file_path):
    lines = read_file_lines(file_path)
    if not lines:
        return

    root_domains = set(subdomain.split('.')[-2] + '.' + subdomain.split('.')[-1] for subdomain in lines)
    output_file = f"{os.path.splitext(file_path)[0]}_root_domains.txt"
    write_file_lines(output_file, [f"{domain}\n" for domain in sorted(root_domains)])
    console.print(f"[green] Subdomains converted to root domains and saved to {output_file}[/green]")

def separate_domains_by_extension(file_path, extensions):
    lines = read_file_lines(file_path)
    if not lines:
        return

    extensions_dict = defaultdict(list)
    for domain in lines:
        domain = domain.strip()  # Strip newline characters
        extension = domain.split('.')[-1]
        extensions_dict[extension].append(domain)

    base_name = os.path.splitext(file_path)[0]
    if 'all' in extensions:
        for extension, domain_list in extensions_dict.items():
            ext_file = f"{base_name}_{extension}.txt"
            write_file_lines(ext_file, [f"{domain}\n" for domain in domain_list])
            console.print(f"[green] Domains with .{extension} saved to {ext_file}[/green]")
    else:
        for extension in extensions:
            if extension in extensions_dict:
                ext_file = f"{base_name}_{extension}.txt"
                write_file_lines(ext_file, [f"{domain}\n" for domain in extensions_dict[extension]])
                console.print(f"[green] Domains with .{extension} saved to {ext_file}[/green]")
            else:
                console.print(f"[yellow] No domains found with .{extension} extension[/yellow]")

def resolve_domain_to_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return f"{domain} -> {ip}"
    except socket.gaierror:
        return f"{domain} -> Resolution failed"

def domains_to_ip(file_path):
    lines = read_file_lines(file_path)
    if not lines:
        return

    output_file = f"{os.path.splitext(file_path)[0]}_with_ips.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_domain = {executor.submit(resolve_domain_to_ip, domain): domain for domain in lines}
                for future in as_completed(future_to_domain):
                    file.write(future.result() + "\n")
        console.print(f"[green] Domain-to-IP mappings saved to {output_file}[/green]")
    except Exception as e:
        console.print(f"[red] Error resolving domains to IPs: {e}[/red]")

def txt_toolkit_main_menu():
    while True:
        console.print("[yellow]\n [1] Split TXT File[/yellow]")
        console.print("[yellow] [2] Merge Txt files[/yellow]")
        console.print("[yellow] [3] Txt cleaner (extract domains, subdomains & IP)[/yellow]")
        console.print("[yellow] [4] Separate Domains by Extensions (like .com, .in)[/yellow]")
        console.print("[yellow] [5] Convert Domains to IP Addresses[/yellow]")
        console.print("[yellow] [6] Remove Duplicate Domains[/yellow]")
        console.print("[yellow] [7] Convert Subdomains to Root domains[/yellow]")
        console.print("[red] [0] Exit[/red]")

        choice = get_input("\n [-] Enter your choice")
        
        if choice == "1":
            file_path = get_input(" Enter the file path")
            parts = int(get_input(" Enter number of parts to split the file into"))
            split_txt_file(file_path, parts)

        elif choice == "2":
            directory = get_input(" Input the directory path where your text files are located (or press Enter to use the current directory)", default=os.getcwd())
            merge_all = get_input(prompt=" Do you want to merge all .txt files in the directory? (yes/no)", default="yes")
            files_to_merge = []
            if merge_all == 'no':
                filenames = get_input(" Enter the filenames to merge, separated by commas")
                files_to_merge = [filename.strip() for filename in filenames.split(',') if filename.strip()]
            output_file = get_input(" Enter the name for the merged output file")
            merge_txt_files(directory, merge_all, files_to_merge, output_file)

        elif choice == "3":
            input_file = get_input(" Enter the name of the input file containing the data")
            domain_output_file = get_input(" Enter the name for the output file for domains")
            ip_output_file = get_input("Enter the name for the output file for IP addresses")
            txt_cleaner(input_file, domain_output_file, ip_output_file)

        elif choice == "4":
            file_path = get_input(" Enter the file path")
            extensions_input = get_input(" Enter the extensions to save (comma-separated, or 'all' for all extensions)")
            extensions = [ext.strip() for ext in extensions_input.split(',')]
            separate_domains_by_extension(file_path, extensions)

        elif choice == "5":
            file_path = get_input(" Enter the file path")
            domains_to_ip(file_path)

        elif choice == "6":
            file_path = get_input(" Enter the file path")
            remove_duplicate_domains(file_path)

        elif choice == "7":
            file_path = get_input(" Enter the file path")
            convert_subdomains_to_domains(file_path)

        elif choice == "0":
            console.print("[red] Exiting TXT Toolkit![/red]")
            break

        else:
            console.print("[red] Invalid choice. Please try again.[/red]")
