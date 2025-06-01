import re
import random
import string
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


class DomainValidator:
    DOMAIN_REGEX = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
    )

    @classmethod
    def is_valid_domain(cls, domain):
        return bool(
            domain
            and isinstance(domain, str)
            and cls.DOMAIN_REGEX.match(domain)
        )

    @staticmethod
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


class WildcardDetector:
    def __init__(self, timeout=3):
        self.wildcard_ips = set()
        self.wildcard_detected = False
        self.timeout = timeout
        
    def _generate_random_subdomain(self, length=10):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{random_string}-nonexistent-{random.randint(10000, 99999)}"
    
    def _resolve_domain(self, domain):
        try:
            socket.setdefaulttimeout(self.timeout)
            ip = socket.gethostbyname(domain)
            return True, ip
        except (socket.gaierror, socket.timeout):
            return False, None
        except Exception:
            return False, None
    
    def detect_wildcards(self, domain, test_count=5):
        self.wildcard_ips.clear()
        self.wildcard_detected = False
        
        wildcard_candidates = {}
        
        for _ in range(test_count):
            random_subdomain = self._generate_random_subdomain()
            test_domain = f"{random_subdomain}.{domain}"
            
            exists, ip = self._resolve_domain(test_domain)
            if exists and ip:
                ips = [ip] if isinstance(ip, str) else ip
                for single_ip in ips:
                    if single_ip in wildcard_candidates:
                        wildcard_candidates[single_ip] += 1
                    else:
                        wildcard_candidates[single_ip] = 1

        for ip, count in wildcard_candidates.items():
            if count >= 2:
                self.wildcard_ips.add(ip)
                self.wildcard_detected = True
        
        return self.wildcard_detected
    
    def is_wildcard_ip(self, ip):
        if not ip:
            return False
        
        ips_to_check = [ip] if isinstance(ip, str) else ip
        
        for single_ip in ips_to_check:
            if single_ip in self.wildcard_ips:
                return True
        return False
    
    def get_wildcard_ips(self):
        return self.wildcard_ips.copy()


class DNSResolver:
    def __init__(self, timeout=3):
        socket.setdefaulttimeout(timeout)
    
    def resolve(self, hostname):
        try:
            
            ip = socket.gethostbyname(hostname)
            return True, ip
        except (socket.gaierror, socket.timeout):
            return False, None
        except Exception:
            return False, None

    def check_subdomain(self, subdomain):
        success, result = self.resolve(subdomain)
        return success, result


class WordlistManager:
    def __init__(self, wordlist_path=None):
        self.wordlist_path = wordlist_path
        self.wordlist = []
        
    def load_wordlist(self):
        if not self.wordlist_path:
            raise ValueError("Wordlist path not specified")
            
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
            return True
        except FileNotFoundError:
            raise FileNotFoundError(f"Wordlist file not found: {self.wordlist_path}")
        except Exception as e:
            raise Exception(f"Error loading wordlist: {str(e)}")
    
    def get_wordlist(self):
        return self.wordlist
    
    def get_wordlist_size(self):
        return len(self.wordlist)


class SubdomainBruteforcer:
    def __init__(self, wordlist_path, max_workers=50, timeout=3, enable_wildcard_filtering=True):
        self.wordlist_manager = WordlistManager(wordlist_path)
        self.dns_resolver = DNSResolver(timeout=timeout)
        self.wildcard_detector = WildcardDetector(timeout=timeout)
        self.max_workers = max_workers
        self.wordlist = []
        self.enable_wildcard_filtering = enable_wildcard_filtering
        self.wildcard_detected = False
        
    def load_wordlist(self):
        self.wordlist_manager.load_wordlist()
        self.wordlist = self.wordlist_manager.get_wordlist()
        return len(self.wordlist)
        
    def _test_subdomain(self, word, domain):
        subdomain = f"{word}.{domain}"
        exists, ip = self.dns_resolver.check_subdomain(subdomain)
        
        if exists and ip:
            if self.enable_wildcard_filtering and self.wildcard_detected:
                if self.wildcard_detector.is_wildcard_ip(ip):
                    return None, None
            return subdomain, ip
        return None, None
        
    def bruteforce_domain(self, domain, progress_callback=None):
        found_subdomains = set()
        tested_count = 0
        
        if self.enable_wildcard_filtering:
            self.wildcard_detected = self.wildcard_detector.detect_wildcards(domain)
            if self.wildcard_detected and progress_callback:
                wildcard_ips = self.wildcard_detector.get_wildcard_ips()
                progress_callback('wildcard_detected', wildcard_ips)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_word = {
                executor.submit(self._test_subdomain, word, domain): word 
                for word in self.wordlist
            }

            for future in as_completed(future_to_word):
                tested_count += 1
                try:
                    subdomain, ip = future.result()
                    if subdomain:
                        found_subdomains.add(subdomain)
                        if progress_callback:
                            progress_callback('found', subdomain, ip)
                except Exception as e:
                    pass
                    
                if progress_callback:
                    progress_callback('progress', tested_count, len(found_subdomains))
                    
        return found_subdomains


class CursorManager:
    def __enter__(self):
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('\033[?25h', end='', flush=True)
