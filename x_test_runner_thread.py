import seldom
from seldom.extend_lib import threads


@threads(2)  # !!!核心!!!! 设置线程数
def run_case(path: str):
    """
    根据传入的path执行用例
    """
    seldom.main(path=path, debug=False)


if __name__ == "__main__":
    # 定义3个测试文件，分别丢给3个线程执行。
    paths = [
        "./testcase/seldom_test_excel_api.py",
        "./testcase/test_dvd.py",
        # "./testcase/seldom_test_excel_api.py",
    ]
    for p in paths:
        run_case(p)
