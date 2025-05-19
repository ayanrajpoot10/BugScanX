import re
import random
import requests
from bugscanx.utils.http import HEADERS, USER_AGENTS


class RequestHandler:
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        self.session.headers.update(HEADERS)
        self.session.timeout = 10

    def get(self, url):
        try:
            self.session.headers["user-agent"] = random.choice(USER_AGENTS)
            response = self.session.get(url)
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
    r'[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
)


def is_valid_domain(domain):
    return bool(
        domain
        and isinstance(domain, str)
        and DOMAIN_REGEX.match(domain)
    )


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
