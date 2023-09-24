import requests
from weathon.dl.utils.constants import BARK_WEBHOOK_URL
import os
from typing import List
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from weathon.utils.constants import MailConfig


class Notify:
    BARK: str = "bark"
    EMAIL: str = "email"

    def send_message(self, title: str = "", description: str = "", content: str = "", app_type: str = "bark"):
        if app_type == self.BARK:
            self._bark_message(title=title, description=description, content=content, webhook_url=BARK_WEBHOOK_URL)

    def _bark_message(self, title: str = "", description: str = "", content: str = "", webhook_url=BARK_WEBHOOK_URL):
        if webhook_url:
            try:
                data = {
                    "title": title,
                    "description": description,
                    "content": content,
                }
                res = requests.post(url=webhook_url, json=data)
                if res.status_code != 200:
                    print(f'response code {res.status_code}! , Failed to send message.')
            except Exception as e:
                print(f'Failed to send message.{e.args}')

    def send_email(self, receivers: List[str] = ['16621660628@163.com'], subject: str = "", content: str = "",
                   filenames: List[str] = None):
        """
        发送邮件
        Args:
            to_users: 收件人， 多个收件人用英文分号进行分割
            subject: 邮件主题
            content: 邮件正文内容
            filenames: 附件，要发送的文件路径
        Returns:

        Example:
            send_email(receivers=["16621660628@163.com"], subject="邮件测试", content="this is a test")
        """
        mail_config = MailConfig(receivers=receivers)

        email = MIMEMultipart()
        email['From'] = mail_config.sender
        email['To'] = mail_config.receivers
        email['Subject'] = subject

        message = MIMEText(content)
        email.attach(message)

        for filename in filenames or []:
            display_filename = os.path.basename(filename)
            fp = open(filename, 'rb')
            attachment = MIMEApplication(fp.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', display_filename))
            email.attach(attachment)
            fp.close()

        smtp = smtplib.SMTP_SSL(mail_config.smtp_host,
                                mail_config.smtp_port)  # 创建SMTP_SSL对象(连接邮件服务器),邮件服务器域名(自行修改),邮件服务端口(通常是465)
        smtp.login(mail_config.sender, mail_config.smtp_password)  # 通过用户名和授权码进行登录
        smtp.sendmail(mail_config.sender, receivers, email.as_string())  # 发送邮件(发件人，收件人，邮件内容)
        smtp.close()
