import logging
import unittest
from test_async_demo import TestDemo
from test_no_async import TestNoAsync
import logs.color_root_logger

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logs.color_root_logger.logger.debug("开始执行异步测试用例...")

    # cases = unittest.defaultTestLoader.discover(".", pattern='test*.py')
    # unittest.TextTestRunner().run(cases)

    loader = unittest.TestLoader()
    # suite = loader.loadTestsFromTestCase(TestDemo)
    suite = loader.loadTestsFromTestCase(TestNoAsync)
    runner = unittest.TextTestRunner()
    runner.run(suite)
