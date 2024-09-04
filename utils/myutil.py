import os
import re


def get_latest_file_path(dir_path):
    """
    获取指定目录下的生成的最新测试报告文件
    :param dir_path:生成报告的目录
    :return:返回文件的绝对路径
    """
    # 列出指定目录下的所有文件和目录名
    lists = os.listdir(dir_path)
    # 使用 自定义的key函数对文件列表进行排序，排序依据是 os.path.getmtime(path) 文件的最后修改时间（时间戳浮点数）
    # os.path.join(testreport, fn) 将目录名和文件名结合起来，形成完整的文件路径
    lists.sort(key=lambda filename: os.path.getmtime(os.path.join(dir_path, filename)))
    # 因为文件已经根据修改时间排序了，最新的文件会在列表的最后
    file_new = os.path.join(dir_path, lists[-1]) if len(lists) > 0 else None
    return file_new


def get_project_path():
    """获取项目路径"""
    project_path = os.path.join(
        os.path.dirname(__file__),
        "..",
    )
    return project_path


def http_to_https(file_name: str, encoding="utf-8"):
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            # modified_line = line.replace('http://', 'https://')
            new_content = re.sub(r'^ *(<script src="http|<link rel="stylesheet" href="http)://', r"\1s://", line)
            write_file.write(new_content)
    os.replace(f'{file_name}.tmp', file_name)


if __name__ == '__main__':
    sample_list = ["企业无严重违法", "企业教育经费用支出（万元）", "场地面积（m2）", ]
    reversed_list = sample_list[::-1]
    print(reversed_list)

    # http_to_https("../reports/result-20240807.html")


