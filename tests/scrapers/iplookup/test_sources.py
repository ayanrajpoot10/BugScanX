import unittest
import time
from bugscanx.modules.scrapers.iplookup.sources import (
    RapidDNSSource,
    YouGetSignalSource
)


class TestIPLookupSources(unittest.TestCase):
    def setUp(self):
        self.test_ip = "8.8.8.8"
        self.sources = {
            'rapiddns': RapidDNSSource(),
            'yougetsignal': YouGetSignalSource()
        }

    def test_individual_sources(self):
        for source_name, source in self.sources.items():
            print(f"\nTesting {source_name}...")
            try:
                start_time = time.time()
                domains = source.fetch(self.test_ip)
                end_time = time.time()
                execution_time = end_time - start_time
                
                print(f"Time taken: {execution_time:.2f} seconds")
                print(f"Found {len(domains)} domains")
                print("Sample domains:", list(domains)[:5])
                self.assertIsInstance(domains, set)
            except Exception as e:
                print(f"Error in {source_name}: {str(e)}")
                raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
