import logging
import re
import subprocess

from utils import color_format_logging

if __name__ == '__main__':
    logger = logging.getLogger()
    log_format = "[%(asctime)s]-[%(filename)s:%(lineno)d]-[%(levelname)s]%(message)s"
    pytest_script = f"pytest --log-date-format=%Y-%m-%d_%H:%M:%S --log-format={log_format} --color=yes -vs --log-cli-level=INFO ./"
    pytest_run_result = subprocess.Popen(pytest_script.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="UTF-8")
    logger.addHandler(color_format_logging.create_file_handler("%(message)s"))
    logger.setLevel(logging.INFO)

    for line in pytest_run_result.stdout:
        print(line, end="")
        # 记录日志：ANSI转义序列匹配去除颜色代码
        logger.info(re.compile(r'\033\[[0-9;]*[mK]').sub('', line).rstrip('\n'))
    for line in pytest_run_result.stderr:
        print(line, end="")
        logger.critical(re.compile(r'\033\[[0-9;]*[mK]').sub('', line).rstrip('\n'))
    pytest_run_result.wait()
