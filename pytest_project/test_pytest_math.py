import logging
import time

import pytest


class TestMathOperations:
    def test_2add(self):
        logging.info("test add.")
        print("#" * 100)
        assert 1 + 2 == 3

    def test_1subtract(self):
        time.sleep(1)
        print(1)
        assert 5 - 3 == 2


if __name__ == '__main__':
    pytest.main(['-vs'])
