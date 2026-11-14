import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from importlib.machinery import SourceFileLoader
validator = SourceFileLoader('forge_validator', str(Path(__file__).resolve().parent.parent / 'scripts/bootstrap.py')).load_module()

class BootstrapTests(unittest.TestCase):
    def test_bootstrap_integrity(self):
        validator.validate()

if __name__ == '__main__':
    unittest.main()
