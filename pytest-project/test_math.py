import logging
import time

import pytest


class TestMathOperations:
    def test_add(self):
        logging.info("test add.")
        print("#" * 100)
        assert 1 + 2 == 3

    def test_subtract(self):
        time.sleep(1)
        assert 5 - 3 == 2


if __name__ == '__main__':
    pytest.main(['-vs'])
