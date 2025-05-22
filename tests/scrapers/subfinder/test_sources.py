import unittest
import time
from bugscanx.modules.scrapers.subfinder.sources import (
    CrtshSource, HackertargetSource, RapidDnsSource, C99Source,
    AnubisDbSource, AlienVaultSource, CertSpotterSource
)


class TestSubfinderSources(unittest.TestCase):
    def setUp(self):
        self.test_domain = "jio.com"
        self.sources = {
            'crtsh': CrtshSource(),
            'hackertarget': HackertargetSource(),
            'rapiddns': RapidDnsSource(),
            'anubisdb': AnubisDbSource(),
            'alienvault': AlienVaultSource(),
            'certspotter': CertSpotterSource(),
            'c99': C99Source()
        }

    def test_individual_sources(self):
        for source_name, source in self.sources.items():
            print(f"\nTesting {source_name}...")
            try:
                start_time = time.time()
                subdomains = source.fetch(self.test_domain)
                end_time = time.time()
                execution_time = end_time - start_time
                
                print(f"Time taken: {execution_time:.2f} seconds")
                print(f"Found {len(subdomains)} subdomains")
                print("Sample subdomains:", list(subdomains)[:5])
                self.assertIsInstance(subdomains, set)
            except Exception as e:
                print(f"Error in {source_name}: {str(e)}")
                raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
