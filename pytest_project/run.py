import logging
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from utils import color_format_logging

if __name__ == '__main__':
    logger = logging.getLogger()
    log_format = "[%(asctime)s]-[%(filename)s:%(lineno)d]-[%(levelname)s]%(message)s"
    logger.addHandler(color_format_logging.create_file_handler("%(message)s"))
    logger.setLevel(logging.INFO)

    pytest_script = f"pytest --log-date-format=%Y-%m-%d_%H:%M:%S --log-format={log_format} --color=yes -vs --log-cli-level=debug ./"
    pytest_run_result = subprocess.Popen(pytest_script.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="UTF-8")


    def log_output(stream, log, log_level):
        """ 读取子进程的输出流并记录日志 """
        for line in stream:
            print(f"\033[34m{line}\033[0m" if log_level == logging.CRITICAL else line, end="")
            log.log(log_level, re.compile(r'\033\[[0-9;]*[mK]').sub('', line).rstrip('\n'))  # 去除ANSI颜色代码并记录日志


    # 使用线程池来管理stdout和stderr的读取
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 提交两个任务：分别处理stdout和stderr
        executor.submit(log_output, pytest_run_result.stdout, logger, logging.INFO)
        executor.submit(log_output, pytest_run_result.stderr, logger, logging.CRITICAL)

    pytest_run_result.wait()
