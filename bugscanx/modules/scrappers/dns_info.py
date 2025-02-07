import dns.resolver
import dns.reversename
from bugscanx.utils import *
from colorama import Fore, init
init(autoreset=True)

def resolve_a_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        print(Fore.RED + " No A record found.")
    except dns.resolver.NXDOMAIN:
        print(Fore.RED + " Domain does not exist.")
    except Exception as e:
        print(Fore.RED + f" Error fetching A record: {e}")
    return []

def resolve_cname_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        print(Fore.RED + " No CNAME record found.")
    except dns.resolver.NXDOMAIN:
        print(Fore.RED + " Domain does not exist.")
    except Exception as e:
        print(Fore.RED + f" Error fetching CNAME record: {e}")
    return []

def resolve_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [f"{answer.exchange} (priority: {answer.preference})" for answer in answers]
    except dns.resolver.NoAnswer:
        print(Fore.RED + " No MX record found.")
    except dns.resolver.NXDOMAIN:
        print(Fore.RED + " Domain does not exist.")
    except Exception as e:
        print(Fore.RED + f" Error fetching MX record: {e}")
    return []

def resolve_ns_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        print(Fore.RED + " No NS record found.")
    except dns.resolver.NXDOMAIN:
        print(Fore.RED + " Domain does not exist.")
    except Exception as e:
        print(Fore.RED + f" Error fetching NS record: {e}")
    return []

def resolve_txt_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        print(Fore.RED + " No TXT record found.")
    except dns.resolver.NXDOMAIN:
        print(Fore.RED + " Domain does not exist.")
    except Exception as e:
        print(Fore.RED + f" Error fetching TXT record: {e}")
    return []

def nslookup(domain):
    print(Fore.CYAN + f"\n Performing NSLOOKUP for: {domain}")

    records = {
        "A": resolve_a_record(domain),
        "CNAME": resolve_cname_record(domain),
        "MX": resolve_mx_record(domain),
        "NS": resolve_ns_record(domain),
        "TXT": resolve_txt_record(domain),
    }

    for record_type, values in records.items():
        if values:
            print(Fore.GREEN + f"\n {record_type} Records:")
            for value in values:
                if value:
                    print(Fore.LIGHTCYAN_EX + f"- {value}")
        else:
            print(Fore.RED + f"\n No {record_type} records found for {domain}.")

def main():
    domain = get_input("\n Enter the domain to lookup")
    if not domain:
        print(Fore.RED + " Please enter a valid domain.")
    nslookup(domain)



