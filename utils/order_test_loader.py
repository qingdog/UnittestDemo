import unittest
from collections.abc import Sequence


class OrderTestLoader(unittest.TestLoader):
    """重写获取测试用例的方法，不再按照方法名的字符排序来执行用例。自定义执行顺序，按照用例方法编写的顺序来执行。"""
    def getTestCaseNames(self, testcase_class):
        # 调用父类的获取“测试方法”函数
        test_names: Sequence[str] = super().getTestCaseNames(testcase_class)
        # 顺序获取测试用例类的所有方法，包括测试方法和非测试、类方法、内置属性等。再把字典的所有键转换成列表
        testcase_methods = list(testcase_class.__dict__.keys())

        # 确保test_names是一个列表
        if not isinstance(test_names, list):
            test_names = list(test_names)
        # 根据list的索引对testcase_methods进行排序
        test_names.sort(key=testcase_methods.index)
        # 返回测试方法名称
        return test_names


# 用于在 测试类 中单个文件执行测试
'''
def load_tests(test_loader, test_suite, pattern):
    """兼容 python -m unittest loader.py #避免__main__函数 在unittest模式下不会执行"""
    main()
    return test_suite'''


def main():
    class TestA(unittest.TestCase):
        """使用内部类避免识别成测试类，以测试模式执行"""

        def test2_get_name(self):
            print("aa...")
            return None

        def test1_get_name(self):
            print("a...")

    print(OrderTestLoader().getTestCaseNames(testcase_class=TestA))


if __name__ == '__main__':
    main()
