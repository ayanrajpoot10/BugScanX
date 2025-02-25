import re
import random
import httpx
from bugscanx.utils import HEADERS, USER_AGENTS, SUBFINDER_TIMEOUT

async def make_request(url, client):
    try:
        headers = HEADERS.copy()
        headers["user-agent"] = random.choice(USER_AGENTS)
        
        response = await client.get(url, headers=headers, timeout=SUBFINDER_TIMEOUT)
        if response.status_code == 200:
            return response
    except httpx.RequestError:
        pass
    return None

def is_valid_domain(domain):
    regex = re.compile(
        r'^(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z]{2,6}$'
    )
    return domain and isinstance(domain, str) and re.match(regex, domain) is not None

async def filter_valid_subdomains(subdomains, domain):
    result = set()
    for sub in subdomains:
        if isinstance(sub, str) and is_valid_domain(sub):
            # Ensure it's related to the target domain
            if sub.endswith(f".{domain}") or sub == domain:
                result.add(sub)
    return result
