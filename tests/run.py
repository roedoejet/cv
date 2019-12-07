import os
from unittest import TestLoader, TextTestRunner, TestSuite

from . import __file__ as TEST_DIR

# Unit tests
from test_urls import URLsTest

loader = TestLoader()

data_tests = [
    loader.loadTestsFromTestCase(test)
    for test in [URLsTest]
]

def run_tests(suite):
    if suite == 'dev':
        suite = TestSuite(data_tests)
    elif suite == 'prod' or suite == 'all':
        suite = loader.discover(os.path.dirname(TEST_DIR))
        
    runner = TextTestRunner(verbosity=3)
    runner.run(suite)

if __name__ == "__main__":
    run_tests('dev')