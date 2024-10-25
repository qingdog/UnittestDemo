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


def http_to_https(file_name: str, encoding="utf-8", re_remove_line=".+XTestRunner.+"):
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            # modified_line = line.replace('http://', 'https://')
            # 更换cdn
            # new_content = re.sub(r'http://img.itest.info/', r'https://seldom.pages.dev/', line)
            # new_content = re.sub(r'http(s)?://img.itest.info/', r'https://cdn.jsdelivr.net/gh/qingdog/cdn/seldom/', line)
            new_line = re.sub(r'^ *(<script src="http|<link rel="stylesheet" href="http)://', r"\1s://", line)

            new_content = re.sub(rf'{re_remove_line}', r"", new_line)
            write_file.write(new_content)

    os.replace(f'{file_name}.tmp', file_name)


# 失败替换为成功
def html_line_to_new_line(file_name: str, encoding="utf-8", re_line="失败([\u4e00-\u9f85]*)", re_new_line="成功~\\1",
                          count=0):
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            new_content = re.sub(rf'{re_line}', rf"{re_new_line}", line)
            write_file.write(new_content)

    os.replace(f'{file_name}.tmp', file_name)


# https://github.com/houtianze/bypy/pull/576/commits/dc23a7c68181e39cb890e0550ae390848c75c3e7
def baidu_slice_encrypt(md5str):
    """上传百度网盘资源的MD5切片非可逆函数"""
    if len(md5str) != 32:
        return md5str
    for i in range(0, 32):
        v = int(md5str[i], 16)
        if v < 0 or v > 16:
            return md5str
    md5str = md5str[8:16] + md5str[0:8] + md5str[24:32] + md5str[16:24]
    encryptstr = ""
    for e in range(0, len(md5str)):
        encryptstr += hex(int(md5str[e], 16) ^ 15 & e)[2:3]
    return encryptstr[0:9] + chr(ord("g") + int(encryptstr[9], 16)) + encryptstr[10:]


if __name__ == '__main__':
    # sample_list = ["企业无严重违法", "企业教育经费用支出（万元）", "场地面积（m2）", ]
    sample_list = "企业无严重违法"
    reversed_list = sample_list[::-1]
    print(reversed_list)

    print(baidu_slice_encrypt("697914dfbf71fcb1040647760a0fb722"))
    # http_to_https("../reports/result-20240807.html")
