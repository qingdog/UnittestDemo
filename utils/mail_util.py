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


def send_mail(html_email_file_path, smtp_config, attachment=None):
    logging.info(f"向 {smtp_config['email_recipient']} 发送邮件中...")
    """
    定义发送邮件
    :param html_email_file_path: html邮件文件路径
    :param smtp_config: 邮件配置
    :param attachment: 邮件的附件 默认为html邮件文件
    :return:
    """
    # 读取邮件内容
    with open(html_email_file_path, 'rb') as f:
        email_str = f.read().decode("UTF-8")

    # 读取附件
    attachment = html_email_file_path if attachment is None else attachment
    with open(attachment, 'rb') as f:
        attachment_str = f.read()

    # 创建 MIMEBase 对象，并设置内容类型为 octet-stream
    attach_mime_base = MIMEBase('application', 'octet-stream')
    attach_mime_base.set_payload(attachment_str)
    # 用 base64 编码
    encoders.encode_base64(attach_mime_base)
    attach_mime_base.add_header("Content-Disposition", "attachment", filename=("gbk", "", os.path.basename(attachment)))

    # 创建邮件对象
    mime_multipart = MIMEMultipart('related')
    # 给邮件设置附件
    mime_multipart.attach(attach_mime_base)
    # 设置html邮件内容
    email_mime_text = MIMEText(email_str, 'html', 'utf-8')
    mime_multipart.attach(email_mime_text)
    # 邮件主题、发件人、收件人
    mime_multipart['Subject'] = smtp_config["subject"]
    mime_multipart['from'] = smtp_config["email_sender"]
    mime_multipart['to'] = smtp_config["email_recipient"]

    try:
        # 连接smtp服务端
        smtp = smtplib.SMTP(smtp_config["smtp_host"], smtp_config["port"])
        # server.connect()
        # 日志等级为DEBUG 则开启调试模式
        smtp.set_debuglevel(logging.getLogger().level == logging.DEBUG)
        smtp.starttls()
        smtp.login(smtp_config["user"], smtp_config["password"])
        # 发送邮件
        smtp.sendmail(smtp_config["email_sender"], smtp_config["email_recipient"], mime_multipart.as_string())
        smtp.quit()
        logging.info("邮件发送成功！")
    except Exception as e:
        raise e
