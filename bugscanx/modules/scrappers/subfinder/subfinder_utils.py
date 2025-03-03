import re
import random
import requests
from requests.exceptions import RequestException
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
    except RequestException:
        pass
    return None

def is_valid_domain(domain):
    regex = re.compile(
        r'^(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z]{2,6}$'
    )
    return domain and isinstance(domain, str) and re.match(regex, domain) is not None

def filter_valid_subdomains(subdomains, domain):
    result = set()
    for sub in subdomains:
        if isinstance(sub, str) and is_valid_domain(sub):
            if sub.endswith(f".{domain}") or sub == domain:
                result.add(sub)
    return result
