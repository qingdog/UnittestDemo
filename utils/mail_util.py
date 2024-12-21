#!/usr/bin/env python
# _*_ coding:utf-8 _*_
__author__ = 'YinJia'

import logging
import os
from email import encoders
from email.mime.base import MIMEBase

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Sequence


class EmailConfig:
    """发件人、收件人、smtp 主机、smtp 端口、smtp 用户名、smtp 密码、邮件主题、消息"""

    def __init__(self, from_addr: str, to_addrs: str | Sequence[str], smtp_login_user: str, smtp_login_password: str,
                 smtp_host: str, smtp_port: int = 25, subject: str = ""):
        self.subject = subject
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_login_user = smtp_login_user
        self.smtp_login_password = smtp_login_password


def send_mail(email_config: EmailConfig, email_content: str | bytes, email_content_subtype="plain", charset="utf-8", attachment_path=None):
    """
    发送HTML邮件
    :param email_config: 邮件配置类
    :param email_content: HTML邮件正文
    :param email_content_subtype: plain、html
    :param charset: utf-8、gbk
    :param attachment_path: 邮件的附件 默认为html邮件文件
    :return:
    """
    logging.info(f"向 {email_config.from_addr} 发送邮件中...")
    # 读取附件
    try:
        if attachment_path:
            with open(attachment_path, 'rb') as f:
                attachment_content = f.read()
        else:
            attachment_path = f"正文附件{".html" if email_content_subtype != "plain" else ".txt"}"
            attachment_content = email_content
    except FileNotFoundError:
        logging.error(f"附件文件 {attachment_path} 未找到")
        raise

    # 创建 MIMEBase 对象，并设置内容类型为 octet-stream
    attach_mime_base = MIMEBase('application', 'octet-stream')
    attach_mime_base.set_payload(attachment_content)
    # 用 base64 编码
    encoders.encode_base64(attach_mime_base)
    attach_mime_base.add_header("Content-Disposition", "attachment", filename=("gbk", "", os.path.basename(attachment_path)))

    # 创建邮件对象
    mime_multipart = MIMEMultipart('related')
    # 给邮件设置附件
    mime_multipart.attach(attach_mime_base)
    # 设置html邮件内容
    email_mime_text = MIMEText(email_content, email_content_subtype, charset)
    mime_multipart.attach(email_mime_text)

    mime_multipart['Subject'] = email_config.subject
    mime_multipart['from'] = email_config.from_addr
    mime_multipart['to'] = email_config.to_addrs

    try:
        '''smtp = smtplib.SMTP(email_config.smtp_host, email_config.smtp_port)
        smtp.connect()
        smtp.starttls()'''
        # 连接smtp服务端（使用 SMTP_SSL 进行加密连接）
        smtp_server = smtplib.SMTP_SSL(email_config.smtp_host, email_config.smtp_port)
        smtp_server.set_debuglevel(logging.getLogger().level == logging.DEBUG)  # 日志等级为DEBUG 则开启调试模式
        # 登录并发送邮件
        smtp_server.login(email_config.smtp_login_user, email_config.smtp_login_password)
        smtp_server.sendmail(email_config.from_addr, email_config.to_addrs, mime_multipart.as_string())
        smtp_server.quit()
        logging.info("邮件发送成功！")
    except Exception as e:
        raise e
