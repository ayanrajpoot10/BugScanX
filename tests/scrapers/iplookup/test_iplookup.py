import os
import tempfile
import unittest
from bugscanx.modules.scrapers.iplookup.iplookup import IPLookup
from bugscanx.modules.scrapers.iplookup.sources import get_scrapers


class TestIPLookup(unittest.TestCase):
    def setUp(self):
        self.iplookup = IPLookup()
        self.test_ips = ["8.8.8.8", "1.1.1.1", "142.250.190.78"]
        self.sources = get_scrapers()
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_domains.txt")

    def test_full_scan(self):
        print("\nTesting full IP lookup scan...")
        results = self.iplookup.run(self.test_ips, self.output_file, self.sources)
        
        print(f"\nTotal domains found: {len(results)}")
        print("Results per IP:")
        for ip in self.test_ips:
            print(f"{ip}: {self.iplookup.console.ip_stats.get(ip, 0)} domains")

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
