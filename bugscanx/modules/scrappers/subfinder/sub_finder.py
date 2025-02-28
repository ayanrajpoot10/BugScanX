import os
import httpx
import aiofiles
import asyncio

from bugscanx.utils import get_input
from .subfinder_console import SubFinderConsole
from .subfinder_sources import get_all_sources, get_bulk_sources
from .subfinder_utils import is_valid_domain, filter_valid_subdomains
from .concurrent_processor import ConcurrentProcessor

async def process_domain(domain, output_file, sources, console, total=1, current=1):
    if not is_valid_domain(domain):
        console.print_error(f"Invalid domain: {domain}")
        return set()

    await console.start_domain_scan(domain)
    await console.show_progress(current, total)
    
    async with httpx.AsyncClient() as client:
        async def fetch_source(source):
            try:
                found = await source.fetch(domain, client)
                return await filter_valid_subdomains(found, domain)
            except Exception as e:
                console.print_error(f"[red]Error with {source.name}: {str(e)}[/red]")
                return set()

        results = await asyncio.gather(
            *[fetch_source(source) for source in sources]
        )
        subdomains = set().union(*results)

    console.update_domain_stats(domain, len(subdomains))
    await console.print_domain_complete(domain, len(subdomains))

    async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
        await f.write("\n".join(sorted(subdomains)) + "\n")

    return subdomains

async def find_subdomains():
    console = SubFinderConsole()
    domains = []
    
    if await get_input("Select input type", "choice", 
                       choices=["single domain", "bulk domains from file"],
                       use_async=True) == "single domain":
        domains = [await get_input("Enter the domain to find subdomains", use_async=True)]
        sources = get_all_sources()
        output_file = f"{domains[0]}_subdomains.txt"
    else:
        file_path = await get_input("Enter the path to the file containing domains", "file", use_async=True)
        with open(file_path, 'r') as f:
            domains = [d.strip() for d in f if is_valid_domain(d.strip())]
        sources = get_bulk_sources()
        output_file = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

    if not domains:
        console.print_error("No valid domains provided")
        return

    output_file = await get_input("Enter the output file name", default=output_file, use_async=True)
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

    async def process_domain_wrapper(domain: str, index: int):
        return await process_domain(domain, output_file, sources, console, len(domains), index + 1)

    processor = ConcurrentProcessor(max_concurrent=3)
    all_subdomains = await processor.process_items(
        domains,
        process_domain_wrapper,
        on_error=lambda domain, error: console.print_error(f"Error processing {domain}: {error}")
    )

    console.print_final_summary(output_file)
