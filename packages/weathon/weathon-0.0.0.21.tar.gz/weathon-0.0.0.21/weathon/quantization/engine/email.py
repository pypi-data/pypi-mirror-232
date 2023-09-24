from queue import Queue, Empty
from threading import Thread
import smtplib
from email.message import EmailMessage
from weathon.quantization.base.engine import BaseEngine, EventEngine, MainEngine
from weathon.utils.constants import MailConfig

# 功能引擎

class EmailEngine(BaseEngine):
    """
    Provides email sending function.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super(EmailEngine, self).__init__(main_engine, event_engine, "email")

        self.thread: Thread = Thread(target=self.run)
        self.queue: Queue = Queue()
        self.active: bool = False

        self.email_config = MailConfig(receivers="16621660628@163.com")

        self.main_engine.send_email = self.send_email

    def send_email(self, subject: str, content: str, receiver: str = "") -> None:
        """"""
        # Start email engine when sending first email.
        if not self.active:
            self.start()

        # Use default receiver if not specified.
        if not receiver:
            receiver: str = self.email_config.receiver

        msg: EmailMessage = EmailMessage()
        msg["From"] = self.email_config.sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.set_content(content)

        self.queue.put(msg)

    def run(self) -> None:
        """"""
        while self.active:
            try:
                msg: EmailMessage = self.queue.get(block=True, timeout=1)

                with smtplib.SMTP_SSL(self.email_config.smtp_host, self.email_config.smtp_port) as smtp:
                    smtp.login(self.email_config.smtp_user, self.email_config.smtp_password)
                    smtp.send_message(msg)
            except Empty:
                pass

    def start(self) -> None:
        """"""
        self.active = True
        self.thread.start()

    def close(self) -> None:
        """"""
        if not self.active:
            return

        self.active = False
        self.thread.join()
