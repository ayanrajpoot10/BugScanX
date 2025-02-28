import asyncio
from rich import print
from bugscanx.utils import get_input, is_cidr

from .scrapers import get_scrapers
from .ip_utils import process_input, process_file
from .result_manager import ResultManager


async def extract_domains(ip, scrapers):
    print(f"[cyan] Searching domains for IP: {ip}[/cyan]")
    domains = []
    tasks = [scraper.fetch_domains(ip) for scraper in scrapers]
    results = await asyncio.gather(*tasks)
    
    for domain_list in results:
        if domain_list:
            domains.extend(domain_list)
            
    domains = sorted(set(domains))
    return (ip, domains)


async def process_ips(ips, output_file):
    if not ips:
        print("[bold red] No valid IPs/CIDRs to process.[/bold red]")
        return 0
        
    scrapers = get_scrapers()
    semaphore = asyncio.Semaphore(5)
    total_domains = 0
    result_manager = ResultManager(output_file)
    
    total_ips = len(ips)
    processed = 0
    
    async def process_ip_with_semaphore(ip):
        async with semaphore:
            ip, domains = await extract_domains(ip, scrapers)
            if domains:
                await result_manager.save_result(ip, domains)
                nonlocal total_domains
                total_domains += len(domains)
            
            nonlocal processed
            processed += 1
            progress = processed / total_ips * 100
            print(f"[yellow] Progress: {processed}/{total_ips} IPs processed ({progress:.2f}%)[/yellow]")
            return ip, domains

    tasks = [process_ip_with_semaphore(ip) for ip in ips]
    for future in asyncio.as_completed(tasks):
        await future
    
    for scraper in scrapers:
        await scraper.close()
        
    print(f"[green]\n All IPs processed! Total domains found: {total_domains}[/green]")
    return total_domains
    

async def get_input_interactively():
    ips = []
    
    input_choice = await get_input("Choose input type", "choice", 
                                  choices=["Manual IP/CIDR", "IP/CIDR from file"], 
                                  use_async=True)
    
    if input_choice == "Manual IP/CIDR":
        cidr = await get_input("Enter an IP or CIDR", validators=[is_cidr], use_async=True)
        ips.extend(process_input(cidr))
    else:
        file_path = await get_input("Enter the file path containing IPs/CIDRs", "file", use_async=True)
        ips.extend(process_file(file_path))
        
    output_file = await get_input("Enter the output file path", use_async=True)
    return ips, output_file


async def iplookup_main(ips=None, output_file=None):
    if ips is None or output_file is None:
        ips, output_file = await get_input_interactively()
    await process_ips(ips, output_file)

