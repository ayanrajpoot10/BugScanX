import dns.resolver
import dns.reversename

from rich import print

from bugscanx.utils import get_input

def resolve_a_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"[red] Error fetching A record: {e}[/red]")
    return []

def resolve_cname_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        return [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"[red] Error fetching CNAME record: {e}[/red]")
    return []

def resolve_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [f"{answer.exchange} (priority: {answer.preference})" for answer in answers]
    except Exception as e:
        print(f"[red] Error fetching MX record: {e}[/red]")
    return []

def resolve_ns_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        return [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"[red] Error fetching NS record: {e}[/red]")
    return []

def resolve_txt_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        return [answer.to_text() for answer in answers]
    except Exception as e:
        print(f"[red] Error fetching TXT record: {e}[/red]")
    return []

def nslookup(domain):
    print(f"[cyan]\n Performing NSLOOKUP for: {domain}[/cyan]")

    records = {
        "A": resolve_a_record(domain),
        "CNAME": resolve_cname_record(domain),
        "MX": resolve_mx_record(domain),
        "NS": resolve_ns_record(domain),
        "TXT": resolve_txt_record(domain),
    }

    for record_type, values in records.items():
        if values:
            print(f"[green]\n {record_type} Records:[/green]")
            for value in values:
                if value:
                    print(f"[cyan]- {value}[/cyan]")
        else:
            print(f"[red]\n No {record_type} records found for {domain}.[/red]")

def main():
    domain = get_input("\n Enter the domain to lookup")
    if not domain:
        print("[red] Please enter a valid domain.[/red]")
    nslookup(domain)



