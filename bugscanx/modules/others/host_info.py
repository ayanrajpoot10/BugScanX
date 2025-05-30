import ssl
import socket
import http.client
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from rich import print

from bugscanx.utils.common import get_input


class HostScanner:
    CDN_PROVIDERS = {
        "Cloudflare": {
            "headers": ["cf-ray", "cf-cache-status", "cf-request-id", "cf-visitor", "cf-connecting-ip", "cf-ipcountry", "cf-railgun", "cf-polished", "cf-apo-via"],
            "cname": ["cloudflare.net", "cloudflare.com", "cloudflare-dns.com"]
        },
        "Amazon CloudFront": {
            "headers": ["x-amz-cf-id", "x-amz-cf-pop", "x-amz-request-id"],
            "cname": ["cloudfront.net", "amazonaws.com"]
        },
        "Google": {
            "headers": ["x-goog-cache-status", "x-goog-generation", "x-goog-metageneration", "x-guploader-uploadid"],
            "cname": ["googleusercontent.com", "googlevideo.com", "google.com", "gstatic.com", "googleapis.com"]
        },
        "Akamai": {
            "headers": ["x-akamai-transformed", "akamai-cache-status", "akamai-origin-hop", "x-akamai-request-id", "x-akamai-ssl-client-sid", "akamai-grn", "x-akamai-config-log-detail"],
            "cname": ["akamai.net", "edgekey.net", "edgesuite.net", "akamaized.net", "akamaiedge.net", "akamaitechnologies.com", "akamaihd.net"]
        },
        "Fastly": {
            "headers": ["fastly-debug", "x-served-by", "x-cache-hits", "x-timer", "fastly-ff", "x-fastly-request-id"],
            "cname": ["fastly.net", "fastlylb.net"]
        },
        "Microsoft Azure": {
            "headers": ["x-azure-ref", "x-azure-requestid", "x-msedge-ref", "x-ec-custom-error", "x-azure-fdid"],
            "cname": ["azureedge.net", "msedge.net", "azure-edge.net", "trafficmanager.net", "azurefd.net"]
        },
        "BunnyCDN": {
            "headers": ["cdn-pullzone", "cdn-uid", "cdn-requestid", "cdn-cache", "cdn-zone", "bunnycdn-cache-tag"],
            "cname": ["b-cdn.net"]
        },
        "KeyCDN": {
            "headers": ["x-edge-location", "server-keycdn"],
            "cname": ["kxcdn.com"]
        },
        "Sucuri": {
            "headers": ["x-sucuri-id", "x-sucuri-cache", "x-sucuri-block", "server-sucuri"],
            "cname": ["sucuri.net"]
        },
        "Imperva": {
            "headers": ["x-iinfo", "incap-ses", "visid-incap"],
            "cname": ["incapdns.net", "imperva.com", "impervadns.net"]
        },
        "Cachefly": {
            "headers": ["x-cf-", "server-cachefly"],
            "cname": ["cachefly.net"]
        },
        "CDN77": {
            "headers": ["x-77-", "server-cdn77"],
            "cname": ["cdn77.net", "cdn77.org"]
        },
        "Alibaba": {
            "headers": ["ali-cdn-", "x-oss-", "server-tengine"],
            "cname": ["alikunlun.com", "alicdn.com"]
        },
        "Tencent": {
            "headers": ["x-nws-", "x-daa-tunnel"],
            "cname": ["qcloudcdn.com", "myqcloud.com"]
        }
    }

    def __init__(self, host, protocol="https", method_list=None):
        self.host = host
        self.protocol = protocol
        self.url = f"{protocol}://{host}"
        self.method_list = method_list

    def get_ips(self):
        try:
            ips = socket.getaddrinfo(self.host, None)
            unique_ips = list(set(ip[4][0] for ip in ips))
            print("[bold white]\nIPs:[/bold white]")
            for ip in unique_ips:
                print(f"  • {ip}")
            return True
        except socket.gaierror as e:
            print(f"[bold red] Error resolving hostname: {e}[/bold red]")
            return False

    def get_cname_records(self):
        try:
            result = []
            answers = socket.getaddrinfo(self.host, None)
            for answer in answers:
                try:
                    cname = socket.gethostbyaddr(answer[4][0])[0]
                    result.append(cname.lower())
                except (socket.herror, socket.gaierror):
                    continue
            return result
        except (socket.herror, socket.gaierror):
            return []

    def get_cdn(self):
        try:
            detected_cdns = set()
            
            response = requests.get(self.url, timeout=5)
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            cnames = self.get_cname_records()
            
            for provider, indicators in self.CDN_PROVIDERS.items():
                if any(header.lower() in headers.keys() for header in indicators['headers']):
                    detected_cdns.add(provider)
                    continue
                
                if any(cname_pattern in cname for cname in cnames 
                      for cname_pattern in indicators['cname']):
                    detected_cdns.add(provider)
            
            if detected_cdns:
                print("[bold white]\nCDNs:[/bold white]")
                for cdn in detected_cdns:
                    print(f"  • {cdn}")
            else:
                print("[bold white]\nNo known CDN[/bold white]")
                
        except requests.exceptions.RequestException as e:
            print(f"[bold red] Error checking CDN: {e}[/bold red]")

    def get_http_info(self):
        def check_method(method):
            try:
                response = requests.request(method, self.url, timeout=5)
                return method, response.status_code, dict(response.headers)
            except requests.exceptions.RequestException as e:
                return method, 0, {'error': str(e)}
        
        with ThreadPoolExecutor(max_workers=len(self.method_list)) as executor:
            futures = {
                executor.submit(check_method, method): method 
                for method in self.method_list
            }
            
            for future in as_completed(futures):
                method, status_code, headers = future.result()
                
                status_desc = http.client.responses.get(status_code, 'Unknown Status Code')
                print(f"\n[bold yellow]Method: {method}[/bold yellow] | [bold magenta]Status: {status_code} {status_desc}[/bold magenta]")
                
                if 'error' in headers:
                    print(f"  [bold red]Error: {headers['error']}[/bold red]")
                else:
                    if headers:
                        print("  [bold white]Headers:[/bold white]")
                        for header_name, header_value in headers.items():
                            print(f"    {header_name}: {header_value}")

    def get_sni_info(self):
        if self.protocol != "https":
            return
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    sni_info = {
                        'version': ssock.version(),
                        'cipher': ssock.cipher(),
                        'cert': ssock.getpeercert()
                    }
                    
                    print(f"[bold white]SSL Version:[/bold white] {sni_info['version']}")
                    print(f"[bold white]Cipher Suite:[/bold white] {sni_info['cipher'][0]}")
                    print(f"[bold white]Cipher Bits:[/bold white] {sni_info['cipher'][1]}")
                    
                    cert = sni_info['cert']
                    
                    def parse_cert_field(field):
                        return {item[0]: item[1] if len(item) > 1 else '' for item in field}
                    
                    print(f"[bold white]Subject:[/bold white] {parse_cert_field(cert.get('subject', []))}")
                    print(f"[bold white]Issuer:[/bold white] {parse_cert_field(cert.get('issuer', []))}")
                    print(f"[bold white]Serial Number:[/bold white] {cert.get('serialNumber', 'N/A')}")
                    
        except Exception as e:
            print(f"[bold red] Error getting SSL info: {e}[/bold red]")

    def scan(self):

        if not self.get_ips():
            return
            
        self.get_cdn()
        self.get_http_info()
        self.get_sni_info()


def main():
    host = get_input("Enter host")
    protocol = get_input("Select protocol", "choice", choices=["http", "https"])
    available_methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]
    method_list = get_input(
        "Select HTTP method(s)",
        "choice",
        multiselect=True, 
        choices=available_methods,
        transformer=lambda result: ', '.join(result) if isinstance(result, list) else result
    )

    scanner = HostScanner(host, protocol, method_list)
    scanner.scan()
