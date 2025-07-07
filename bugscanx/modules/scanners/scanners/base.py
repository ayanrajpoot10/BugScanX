import ipaddress
import threading
from datetime import datetime

from .multithread import MultiThread


class BaseScanner(MultiThread):
    def __init__(self, is_cidr_input=False, cidr_ranges=None, output_file=None, **kwargs):
        super().__init__(**kwargs)
        self.is_cidr_input = is_cidr_input
        self.cidr_ranges = cidr_ranges or []
        self.output_file = output_file
        self._metadata_written = False
        self._file_lock = threading.Lock()

    def write_to_file(self, message):
        if self.output_file:
            with self._file_lock:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(message + '\n')

    def write_scan_metadata(self, filepath=None):
        if self.output_file and not self._metadata_written:
            with self._file_lock:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\nScan Time: {timestamp}\n")
                    if filepath:
                        f.write(f"File Scanned: {filepath}\n\n")
                    elif self.cidr_ranges:
                        f.write(f"CIDR Ranges: {', '.join(self.cidr_ranges)}\n\n")
                self._metadata_written = True

    def convert_host_port(self, host, port):
        return host + (f':{port}' if port not in ['80', '443'] else '')

    def get_url(self, host, port):
        port = str(port)
        protocol = 'https' if port == '443' else 'http'
        return f'{protocol}://{self.convert_host_port(host, port)}'

    def generate_cidr_hosts(self, cidr_ranges):
        for cidr in cidr_ranges:
            try:
                network = ipaddress.ip_network(cidr.strip(), strict=False)
                for ip in network.hosts():
                    yield str(ip)
            except ValueError:
                continue

    def get_total_cidr_hosts(self, cidr_ranges):
        total = 0
        for cidr in cidr_ranges:
            try:
                network = ipaddress.ip_network(cidr.strip(), strict=False)
                total += max(0, network.num_addresses - 2)
            except ValueError:
                continue
        return total

    def set_cidr_total(self, cidr_ranges):
        if self.is_cidr_input and cidr_ranges:
            total_hosts = self.get_total_cidr_hosts(cidr_ranges)
            port_multiplier = len(getattr(self, 'port_list', [1]))
            method_multiplier = len(getattr(self, 'method_list', [1]))
            self.set_total(total_hosts * port_multiplier * method_multiplier)

    def read_lines_count(self, filepath):
        line_count = 0
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                line_count += chunk.count(b'\n')
        return line_count

    def set_host_total(self, host_filepath):
        if host_filepath:
            total_hosts = self.read_lines_count(host_filepath)
            port_multiplier = len(getattr(self, 'port_list', [1]))
            method_multiplier = len(getattr(self, 'method_list', [1]))
            self.set_total(total_hosts * port_multiplier * method_multiplier)

    def generate_hosts_from_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    host = line.strip()
                    if host and not host.startswith(('#', '*')):
                        yield host
        except (FileNotFoundError, IOError, UnicodeDecodeError):
            return
