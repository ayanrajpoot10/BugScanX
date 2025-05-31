from dns import resolver as dns_resolver
from rich import print

from bugscanx.utils.common import get_input


def configure_resolver():
    return dns_resolver.Resolver()


def resolve_and_print(domain, record_type):
    print(f"\n[green] {record_type} Records:[/green]")
    try:
        dns_obj = configure_resolver()
        answers = dns_obj.resolve(domain, record_type)
        found = False
        for answer in answers:
            found = True
            if record_type == "MX":
                print(
                    f"[cyan]- {answer.exchange} "
                    f"(priority: {answer.preference})[/cyan]"
                )
            else:
                print(f"[cyan]- {answer.to_text()}[/cyan]")
        if not found:
            print(f"[yellow] No {record_type} records found[/yellow]")
    except (dns_resolver.NXDOMAIN, dns_resolver.NoAnswer):
        print(f"[yellow] No {record_type} records found[/yellow]")
    except Exception:
        print(f"[yellow] Error fetching {record_type} record[/yellow]")


def nslookup(domain):
    print(f"[cyan]\n Performing NSLOOKUP for: {domain}[/cyan]")

    record_types = [
        "A",
        "AAAA",
        "CNAME",
        "MX",
        "NS",
        "TXT",
    ]

    for record_type in record_types:
        resolve_and_print(domain, record_type)


def main():
    domain = get_input("Enter target")

    try:
        nslookup(domain)
    except Exception as e:
        print(f"[red] An error occurred during DNS lookup: {str(e)}[/red]")
