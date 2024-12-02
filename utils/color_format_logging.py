import logging
import os
import sys
import time


class ColoredFormatter(logging.Formatter):
    """定义一个日志格式化器，添加颜色代码"""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *, defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record):
        color_codes = {
            logging.DEBUG: '\033[94m',  # 蓝色
            logging.INFO: '\033[92m',  # 绿色
            logging.WARNING: '\033[93m',  # 黄色
            logging.ERROR: '\033[91m',  # 红色
            logging.CRITICAL: '\033[95m',  # 紫色
            "nocolor": '\033[0m'
        }
        # critical级别输出紫色信息 error级别输出红色信息
        record.levelname = color_codes.get(record.levelno, '\033[0m') + record.levelname + '\033[0m'
        if record.levelno == logging.CRITICAL:
            record.msg = f"{color_codes.get(logging.CRITICAL)}{record.msg}{color_codes.get("nocolor")}"
            record.exc_text = f"{color_codes.get(logging.CRITICAL)}{record.exc_text}{color_codes.get("nocolor")}"
        elif record.levelno == logging.ERROR:
            record.exc_text = f"{color_codes.get(logging.ERROR)}{record.exc_text}{color_codes.get("nocolor")}"
        return super().format(record)

log_dir = "logs"  # 日志目录
log_path_name = os.path.join(log_dir, f'{time.strftime("%Y%m%d")}.log')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # 创建目录
logging_format = "{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}"
log_date_format = "%Y-%m-%d_%H:%M:%S"

is_root_logger = len(logging.getLogger().handlers) == 0
is_file_handler = False
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        is_file_handler = True
    elif isinstance(handler, logging.StreamHandler):
        stream = handler.stream
        # console_stream_handler = logging.getLogger().handlers[-1]
        # 设置控制台日志格式化器（包含颜色代码）
        handler.setFormatter(ColoredFormatter(fmt=f'{logging_format}', datefmt=f'{log_date_format}', style="{", defaults={'user': '', 'prefix': ''}))
        if hasattr(stream, "name") and stream.name == '<stderr>':
            is_root_logger = True
            # break

if is_root_logger and len(logging.getLogger().handlers) <= 1:
    '''logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s', datefmt=f"%Y-%m-%d_%H:%M:%S",
                        handlers=[logging.FileHandler(f"{time.strftime("%Y-%m-%d")}.log", encoding="UTF-8", mode='a'), logging.StreamHandler(sys.stdout)])'''
    # 创建文件处理器并应用格式化器 创建文件日志格式化器（不包含颜色代码）
    file_handler = logging.FileHandler(f"{log_path_name}", encoding="UTF-8", mode='a')
    file_handler.setFormatter(logging.Formatter(fmt=f"{logging_format}", datefmt=f"{log_date_format}", style="{", defaults={'user': '', 'prefix': ''}))
    # 创建控制台处理器并应用格式化器 创建控制台日志格式化器（包含颜色代码）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(fmt=f"{logging_format}", datefmt=f"{log_date_format}", style="{", defaults={'user': '', 'prefix': ''}))
    # 添加处理器到日志器
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)
elif not is_file_handler:
    file_handler = logging.FileHandler(f"{log_path_name}", encoding="UTF-8", mode='a')
    file_handler.setFormatter(logging.Formatter(fmt=f"{logging_format}", datefmt=f"{log_date_format}", style="{", defaults={'user': '', 'prefix': ''}))
    logging.getLogger().addHandler(file_handler)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("先换行再输出DEBUG级别的日志", extra={"prefix": "\n"})
    logging.info("这是一个INFO级别的日志", extra={"user": "lucy"})
    logging.warning("\n这是一个WARNING级别的日志")
    logging.error("这是一个ERROR级别的日志", exc_info=True)
    logging.critical("这是一个CRITICAL级别的日志", exc_info=False)

    # 不继承root logger，不保持不同库的logging之间的日志格式一致，这里的logger使用独立的自定义格式输出日志
    logging.getLogger("mylogger").parent = None
    logging.getLogger("mylogger").warning("this is mylogger")
