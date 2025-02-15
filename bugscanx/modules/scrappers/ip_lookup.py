import ipaddress
import random
import threading
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from rich import print

from bugscanx.utils import (
    get_input,
    cidr_validator,
    choice_validator,
    not_empty_validator,
    file_path_validator,
    digit_validator,
    completer
)
from bugscanx.utils.http_utils import USER_AGENTS, EXTRA_HEADERS

file_write_lock = threading.Lock()

def fetch_rapiddns(ip):
    base_url = f"https://rapiddns.io/sameip/{ip}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        **EXTRA_HEADERS
    }
    time.sleep(random.uniform(1, 3))
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return [row.find_all('td')[0].text.strip() for row in soup.find_all('tr') if row.find_all('td')]
    except requests.RequestException:
        return []

def fetch_yougetsignal(ip):
    url = "https://domains.yougetsignal.com/domains.php"
    data = {
        'remoteAddress': ip,
        'key': '',
        '_': ''
    }
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        return [domain[0] for domain in response.json().get("domainArray", [])]
    except requests.RequestException:
        return []

def fetch_bing(ip):
    base_url = f"https://www.bing.com/search?q=ip%3A{ip}"
    time.sleep(random.uniform(1, 3))
    try:
        response = requests.get(base_url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        return [title['href'].split('/')[2] for row in soup.find_all('li', class_='b_algo') if (title := row.find('a'))]
    except requests.RequestException:
        return []

def extract_domains_for_ip(ip):
    domains = []
    print(f"[cyan] Searching domains for IP: {ip}[cyan]")
    
    domains += fetch_rapiddns(ip)
    domains += fetch_yougetsignal(ip)
    domains += fetch_bing(ip)

    domains = sorted(set(domains))
    
    print(f"[green] Domains found for IP {ip}: {len(domains)}[/green]")
    
    return (ip, domains)

def save_results_to_file(results, output_file):
    total_domains_found = 0
    with open(output_file, 'a') as f:
        for ip, domains in results:
            total_found = len(domains)
            if total_found == 0:
                continue
            total_domains_found += total_found
            f.write(f"Domains found for IP {ip}: {total_found}\n")
            for domain in domains:
                f.write(f"{domain}\n")
    print(f"[green]\n Saved! Current total domains found across processed IPs: {total_domains_found}[/green]")

def process_cidr(cidr, ip_queue):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        for ip in network.hosts():
            ip_queue.put(str(ip))
    except ValueError as e:
        print(f" Invalid CIDR block {cidr}: {e}")

def Ip_lookup_menu():
    input_choice = get_input("\n Enter 1 for manual CIDR input or 2 for file input", validator=choice_validator)
    
    if input_choice == "1":
        cidr_or_filename = get_input(" Enter an IP or CIDR", validator=cidr_validator)
    else:
        cidr_or_filename = get_input(" Enter the file path containing IPs/CIDRs", validator=file_path_validator, completer=completer)
    
    output_file = get_input(" Enter the output file path", validator=not_empty_validator)

    ip_queue = Queue()

    if input_choice == "1":
        if '/' in cidr_or_filename:
            process_cidr(cidr_or_filename, ip_queue)
        else:
            ip_queue.put(cidr_or_filename)
    else:
        with open(cidr_or_filename, 'r') as f:
            for line in f:
                entry = line.strip()
                if entry:
                    if '/' in entry:
                        process_cidr(entry, ip_queue)
                    else:
                        ip_queue.put(entry)

    total_ips = ip_queue.qsize()
    if total_ips == 0:
        print("[bold red] No valid IPs/CIDRs to process.[/bold red]")
        return

    while True:
        threads_input = get_input(" Enter the number of threads to use (1-5)", validator=digit_validator)
        threads = int(threads_input)
        if 1 <= threads <= 5:
            break
        else:
            print("[bold red] Please enter a number between 1 and 5.[/bold red]")

    results = []
    progress = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(extract_domains_for_ip, ip_queue.get()) for _ in range(total_ips)]
        
        for i, future in enumerate(futures, start=1):
            results.append(future.result())
            progress += 1

            if i % 5 == 0 or i == total_ips:
                percent_complete = (progress / total_ips) * 100
                print(f"[yellow]\r Progress: {progress}/{total_ips} IPs processed ({percent_complete:.2f}%)[/yellow]", end="")
                save_results_to_file(results[-5:], output_file)
    
    print()
    print("[green]\n All IPs processed![/green]")
