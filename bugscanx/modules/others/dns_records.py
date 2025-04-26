import os
from rich import print
from dns import resolver as dns_resolver
from bugscanx.utils.common import get_input, get_confirm

def configure_resolver(custom_nameservers=None):
    dns_obj = dns_resolver.Resolver()
    
    if custom_nameservers and len(custom_nameservers) > 0:
        dns_obj.nameservers = custom_nameservers
        print(f"[yellow]Using custom DNS servers: {', '.join(custom_nameservers)}[/yellow]")
        return dns_obj
    
    is_termux = 'com.termux' in os.environ.get('PREFIX', '') or os.path.exists('/data/data/com.termux')
    
    if is_termux:
        dns_obj.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
    
    return dns_obj

def resolve_and_print(domain, record_type, custom_nameservers=None):
    print(f"\n[green] {record_type} Records:[/green]")
    try:
        dns_obj = configure_resolver(custom_nameservers)
        answers = dns_obj.resolve(domain, record_type)
        found = False
        for answer in answers:
            found = True
            if record_type == 'MX':
                print(f"[cyan]- {answer.exchange} (priority: {answer.preference})[/cyan]")
            elif record_type == 'SOA':
                print(f"[cyan]- Primary NS: {answer.mname}")
                print(f"  Responsible: {answer.rname}")
                print(f"  Serial: {answer.serial}")
                print(f"  Refresh: {answer.refresh}")
                print(f"  Retry: {answer.retry}")
                print(f"  Expire: {answer.expire}")
                print(f"  Minimum TTL: {answer.minimum}[/cyan]")
            elif record_type == 'SRV':
                print(f"[cyan]- Priority: {answer.priority}, Weight: {answer.weight}")
                print(f"  Port: {answer.port}, Target: {answer.target}[/cyan]")
            else:
                print(f"[cyan]- {answer.to_text()}[/cyan]")
        if not found:
            print(f"[yellow] No {record_type} records found[/yellow]")
    except (dns_resolver.NXDOMAIN, dns_resolver.NoAnswer):
        print(f"[yellow] No {record_type} records found[/yellow]")
    except Exception:
        print(f"[yellow] Error fetching {record_type} record[/yellow]")

def nslookup(domain, custom_nameservers=None):
    print(f"[cyan]\n Performing NSLOOKUP for: {domain}[/cyan]")
    
    record_types = [
        'A',
        'AAAA',
        'CNAME',
        'MX',
        'NS',
        'TXT',
        'SOA',
        'PTR',
        'SRV',
        'CAA',
        'DNSKEY',
        'TLSA'
    ]
    
    for record_type in record_types:
        resolve_and_print(domain, record_type, custom_nameservers)

def main():
    domain = get_input("Enter the domain to lookup")
    if not domain:
        print("[red] Please enter a valid domain.[/red]")
        return
    
    use_custom_dns = get_confirm(" Want to use custom DNS servers?")
    custom_nameservers = None
    
    if use_custom_dns:
        nameservers_input = get_input("Enter DNS servers separated by commas (e.g., 8.8.8.8,1.1.1.1)")
        if nameservers_input:
            custom_nameservers = [server.strip() for server in nameservers_input.split(',')]
            print(f"[cyan] Will use custom DNS servers: {', '.join(custom_nameservers)}[/cyan]")
    
    try:
        nslookup(domain, custom_nameservers)
    except Exception as e:
        print(f"[red] An error occurred during DNS lookup: {str(e)}[/red]")
