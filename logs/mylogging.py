import logging
import os
import re
import sys
import time


class ColoredFormatter(logging.Formatter):
    """定义一个日志格式化器，添加颜色代码"""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *, defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record):
        # 定义颜色
        color_codes = {
            logging.DEBUG: '\033[94m',  # 蓝色
            logging.INFO: '\033[92m',  # 绿色
            logging.WARNING: '\033[93m',  # 黄色
            logging.ERROR: '\033[91m',  # 红色
            logging.CRITICAL: '\033[95m',  # 紫色
            "nocolor": '\033[0m'
        }
        # 添加颜色代码
        record.levelname = color_codes.get(record.levelno, '\033[0m') + record.levelname + '\033[0m'
        if record.levelno == logging.ERROR:
            record.msg = f"{color_codes.get(logging.CRITICAL)}{record.msg}{color_codes.get("nocolor")}"
            record.exc_text = f"{color_codes.get(logging.CRITICAL)}{record.exc_text}{color_codes.get("nocolor")}"
        return super().format(record)


class MyLogging:
    _logging_filename = time.strftime("%Y%m%d")
    logger: logging.Logger = None

    @classmethod
    def getLogger(cls, logger_name="", logger_level=logging.DEBUG, filename=""):
        """eg: getLogger(10, "name", os.path.basename(__file__)).info(msg)"""
        # 根据name单独设置一个logger
        if logger_name != "":
            return cls(logger_name, logger_level, filename).logger
        # 使用当前文件名获取一个logger
        if cls.logger is None:
            logger_name = os.path.basename(__file__)
            cls.logger = cls(logger_name, logger_level, filename).logger
            # 不继承root logger，无需保持一致，使用独立的自定义格式输出日志
            cls.logger.parent = None
        return cls.logger

    def __init__(self, logger_name="", logger_level=logging.DEBUG, filename=""):
        """在控制台打印日志和记录日志到文件"""
        # 文件的命名,去掉.py
        filename = filename if re.search(".py$", filename) is None else f"_{filename[0:-3]}"
        self._logging_filename = f"{self._logging_filename}{filename}.log"
        self._logging_filepath = os.path.join(os.path.dirname(__file__), self._logging_filename)

        """
        # 配置Root logger
        logging.basicConfig(
            level=logging.DEBUG, # 默认logging的日志级别为warning，这里设置为debug
            format='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d_%H:%M:%S',
            # ,filename="result.log"
            handlers=[
                logging.FileHandler(f"{self._logging_filename}", encoding="UTF-8", mode='a'),  # 文件日志处理器
                logging.StreamHandler(sys.stdout)  # 控制台日志处理器
            ]
        )
        # 换个新的日志文件名进行写入
        if filename != "":
            file_handler = logging.FileHandler(f"{self._logging_filename}", encoding="UTF-8", mode='a')
            file_handler.setFormatter(logging.Formatter(
                fmt='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d_%H:%M:%S'
            ))
            self._logger.handlers[0] = file_handler
        # 为控制台日志处理器设置彩色格式化器
        console_handler = self._logger.handlers[1]  # 获取控制台日志处理器
        console_handler.setFormatter(
            ColoredFormatter(fmt="[{asctime}] - [{filename}:{lineno}] {levelname} {message} {user}",
                             datefmt="%Y-%m-%d_%H:%M:%S", style="{", defaults={'user': 'anonymous'}))
        """

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logger_level)

        # 创建文件处理器并应用格式化器 创建文件日志格式化器（不包含颜色代码）
        file_handler = logging.FileHandler(f"{self._logging_filepath}", encoding="UTF-8", mode='a')
        file_handler.setFormatter(logging.Formatter(
            fmt="{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}",
            datefmt="%Y-%m-%d_%H:%M:%S", style="{", defaults={'user': '', 'prefix': ''})
        )

        # 创建控制台处理器并应用格式化器 创建控制台日志格式化器（包含颜色代码）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(
            fmt="{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}",
            datefmt="%Y-%m-%d_%H:%M:%S", style="{", defaults={'user': '', 'prefix': ''})
        )

        # 添加处理器到日志器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


if __name__ == '__main__':
    # 测试日志输出
    mylogger = MyLogging.getLogger()
    #
    mylogger.debug("这是一个DEBUG级别的日志", extra={"prefix": "\n"})
    mylogger.info("这是一个INFO级别的日志", extra={"user": "zhang"})
    mylogger.warning("这是一个WARNING级别的日志")
    mylogger.error("这是一个ERROR级别的日志", exc_info=True)

    # mylogger2 = MyLogging.getLogger()
    # mylogger2.setLevel(logging.WARNING)
    # mylogger2.error("mylogger2", exc_info=True)
    # mylogger2.critical("mylogger2")

    MyLogging.getLogger(10, "my", filename="mylogging.py").warning("this is warning mylogging.py")
    logging.getLogger("mylogging.py2").warning("this is warning...")
    logging.getLogger().warning("\n132")
