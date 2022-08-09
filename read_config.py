import os
import yaml
import logging
import logging.config
import datetime


class ReadConfig(object):
    """
    读取config
    """

    def __init__(self):
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前目录
        self.yaml_path = os.path.join(self.cur_path, "config.yaml")
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            self.config_dict = yaml.load(f, Loader=yaml.FullLoader)  # Loader：默认加载器禁止执行任意函数

    @property
    def get_concurrent_num(self):
        return self.config_dict.get('CONCURRENT_REQUESTS', 10)

    @property
    def get_request_sleep_time(self):
        return self.config_dict.get('REQUEST_SLEEP_TIME', 20)

    @property
    def upload_to_server(self):
        return self.config_dict.get('UPLOAD_TO_SERVER', False)

    @property
    def save_to_json(self):
        return self.config_dict.get('SAVE_TO_JSON_FILE', False)

    @property
    def get_save_path(self):
        return os.path.abspath(self.config_dict.get('SAVE_PATH'))

    @property
    def save_to_database(self):
        return self.config_dict.get('SAVE_TO_DATABASE', False)

    def get_mysql_settings(self):
        db_settings = self.config_dict.get('DATABASE_SETTING', {})
        mysql_conn = f"mysql+pymysql://{db_settings['DATABASE_USER']}:{db_settings['DATABASE_PASSWORD']}@{db_settings['DATABASE_HOST']}:{db_settings['DATABASE_PORT']}/{db_settings['DATABASE_DB']}?charset=utf8mb4"
        return mysql_conn

    @property
    def is_send_email(self):
        return self.config_dict.get('SENT_EMAIL', False)

    def get_email_setting(self):
        return self.config_dict.get('EMAIL_SETTING', {})

    def get_logging(self, obj, type_="FileLogger"):
        # day_ = datetime.datetime.now().strftime('%Y-%m-%d')
        # file_path = f'{self.cur_path}/logs/{day_}/{obj}/'
        # if not os.path.exists(file_path):
        #     os.makedirs(file_path)
        # log_con = os.path.join(self.cur_path, "log_config.yaml")
        # with open(log_con, 'r') as file:
        #     config = yaml.safe_load(file.read())
        # config["handlers"]["info_file_handler"]['filename'] = file_path + 'info.log'
        # config["handlers"]["error_file_handler"]['filename'] = file_path + 'error.log'
        # config["handlers"]["record_file_error_handler"]['filename'] = file_path + 'error.log'
        # config["handlers"]["record_file_info_handler"]['filename'] = file_path + 'info.log'
        # logging.config.dictConfig(config)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        log = logging.getLogger()
        return log
