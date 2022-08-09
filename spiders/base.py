import asyncio
import datetime
import json
import time
import aiohttp
import requests
from read_config import ReadConfig
from tools.tool import Tools
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_fixed


tools = Tools()
config = ReadConfig()


class APIException(Exception):
    def __init__(self, platform, url, code, message):
        self.platform = platform
        self.code = code
        self.message = message
        self.url = url

    def __str__(self):
        message = "\n异常平台：%s\n错误链接：%s\n错误码：%s\n错误消息：%s\n" % (self.platform, self.url, self.code, self.message)
        print(message)
        return message


def send_error_email(retry_state):
    ex = retry_state.outcome.exception()
    print("API异常----", datetime.datetime.now(), ex)
    message = "<p style='color:red'><B>lcsc 爬取异常</B></p >" + "<p>" + str(ex)
    if config.is_send_email:
        tools.sent_email(message)
    return


class Base(object):
    """
    基类
    """
    def __init__(self):
        self.config = ReadConfig()
        self.tools = Tools()
        self.logger = self.config.get_logging(obj='request')
        self.request_time_sleep = self.config.get_request_sleep_time
        self.headers = {
            "authority": "list.szlcsc.com",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://list.szlcsc.com",
            "pragma": "no-cache",
            "referer": "https://list.szlcsc.com/catalog/312.html",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        self.cookies = {
            "acw_tc": "b73d0e1716572570098427012e2b8aac40ed939622c04aff6eff0957b4",
            "acw_sc__v2": "62c7bc31057e2425dcdab8055cc1482abf492cc1",
            "SID": "e0639166-96cb-412f-a839-d45237e1c367",
            "SID.sig": "CGD89G2TupEtsNpNi7dEAQSTuZaBe_FUQ3-49461WY8",
            "cpx": "1",
            "guidePage": "true",
            "noLoginCustomerFlag": "bffeca7a2b1bbe2434c0",
            "noLoginCustomerFlag2": "845b4b1fd0450cae6b3e",
            "PRO_NEW_SID": "042a0ce1-f641-481c-889c-025cb85ff68b",
            "customer_info": "0-0-0-0",
            "computerKey": "e4c5a62d6fe6b103f425",
            "AGL_USER_ID": "4ad70b0f-db5f-406b-96b7-b5248d6b7cfc",
            "Qs_pv_290854": "1575151123038724400%2C1862394803334866000",
        }

    @retry(stop=stop_after_attempt(5), retry_error_callback=send_error_email, retry=retry_if_exception_type(APIException), wait=wait_fixed(2))
    async def send_async_request(self, url: str, params: dict = None, data: dict = None, json_: dict = None,
                                 method: str = "get", **kwargs):
        """
        异步获取数据
        :param json_:
        :param data:
        :param method: 请求方法
        :param url: 链接
        :param params: 所需参数
        :return: 返回请求结果 => dict|str
        """
        start = time.time()
        async with asyncio.Semaphore(self.config.get_concurrent_num):
            async with aiohttp.ClientSession() as session:
                try:
                    self.headers['user-agent'] = self.tools.random_ua()
                    response = await session.request(method=method, url=url, headers=self.headers, params=params,
                                                     data=data, json=json_, cookies=self.cookies, **kwargs)
                    res_text = await response.text()
                    if response.status != 200:
                        extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, response.status)
                        self.logger.error('error', extra=extra_)
                        raise APIException('lcsc', url, response.status, res_text)
                    # await asyncio.sleep(random.uniform(self.request_time_sleep, self.request_time_sleep + 3))
                    response.encoding = 'utf-8'
                    extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, response.status)
                    self.logger.info('ok', extra=extra_)
                    content_type = response.headers.get('Content-Type')
                    if 'json' in content_type:
                        res_text = res_text.replace('null', '').lstrip('(').rstrip(')')
                        data_json = json.loads(res_text, strict=False)
                        return data_json
                    else:
                        return res_text
                except Exception as e:
                    extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, response.status)
                    self.logger.error(e, extra=extra_)

    @retry(stop=stop_after_attempt(5), retry_error_callback=send_error_email, retry=retry_if_exception_type(APIException), wait=wait_fixed(2))
    def send_sync_request(self, url: str, params: dict = None, data: dict = None, json_: dict = None,
                          method: str = "get", **kwargs):
        """
        同步获取数据
        :param json_:
        :param data:
        :param method: 请求方法
        :param url: 链接
        :param params: 所需参数
        :return: 返回请求结果 => dict|str
        """
        start = time.time()
        try:
            self.headers['user-agent'] = self.tools.random_ua()
            response = requests.request(method=method, url=url, headers=self.headers, params=params, data=data,
                                        json=json_, cookies=self.cookies, **kwargs)
            response.encoding = 'utf-8'
            res_text = response.text
            self.cookies.update(response.cookies.get_dict())
            if response.status_code != 200:
                extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, response.status_code)
                self.logger.error('error', extra=extra_)
                raise APIException('lcsc', url, response.status_code, res_text)
            content_type = response.headers.get('Content-Type')
            extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, response.status_code)
            self.logger.info('ok', extra=extra_)
            if 'json' in content_type:
                res_text = res_text.replace('null', '').lstrip('(').rstrip(')')
                data_json = json.loads(res_text, strict=False)
                return data_json
            else:
                return res_text
        except Exception as e:
            extra_ = self.tools.get_extra(url, self.headers, params, time.time() - start, 1)
            self.logger.error(e, extra=extra_)
