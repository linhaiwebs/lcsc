

import random
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from read_config import ReadConfig
import warnings
warnings.filterwarnings('ignore')


config = ReadConfig()


class Tools(object):
    """
    工具类
    """
    def __init__(self):
        self.ua = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.41",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        ]

    def random_ua(self):
        return random.choice(self.ua)

    @staticmethod
    def get_extra(url, headers, params, time_diff, res_status):
        return {'request_url': url, 'request_headers': headers,
                'request_params': params, 'time_diff': time_diff, 'res_status': res_status}

    @classmethod
    def get_email_setting(cls):
        send_email = config.get_email_setting()
        cls.from_addr = send_email.get('FROM_ADDR')
        cls.password = send_email.get('PASSWORD')
        cls.smtp_host = send_email.get('SMTP_HOST')
        cls.receive_list = send_email.get('RECEIVE_LIST')

    @staticmethod
    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def sent_email(self, message):
        self.get_email_setting()
        try:
            to_addr = self.receive_list
            to_addrs = to_addr.split(',')
            # 邮件对象
            msg = MIMEMultipart()
            # 收发件人
            msg['From'] = Tools.format_addr('spider <%s>' % self.from_addr)
            msg['To'] = to_addr
            # 邮件名称
            msg['Subject'] = Header('数据爬取报错邮件', 'utf-8').encode()
            main = f'<p>&emsp;{message}</p>'
            body = '<html><head>Dear all:</head><body>' + main + '</body></html>'
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            server = smtplib.SMTP_SSL(self.smtp_host, 465)  # Foxmail 邮箱服务器地址
            server.set_debuglevel(1)
            server.login(self.from_addr, self.password)  # 发件人邮箱地址， 密码
            server.sendmail(self.from_addr, to_addrs, msg.as_string())  # 发送指令
            server.quit()
        except SystemExit:
            msg = MIMEMultipart()
            msg['From'] = Tools.format_addr('服务器邮件脚本 <%s>' % self.from_addr)
            msg['To'] = Tools.format_addr('管理员 <%s>' % self.from_addr)
            msg['Subject'] = Header('邮件发送失败……', 'utf-8').encode()
            server = smtplib.SMTP_SSL(self.smtp_host, 465)
            server.set_debuglevel(1)
            server.login(self.from_addr, self.password)
            server.sendmail(self.from_addr, [self.from_addr], msg.as_string())
            server.quit()
