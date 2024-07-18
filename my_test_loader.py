import unittest
from collections.abc import Sequence


class MyTestLoader(unittest.TestLoader):
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


class A(unittest.TestCase):
    def test2_get_name(self):
        print("a...")
        return None

    def test1_get_name(self):
        print("a...")


# 兼容 python -m unittest loader.py
def load_tests(test_loader, test_suite, pattern):
    main()
    return test_suite


def main():
    print(A.__dict__)
    print(A.__dict__.keys())
    keys = A.__dict__.keys()
    print(list(keys))
    print(dir(A))
    print(A().test2_get_name())

    l1 = ['test_first1234567892', 'test_second12310', 'test_second12346578987651', 'test_third123456789103']
    l2 = ['__module__', '__annotations__', 'setUpClass', 'test_second12346578987651', 'test_second12310',
          'test_first1234567892', 'test_third123456789103', '__doc__']
    l1.sort(key=l2.index)
    print(l2.index)
    print(l1)

    print()

    print(MyTestLoader.getTestCaseNames(MyTestLoader(), testcase_class=A))


if __name__ == '__main__':
    main()
