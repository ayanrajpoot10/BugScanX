import asyncio
from typing import List
from rich import print

class ResultManager:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.total_domains = 0
        self.lock = asyncio.Lock()

    async def save_result(self, ip: str, domains: List[str]):
        if not domains:
            return
            
        async with self.lock:
            with open(self.output_file, 'a') as f:
                for domain in domains:
                    f.write(f"{domain}\n")
            self.total_domains += len(domains)
            print(f"[green] Saved domains for {ip}. Current total domains found: {self.total_domains}[/green]")
