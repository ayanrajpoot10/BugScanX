import os
import re
import socket
import ipaddress
from rich import print
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from bugscanx.utils.common import get_input, get_confirm

class FileHandler:
    @staticmethod
    def read_lines(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return [line.strip() for line in file.readlines()]
        except Exception as e:
            print(f"[red] Error reading file {file_path}: {e}[/red]")
            return []

    @staticmethod
    def write_lines(file_path, lines):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(f"{line}\n" for line in lines)
            return True
        except Exception as e:
            print(f"[red] Error writing to file {file_path}: {e}[/red]")
            return False

    @staticmethod
    def split_file(file_path, parts):
        lines = FileHandler.read_lines(file_path)
        if not lines:
            return []
        
        lines_per_file = len(lines) // parts
        file_base = os.path.splitext(file_path)[0]
        created_files = []
        
        for i in range(parts):
            start_idx = i * lines_per_file
            end_idx = None if i == parts - 1 else (i + 1) * lines_per_file
            part_file = f"{file_base}_part_{i + 1}.txt"
            
            if FileHandler.write_lines(part_file, lines[start_idx:end_idx]):
                created_files.append((part_file, len(lines[start_idx:end_idx])))
        
        return created_files

    @staticmethod
    def merge_files(directory, files_to_merge, output_file):
        output_path = os.path.join(directory, output_file)
        total_lines = 0
        
        try:
            with open(output_path, 'w', encoding="utf-8") as outfile:
                for filename in files_to_merge:
                    file_path = os.path.join(directory, filename)
                    lines = FileHandler.read_lines(file_path)
                    outfile.write('\n'.join(lines) + "\n")
                    total_lines += len(lines)
            return total_lines
        except Exception as e:
            print(f"[red] Error merging files: {e}[/red]")
            return 0

class DomainProcessor:
    @staticmethod
    def extract_domains_and_ips(content):
        domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b')
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        
        domains = set()
        ips = set()
        
        for line in content:
            domains.update(domain_pattern.findall(line))
            ips.update(ip_pattern.findall(line))
        
        return sorted(domains), sorted(ips)

    @staticmethod
    def get_root_domains(subdomains):
        root_domains = set()
        for subdomain in subdomains:
            parts = subdomain.split('.')
            if len(parts) >= 2:
                root_domains.add('.'.join(parts[-2:]))
        return sorted(root_domains)

    @staticmethod
    def separate_by_extension(domains):
        extensions_dict = defaultdict(list)
        for domain in domains:
            ext = domain.split('.')[-1].lower()
            extensions_dict[ext].append(domain)
        return extensions_dict

    @staticmethod
    def filter_by_keywords(domains, keywords):
        return [domain for domain in domains if any(keyword in domain.lower() for keyword in keywords)]

class IPProcessor:
    @staticmethod
    def resolve_domain(domain):
        try:
            ip = socket.gethostbyname_ex(domain.strip())[2][0]
            return domain, ip
        except (socket.gaierror, socket.timeout):
            return domain, None

    @staticmethod
    def convert_cidr_to_ips(cidr):
        try:
            network = ipaddress.ip_network(cidr.strip(), strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            print(f"[red] Invalid CIDR range: {cidr} - {str(e)}[/red]")
            return []

    @staticmethod
    def resolve_domains_to_ips(domains):
        ip_addresses = set()
        resolved_count = failed_count = 0
        socket.setdefaulttimeout(1)
        
        with Progress(SpinnerColumn(), *Progress.get_default_columns(), TimeElapsedColumn(), transient=True) as progress:
            task = progress.add_task("[yellow]Resolving", total=len(domains))
            
            with ThreadPoolExecutor(max_workers=100) as executor:
                future_to_domain = {executor.submit(IPProcessor.resolve_domain, domain): domain for domain in domains}
                for future in as_completed(future_to_domain):
                    domain, ip = future.result()
                    if ip:
                        ip_addresses.add(ip)
                        resolved_count += 1
                    else:
                        failed_count += 1
                    progress.update(task, advance=1)
        
        return sorted(ip_addresses), resolved_count, failed_count

class MenuManager:
    def __init__(self):
        self.options = {
            "1": ("Split file", self.split_txt_file, "bold cyan"),
            "2": ("Merge files", self.merge_txt_files, "bold blue"),
            "3": ("Remove duplicates", self.remove_duplicate_domains, "bold yellow"),
            "4": ("Subdomains to domains", self.convert_subdomains_to_domains, "bold magenta"),
            "5": ("Domains and IP extractor", self.txt_cleaner, "bold cyan"),
            "6": ("Filter by extension", self.separate_domains_by_extension, "bold magenta"),
            "7": ("Filter by keywords", self.filter_by_keywords, "bold yellow"),
            "8": ("CIDR to IP", self.cidr_to_ip, "bold green"),
            "9": ("Domains to IP", self.domains_to_ip, "bold blue"),
            "0": ("Back", lambda: None, "bold red")
        }

    def split_txt_file(self):
        file_path = get_input("File path", "file")
        parts = int(get_input("Number of parts", "number"))
        created_files = FileHandler.split_file(file_path, parts)
        
        if created_files:
            print(f"[green] Successfully split '{os.path.basename(file_path)}' into {len(created_files)} parts:[/green]")
            for file_path, line_count in created_files:
                print(f"[green] - {os.path.basename(file_path)}: {line_count} lines[/green]")

    def merge_txt_files(self):
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
        total_lines = FileHandler.merge_files(directory, files_to_merge, output_file)
        
        if total_lines:
            print(f"[green] Successfully merged {len(files_to_merge)} files into '{output_file}'[/green]")
            print(f"[green] - Total lines: {total_lines}[/green]")
            print(f"[green] - Output location: {directory}[/green]")

    def remove_duplicate_domains(self):
        file_path = get_input("File path", "file")
        lines = FileHandler.read_lines(file_path)
        
        if not lines:
            return
        
        unique_lines = sorted(set(lines))
        duplicates_removed = len(lines) - len(unique_lines)
        
        if FileHandler.write_lines(file_path, unique_lines):
            print(f"[green] Successfully removed duplicates from '{os.path.basename(file_path)}':[/green]")
            print(f"[green] - Original count: {len(lines)} lines[/green]")
            print(f"[green] - Unique count: {len(unique_lines)} lines[/green]")
            print(f"[green] - Duplicates removed: {duplicates_removed} lines[/green]")

    def txt_cleaner(self):
        input_file = get_input("File path", "file")
        domain_output_file = get_input("Domain output file")
        ip_output_file = get_input("IP output file")
        
        content = FileHandler.read_lines(input_file)
        if not content:
            return
        
        domains, ips = DomainProcessor.extract_domains_and_ips(content)
        
        domains_success = FileHandler.write_lines(domain_output_file, domains)
        ips_success = FileHandler.write_lines(ip_output_file, ips)
        
        if domains_success or ips_success:
            print(f"[green] TXT Cleaner results for '{os.path.basename(input_file)}':[/green]")
            if domains_success:
                print(f"[green] - Extracted {len(domains)} unique domains to '{os.path.basename(domain_output_file)}'[/green]")
            if ips_success:
                print(f"[green] - Extracted {len(ips)} unique IP addresses to '{os.path.basename(ip_output_file)}'[/green]")

    def convert_subdomains_to_domains(self):
        file_path = get_input("File path", "file")
        output_file = get_input("Output file")
        
        subdomains = FileHandler.read_lines(file_path)
        if not subdomains:
            return

        root_domains = DomainProcessor.get_root_domains(subdomains)
        
        if FileHandler.write_lines(output_file, root_domains):
            print(f"[green] Successfully converted subdomains to root domains:[/green]")
            print(f"[green] - Input subdomains: {len(subdomains)}[/green]")
            print(f"[green] - Unique root domains: {len(root_domains)}[/green]")
            print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")

    def separate_domains_by_extension(self):
        file_path = get_input("File path", "file")
        extensions_input = get_input("Extensions (comma-separated) or 'all'")
        
        domains = FileHandler.read_lines(file_path)
        if not domains:
            return
        
        extensions_dict = DomainProcessor.separate_by_extension(domains)
        base_name = os.path.splitext(file_path)[0]
        target_extensions = [ext.strip() for ext in extensions_input.lower().split(',')] if extensions_input.lower() != 'all' else list(extensions_dict.keys())
        
        success_count = 0
        print(f"[green] Separating domains by extension from '{os.path.basename(file_path)}':[/green]")
        
        for ext in target_extensions:
            if ext in extensions_dict:
                ext_file = f"{base_name}_{ext}.txt"
                if FileHandler.write_lines(ext_file, sorted(extensions_dict[ext])):
                    success_count += 1
                    print(f"[green] - Created '{os.path.basename(ext_file)}' with {len(extensions_dict[ext])} domains[/green]")
            else:
                print(f"[yellow] - No domains found with .{ext} extension[/yellow]")
        
        if success_count > 0:
            print(f"[green] Successfully created {success_count} files based on domain extensions[/green]")

    def filter_by_keywords(self):
        file_path = get_input("File path", "file")
        keywords = [k.strip().lower() for k in get_input("Keywords (comma-separated)").split(',')]
        output_file = get_input("Output file")
        
        lines = FileHandler.read_lines(file_path)
        if not lines:
            return
        
        filtered_domains = DomainProcessor.filter_by_keywords(lines, keywords)
        
        if FileHandler.write_lines(output_file, filtered_domains):
            print(f"[green] Successfully filtered domains by keywords:[/green]")
            print(f"[green] - Input domains: {len(lines)}[/green]")
            print(f"[green] - Matched domains: {len(filtered_domains)}[/green]")
            print(f"[green] - Keywords used: {', '.join(keywords)}[/green]")
            print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")

    def cidr_to_ip(self):
        cidr_input = get_input("CIDR range")
        output_file = get_input("Output file")
        
        ip_addresses = IPProcessor.convert_cidr_to_ips(cidr_input)
        
        if ip_addresses and FileHandler.write_lines(output_file, ip_addresses):
            print(f"[green] Successfully converted CIDR to IP addresses:[/green]")
            print(f"[green] - CIDR range: {cidr_input}[/green]")
            print(f"[green] - Total IPs: {len(ip_addresses)}[/green]")
            print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")

    def domains_to_ip(self):
        file_path = get_input("File path", "file")
        output_file = get_input("Output file")
        
        domains = FileHandler.read_lines(file_path)
        if not domains:
            return
            
        ip_addresses, resolved_count, failed_count = IPProcessor.resolve_domains_to_ips(domains)
        
        if ip_addresses and FileHandler.write_lines(output_file, ip_addresses):
            print(f"[green] Successfully resolved domains to IP addresses:[/green]")
            print(f"[green] - Input domains: {len(domains)}[/green]")
            print(f"[green] - Successfully resolved: {resolved_count}[/green]")
            print(f"[green] - Failed to resolve: {failed_count}[/green]")
            print(f"[green] - Unique IP addresses: {len(ip_addresses)}[/green]")
            print(f"[green] - Output file: '{os.path.basename(output_file)}'[/green]")
        else:
            print("[red] No domains could be resolved or there was an error writing to the output file[/red]")

def main():
    menu = MenuManager()
    print("\n".join(f"[{color}] [{key}] {desc}" for key, (desc, _, color) in menu.options.items()))
    choice = input("\n \033[36m[-]  Your Choice: \033[0m")
    
    if choice in menu.options:
        menu.options[choice][1]()
        if choice == '0':
            return
