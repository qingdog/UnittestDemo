import json
import os
import platform
import re
import shutil
import subprocess

from playwright.sync_api import Page, Browser

from utils import myutil

# 定义全局变量以便在多个测试中复用
browser: Browser
page: Page


def generate_environment_properties():
    """
    自动生成 environment.properties 文件并写入测试环境信息
    """
    pip_list = "pip list | findstr test" if platform.system() == "Windows" else "pip list | grep test"
    pip_test = subprocess.run(pip_list.split(" "), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    allure_version = subprocess.run(["allure", "--version"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    env_data = {
        "os_platform": platform.system(),
        "os_version": platform.release(),
        "python_version": platform.python_version(),
        pip_test.stdout: '',
        "allure_version": allure_version.stdout
    }

    result = subprocess.run(["pip", "show", 'playwright'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    playwright_result = re.search(r"(?<=Version: ).+(?=\n)", f"{result.stdout}")
    pytest_name = {"playwright": playwright_result.group()} if playwright_result else {}
    env_data.update(pytest_name)

    # os.makedirs(allure_results, exist_ok=True)  # 确保目录存在
    env_file_path = os.path.join(allure_results, "environment.properties")
    with open(env_file_path, "w") as env_file:
        for key, value in env_data.items():
            env_file.write(f"{key}={value}\n")  # 写入 environment.properties 文件


def update_history_trend_data(_build_order: int):
    """
    读取最新的趋势历史文件history-trend.json，更新 buildOrder构建次数、reportUrl报告跳转链接，并覆盖掉所有历史报告的history-trend.json
    :param _build_order: 报告构建次数
    :return: 报告链接
    """
    report_widgets_history_trend_json = os.path.join(allure_report_plus, str(_build_order), "widgets", "history-trend.json")
    # 读取最新的history-trend.json数据
    with open(report_widgets_history_trend_json) as f:
        history_trend: list = json.load(f)

    history_trend[0]["buildOrder"] = latest_history_trend_data[0]["buildOrder"] + 1 if latest_history_trend_data else 1  # 如果存在历史记录，则使用构建次数加1
    history_trend[0]["reportUrl"] = f"../{_build_order}/"  # 回退上一级目录设置报告链接 allure-report-plus/1/index.html

    # 将添加的两个字段写入到文件中。并覆盖掉所有历史报告的 history-trend.json，用于历史趋势图点击来回切换新老报告
    for i in range(1, _build_order + 1):
        old_history_trend_json = os.path.join(allure_report_plus, str(i), "widgets", "history-trend.json")
        with open(old_history_trend_json, "w+") as f: f.write(json.dumps(history_trend))
    return history_trend[0]["reportUrl"]


allure_report_plus = "allure-report-plus"


def get_latest_history_trend():
    """获取最新的历史趋势文件数据"""
    if not os.path.exists(allure_report_plus):
        return [], 1
    report_latest = myutil.get_latest_dir(allure_report_plus, r"\d+")
    report_widgets_history_trend_latest = os.path.join(report_latest, "widgets", "history-trend.json")

    with open(report_widgets_history_trend_latest) as f:
        latest_history_trend: list = json.load(f)
    latest_history_trend_build_order = 1
    if len(latest_history_trend) > 0 and "buildOrder" in latest_history_trend[0]:
        # build_order = len(latest_history_trend_data) + 1
        latest_history_trend_build_order = latest_history_trend[0]["buildOrder"] + 1
    return latest_history_trend, latest_history_trend_build_order


latest_history_trend_data, build_order = get_latest_history_trend()
# 根据构建次数创建文件夹记录每一次报告
allure_results = os.path.join("allure-results", str(build_order))
allure_report = os.path.join(allure_report_plus, str(build_order))


def main(clear_results=False, record_history=True, open_report=False, single_report=False):
    if single_report:
        if clear_results:
            for filename in os.listdir(os.path.join(os.getcwd(), allure_results)):
                if re.search(r"-((container|result)\.json|attachement\.)", filename): os.remove(os.path.join(allure_results, filename))
        os.system(f'pytest {"."} -s  --alluredir={allure_results}')
        os.system(f"allure generate {allure_results} -o {allure_report} --clean --single-file")
        return

    if clear_results: os.remove(allure_results)
    os.system(f'pytest {"."} -vs  --alluredir={allure_results}')

    if latest_history_trend_data:  # 复制上一个报告的 widgets/ 到新生成的测试结果的 history/
        latest_history = os.path.join(allure_report_plus, str(len(latest_history_trend_data)), "widgets", "history-trend.json")
        os.makedirs(os.path.join(allure_results, "history"), exist_ok=True)  # 创建history目录
        shutil.copy(latest_history, os.path.join(allure_results, "history", "history-trend.json"))

    os.system(f"allure generate {allure_results} -o {allure_report} --clean")

    # 生成报告后更新趋势图
    update_history_trend_data(build_order)
    if open_report: os.system(f"allure open {allure_report_plus} --host 127.0.0.1 --port 12320")


if __name__ == '__main__':
    main()
