import logging
import os
import sys
import time

import utils.myutil

log_path_name = os.path.join(utils.myutil.get_project_path(), "logs", 'test-result_%s.log' % time.strftime("%Y-%m-%d"))
logging_format = "[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s"
log_date_format = "%Y-%m-%d_%H:%M:%S"


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

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
            record.msg = f"{color_codes.get(logging.ERROR)}{record.msg}{color_codes.get('nocolor')}"
            record.exc_text = f"{color_codes.get(logging.CRITICAL)}{record.exc_text}{color_codes.get('nocolor')}"
        return super().format(record)


# 设置 Root Logger 日志记录格式
logging.basicConfig(level=logging.INFO,
                    format=f'{logging_format}',
                    datefmt=f'{log_date_format}',
                    # stream=sys.stdout,
                    # filename='result.log',
                    # filemode='a',
                    handlers=[
                        logging.FileHandler(f"{log_path_name}", encoding="UTF-8", mode='a'),  # 文件日志处理器
                        logging.StreamHandler(sys.stdout),  # 控制台日志处理器
                    ]
                    )
# 获取控制台日志处理器
console_stream_handler = logging.getLogger().handlers[-1]
# 创建控制台日志格式化器（包含颜色代码）
console_stream_handler.setFormatter(ColoredFormatter(
    fmt=f'{logging_format}',
    datefmt=f'{log_date_format}'
))
logger = logging.getLogger()
