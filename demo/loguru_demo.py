import os
import sys

import utils.myutil
from loguru import logger


class LoguruDemo:
    @logger.catch
    def my_function(self, x, y, z):
        # 发生错误？无论如何都会被捕获！
        return 1 / (x + y + z)


def loguru_test_log():
    logger.opt(record=True).info("显示来自记录的值（例如：{record[thread]}）")

    # logger.add(sys.stderr, format="{extra[utc]} {message}")
    context_logger = logger.bind(ip="192.168.0.1", user="someone")
    context_logger.info("轻松地为你的日志添加上下文")
    context_logger.bind(user="someone_else").info("内联绑定额外的属性")
    context_logger.info("使用 kwargs 在格式化时添加上下文：{user}", user="anybody")

    # For scripts
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} - {message}"},
            {"sink": "file.log", "serialize": True},
        ],
        "extra": {"user": "someone"}
    }
    logger.configure(**config)

    # For libraries, should be your library's `__name__`
    logger.disable(__name__)
    logger.info("无论是否添加了接收器，这条消息都不会显示")

    # In your application, enable the logger in the library
    print(__name__)
    logger.enable(__name__)
    logger.info("不过，这条消息会传播到接收器")

    raise RuntimeError("error...")


def main(file_log=True):
    # 移除默认的日志处理器。# 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
    logger.remove()
    # backtrace 确定异常跟踪是否应该延伸到捕获错误的点之外，以便于调试。
    # diagnose 确定变量值是否应在异常跟踪中显示。在生产环境中应将其设置为 False，以避免泄露敏感信息。
    logger.add(sys.stdout, colorize=True,
               format="<green>{time:YYYY-MM-dd HH:mm:ss}</green> - <cyan>{file}:{line} {function}</cyan> "
                      "<level>{level} {message} </level>", level="DEBUG", backtrace=False, diagnose=True)

    if not file_log: return
    # 在记录每条消息之前都会进行检查rotation。如果已经存在与要创建的文件同名的文件，则通过将日期附加到其基本名称来重命名现有文件，以防止文件覆盖。
    log_name = os.path.join(utils.myutil.get_project_path(), "logs", "info_{time:YYYYMM}.log")  # INFO、WARNING、ERROR 和 CRITICAL
    os.makedirs(os.path.dirname(log_name), exist_ok=True)  # 确保日志目录（如logs）存在
    logger.add(sink=log_name, level="INFO", rotation="100 MB", retention="1 month")
    logger.add(os.path.join(utils.myutil.get_project_path(), "logs", "error_{time:YYYYMM}.log"),
               level="ERROR", rotation="100 MB", retention="1 month")

    # logger.info("如果你正在使用 Python {}, 当然更推荐使用 {feature}!", 3.6, feature="f-strings")

    '''LoguruDemo().my_function(1, 2, -3)
    try:
        loguru_test_log()
    except Exception:
        logger.exception("异常")'''


if __name__ == '__main__':
    main(False)
    from pathlib import Path

    project_root = Path(__file__).parent.parent  # 假设脚本在项目的子文件夹中
    print(project_root)
