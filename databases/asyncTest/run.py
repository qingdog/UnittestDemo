import unittest
from test_async_demo import TestDemo
from test_no_async import TestNoAsync

if __name__ == '__main__':
    # cases = unittest.defaultTestLoader.discover(".", pattern='test*.py')
    # unittest.TextTestRunner().run(cases)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNoAsync)
    runner = unittest.TextTestRunner()
    runner.run(suite)
