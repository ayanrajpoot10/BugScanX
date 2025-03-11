import re
import random
import requests
from bugscanx.utils import HEADERS, USER_AGENTS, SUBFINDER_TIMEOUT

def make_request(url, session=None):
    try:
        headers = HEADERS.copy()
        headers["user-agent"] = random.choice(USER_AGENTS)
        
        if session:
            response = session.get(url, headers=headers, timeout=SUBFINDER_TIMEOUT)
        else:
            response = requests.get(url, headers=headers, timeout=SUBFINDER_TIMEOUT)
            
        if response.status_code == 200:
            return response
    except requests.RequestException:
        pass
    return None

DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
    r'[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
)

def is_valid_domain(domain):
    return bool(domain and isinstance(domain, str) and DOMAIN_REGEX.match(domain))

def filter_valid_subdomains(subdomains, domain):
    if not domain or not isinstance(domain, str):
        return set()
    
    domain_suffix = f".{domain}"
    result = set()
    
    for sub in subdomains:
        if not isinstance(sub, str):
            continue
            
        if sub == domain or sub.endswith(domain_suffix):
            result.add(sub)
                
    return result
