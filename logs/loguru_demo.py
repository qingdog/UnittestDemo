import logging
import os
import sys

import utils.myutil
from loguru import logger


class Demo:
    @logger.catch
    def my_function(self, x, y, z):
        # An error? It's caught anyway!
        return 1 / (x + y + z)


def main():
    logger.opt(record=True).info("Display values from the record (eg. {record[thread]})")

    # logger.add(sys.stderr, format="{extra[utc]} {message}")
    context_logger = logger.bind(ip="192.168.0.1", user="someone")
    context_logger.info("Contextualize your logger easily")
    context_logger.bind(user="someone_else").info("Inline binding of extra attribute")
    context_logger.info("Use kwargs to add context during formatting: {user}", user="anybody")

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
    logger.info("No matter added sinks, this message is not displayed")

    # In your application, enable the logger in the library
    print(__name__)
    logger.enable(__name__)
    logger.info("This message however is propagated to the sinks")

    raise RuntimeError("error...")


# logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
# handler_id = logger.add(sys.stderr, level="INFO") # 设置日志等级为DEBUG
if __name__ == '__main__':
    # 移除默认的日志处理器
    logger.remove()
    logger.add(sys.stdout, colorize=True,
               format="<green>{time:YYYY-MM-dd HH:mm:ss}</green> - <cyan>{file}:{line} {function}</cyan> "
                      "<level>{level} {message} </level>", level="DEBUG")

    # 在记录每条消息之前都会进行检查rotation。如果已经存在与要创建的文件同名的文件，则通过将日期附加到其基本名称来重命名现有文件，以防止文件覆盖。
    logger.add(os.path.join(utils.myutil.get_project_path(), "logs", "info_{time:YYYYMM}.log"),
               level="INFO", rotation="100 MB", retention="1 month")
    logger.add(os.path.join(utils.myutil.get_project_path(), "logs", "error_{time:YYYYMM}.log"),
               level="ERROR", rotation="100 MB", retention="1 month")

    logger.info("If you're using Python {}, prefer {feature} of course!", 3.6, feature="f-strings")
    Demo().my_function(1, 2, -3)

    try:
        main()
    except Exception:
        logger.exception("异常")
