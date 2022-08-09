
import datetime
from tools.tool import Tools


if __name__ == '__main__':

    tool = Tools()

    text = f"test {datetime.datetime.now()}"
    tool.sent_email(text)
