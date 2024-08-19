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

    # 移除所有 root logger 的处理器
    # for handler in logging.getLogger().handlers:
    #     handler: logging
    #     if not handler.get_name():
    #         logging.getLogger().removeHandler(handler)
    @classmethod
    def set_root_logger_format(cls, filename=""):
        """设置 root logger"""
        _logging_filename = f"{cls._logging_filename}{filename}.log"
        _logging_filepath = os.path.join(os.path.dirname(__file__), _logging_filename)
        logging.basicConfig(level=logging.DEBUG,  # 默认logging的日志级别为warning，这里设置为debug
                            format='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d_%H:%M:%S',
                            # stream=sys.stdout,
                            # filename='my.log',
                            # filemode='a',
                            handlers=[
                                logging.FileHandler(f"{_logging_filepath}", encoding="UTF-8", mode='a'),  # 文件日志处理器
                                logging.StreamHandler(sys.stdout)  # 控制台日志处理器
                            ]
                            )
        logger = logging.getLogger()
        # 获取控制台日志处理器
        console_handler = logger.handlers[-1]
        # 创建控制台日志格式化器（包含颜色代码）
        console_handler.setFormatter(ColoredFormatter(
            fmt="{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}",
            datefmt="%Y-%m-%d_%H:%M:%S", style="{", defaults={'user': '', 'prefix': ''})
        )
        """
        # 换个新的日志文件名进行写入
        if filename != "":
            file_handler = logging.FileHandler(f"{cls._logging_filename}", encoding="UTF-8", mode='a')
            file_handler.setFormatter(logging.Formatter(
                fmt='[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d_%H:%M:%S'
            ))
            cls.logger.handlers[0] = file_handler
        """
        # cls.getLogger(logger_name="root")
        # cls(logger_name="root")

    @classmethod
    def getLogger(cls, logger_name="", logger_level=logging.DEBUG, filename=""):
        """eg: getLogger(10, "name", os.path.basename(__file__)).info(msg)"""
        # 根据name单独设置一个logger
        if logger_name != "":
            return cls(logger_name, logger_level, filename).logger
        if cls.logger is None:
            # 使用当前文件名获取一个logger
            logger_name = os.path.basename(__file__)
            cls.logger = cls(logger_name, logger_level, filename).logger
            # 不继承root logger，不保持不同库的logging之间的日志格式一致，这里的logger使用独立的自定义格式输出日志
            cls.logger.parent = None
        return cls.logger

    def __init__(self, logger_name="", logger_level=logging.DEBUG, filename=""):
        """在控制台打印日志和记录日志到文件"""
        logger_name = logger_name if re.search(".py$", logger_name) is None else f"{logger_name[0:-3]}"

        # 文件的命名,去掉.log
        filename = filename if re.search(".log$", filename) is None else f"_{filename[0:-4]}"
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

    MyLogging.getLogger("my", 10, filename="mylogging.py").warning("this is warning mylogging.py")
    logging.getLogger("mylogging").warning("this is warning...")
    logging.getLogger().warning("\n132")
