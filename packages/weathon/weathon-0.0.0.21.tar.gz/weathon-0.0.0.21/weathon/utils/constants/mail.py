# 邮件服务器设置
from dataclasses import dataclass
from typing import List


@dataclass
class MailConfig:
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_name: str = "188014193@qq.com"
    smtp_user: str = smtp_name
    smtp_password: str = "ruhmdvmegkncbgbg" # tsgnswracsujbifb

    sender: str = smtp_user
    receivers: List[str] = None

    
    def __post_init__(self):
        self.receivers = ",".join(self.receivers)


