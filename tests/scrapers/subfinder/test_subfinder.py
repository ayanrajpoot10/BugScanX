import os
import tempfile
import unittest
from bugscanx.modules.scrapers.subfinder.subfinder import SubFinder
from bugscanx.modules.scrapers.subfinder.sources import get_sources


class TestSubFinder(unittest.TestCase):
    def setUp(self):
        self.subfinder = SubFinder()
        self.test_domains = ["example.com", "google.com", "jio.com"]
        self.sources = get_sources()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_subdomains.txt")

    def test_full_scan(self):
        print("\nTesting full subdomain scan...")
        results = self.subfinder.run(self.test_domains, self.output_file, self.sources)
        
        print(f"\nTotal subdomains found: {len(results)}")
        print("Results per domain:")
        for domain in self.test_domains:
            domain_results = [s for s in results if s.endswith(domain)]
            print(f"{domain}: {len(domain_results)} subdomains")
            print("Sample subdomains:", domain_results[:5])

        self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file, 'r') as f:
            saved_results = f.read().splitlines()
        self.assertEqual(len(saved_results), len(results))

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        os.rmdir(self.temp_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
