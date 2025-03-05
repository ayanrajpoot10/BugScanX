import os
import re
import ipaddress
from rich import print
from collections import defaultdict
from bugscanx.utils import get_input, get_confirm


def read_file_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except Exception as e:
        print(f"[red] Error reading file {file_path}: {e}[/red]")
        return []

def write_file_lines(file_path, lines):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except Exception as e:
        print(f"[red] Error writing to file {file_path}: {e}[/red]")

def split_txt_file():
    file_path = get_input("File to split", "file")
    parts = int(get_input("Number of parts", "number"))
    lines = read_file_lines(file_path)
    if not lines:
        return
    lines_per_file = len(lines) // parts
    file_base = os.path.splitext(file_path)[0]
    for i in range(parts):
        part_lines = lines[i * lines_per_file: (i + 1) * lines_per_file] if i < parts - 1 else lines[i * lines_per_file:]
        part_file = f"{file_base}_part_{i + 1}.txt"
        write_file_lines(part_file, part_lines)
        print(f"[green] Created file: {part_file}[/green]")

def merge_txt_files():
    directory = get_input("Directory path", default=os.getcwd())
    merge_all = get_confirm("Merge all txt files?")
    files_to_merge = []
    if not merge_all:
        filenames = get_input("Files to merge (comma-separated)")
        files_to_merge = [filename.strip() for filename in filenames.split(',') if filename.strip()]
    output_file = get_input("Output filename")
    try:
        with open(os.path.join(directory, output_file), 'w', encoding="utf-8") as outfile:
            for filename in files_to_merge:
                with open(os.path.join(directory, filename), 'r', encoding="utf-8") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")
        print(f"[green] Files merged into '{output_file}' in directory '{directory}'.[/green]")
    except Exception as e:
        print(f"[red] Error merging files: {e}[/red]")

def remove_duplicate_domains():
    file_path = get_input("File path", "file")
    lines = read_file_lines(file_path)
    if not lines:
        return
    domains = set(lines)
    write_file_lines(file_path, sorted(domains))
    print(f"[green] Duplicates removed from {file_path}[/green]")

def txt_cleaner():
    input_file = get_input("Input file", "file")
    domain_output_file = get_input("Domain output file")
    ip_output_file = get_input("IP output file")
    
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
    
    print(f"[green] Domains have been saved to '{domain_output_file}'.[/green]")
    print(f"[green] IP addresses have been saved to '{ip_output_file}'.[/green]")

def convert_subdomains_to_domains():
    file_path = get_input("Input file", "file")
    output_file = get_input("Output file")
    lines = read_file_lines(file_path)
    if not lines:
        return
    root_domains = set(subdomain.split('.')[-2] + '.' + subdomain.split('.')[-1] for subdomain in lines)
    write_file_lines(output_file, [f"{domain}\n" for domain in sorted(root_domains)])
    print(f"[green] Subdomains converted to root domains and saved to {output_file}[/green]")

def separate_domains_by_extension():
    file_path = get_input("Input file", "file")
    extensions_input = get_input("Extensions (comma-separated) or 'all'")
    extensions = extensions_input.lower().split(',')
    lines = read_file_lines(file_path)
    if not lines:
        return
    
    extensions_dict = defaultdict(list)
    for domain in lines:
        domain = domain.strip()
        extension = domain.split('.')[-1]
        extensions_dict[extension].append(domain)
    
    base_name = os.path.splitext(file_path)[0]
    if 'all' in extensions:
        for extension, domain_list in extensions_dict.items():
            ext_file = f"{base_name}_{extension}.txt"
            write_file_lines(ext_file, [f"{domain}\n" for domain in domain_list])
            print(f"[green] Domains with .{extension} saved to {ext_file}[/green]")
    else:
        for extension in extensions:
            extension = extension.strip()
            if extension in extensions_dict:
                ext_file = f"{base_name}_{extension}.txt"
                write_file_lines(ext_file, [f"{domain}\n" for domain in extensions_dict[extension]])
                print(f"[green] Domains with .{extension} saved to {ext_file}[/green]")
            else:
                print(f"[yellow] No domains found with .{extension} extension[/yellow]")

def filter_by_keywords():
    file_path = get_input("Input file", "file")
    keywords_input = get_input("Keywords (comma-separated)")
    keywords = keywords_input.lower().split(',')
    output_file = get_input("Output file")
    
    lines = read_file_lines(file_path)
    if not lines:
        return
    
    filtered_domains = []
    for domain in lines:
        domain = domain.strip()
        if any(keyword in domain.lower() for keyword in keywords):
            filtered_domains.append(domain)
    
    write_file_lines(output_file, [f"{domain}\n" for domain in filtered_domains])
    print(f"[green] Filtered domains saved to {output_file}[/green]")

def cidr_to_ip():
    cidr_input = get_input("CIDR range")
    output_file = get_input("Output file")
    
    try:
        network = ipaddress.ip_network(cidr_input.strip(), strict=False)
        ip_addresses = [str(ip) + '\n' for ip in network.hosts()]
        write_file_lines(output_file, ip_addresses)
        print(f"[green]{len(ip_addresses)} IP addresses have been saved to '{output_file}'[/green]")
    except ValueError as e:
        print(f"[red]Invalid CIDR range: {cidr_input} - {str(e)}[/red]")

def txt_toolkit_main():
    options = {
        "1": ("Split TXT File", split_txt_file, "bold cyan"),
        "2": ("Merge TXT files", merge_txt_files, "bold blue"),
        "3": ("Remove Duplicate", remove_duplicate_domains, "bold yellow"),
        "4": ("Subdomains to Domains", convert_subdomains_to_domains, "bold magenta"),
        "5": ("TXT Cleaner", txt_cleaner, "bold cyan"),
        "6": ("Filter domains by Extension", separate_domains_by_extension, "bold magenta"),
        "7": ("Filter domains by Keywords", filter_by_keywords, "bold yellow"),
        "8": ("Convert CIDR to IP", cidr_to_ip, "bold green"),
        "0": ("Back", lambda: None, "bold red")
    }
    
    while True:
        print("\n".join(f"[{color}] [{key}] {desc}" for key, (desc, _, color) in options.items()))
        
        choice = input("\n \033[36m[-]  Your Choice: \033[0m")
        
        if choice in options:
            options[choice][1]()
            if choice == '0':
                break