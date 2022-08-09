
import asyncio
import os
import queue
import re
import time
import json
import warnings
import random
import requests
from threading import Thread
from urllib.parse import unquote
from lxml import etree
from tqdm import tqdm
from db_model.db_lcsc import Electroncomponent, get_session, check_table_exist
from read_config import ReadConfig
from spiders.base import Base

warnings.filterwarnings("ignore")


logger = ReadConfig().get_logging(obj='get_data_log', type_='RecordLogger')
config = ReadConfig()


class LcscCrawler(Base):
    """
    获取数据，保存数据，发送数据
    """
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        self._set = set()
        self.success_num = 0
        self.fail_num = 0

    async def get_product_detail(self, product_id, cate_name):
        """
        获取元件数据，json接口
        :param product_id: 元件id
        :param cate_name: 类目名称
        :return: 元件数据 --> dict
        """
        url = "https://cart.szlcsc.com/check/status/jsonp"
        params = {
            "productId": product_id,
            # "callback": f"jQuery360027616383041218895_{int(time.time()*1000)}",
            "_": str(int(time.time()*1000))
        }
        res_text = await self.send_async_request(url=url, params=params, method='get')
        if not res_text:
            pro_ = {'product_id': product_id, 'cate_name': cate_name}
            logger.error(f"get_product_detail not exist res_text!! --> {pro_}")
            return {}
        __result = res_text.get('result', {})
        product_discount_price_list = __result.get('productDiscountPriceList', [])
        convesion_ratio = __result.get('convesionRatio', 1)
        price_spec = []
        for price in product_discount_price_list:
            price_spec.append({"MinValue": price.get('spNumber', 0) * convesion_ratio, "Price": price.get('price', 0)})
        if not price_spec:
            product_price_list = __result.get('productPriceList', [])
            for price1 in product_price_list:
                price_spec.append({"MinValue": price1.get('spNumber', 0) * convesion_ratio,
                                   "Price": price1.get('productPrice', 0)})

        detail_dict = {
            "Name": __result.get('productName'),
            "Category": cate_name,
            "Brand": __result.get('brandName'),
            "Model": __result.get('productModel'),
            "Code": __result.get('productCode'),
            "Encapsulating": __result.get('encapStandard'),
            "Unit": __result.get('productUnit'),
            "PriceSpec": price_spec,
        }
        return detail_dict

    async def get_html(self, product_id):
        """
        元件html的数据
        :param product_id: 元件id
        :return: 元件数据 --> dict | None
        """
        url = f"https://item.szlcsc.com/{product_id}.html"
        res_text = await self.send_async_request(url)
        if not res_text:
            logger.error(f"get_html not exist res_text!! --> product_id: {product_id}")
            return
        html = etree.HTML(res_text)
        package = html.xpath('//div[@class="product-brand-con"]/div[last()]/span[last()]/text()')
        package = package[0] if package else ''
        weight = html.xpath('//div[@class="product-brand-con"]/div[last()-1]/span[last()]/text()')
        weight = weight[0] if weight else ''
        # image_list = html.xpath('//div[@class="thum-cont"]/img/@src')
        # image_list = [i.replace('breviary', 'source') for i in image_list]
        params_list = []
        for param in html.xpath('//table[@class="param-body"]/tr'):
            name = param.xpath('td[1]/text()')
            value = param.xpath('td[2]/text()')
            if not name:
                continue
            params_list.append({'Name': name[0] if name else '', "Value": value[0] if value else ''})
        pdf_url = html.xpath('//div/a[@id="lookAllPdf"]/@href')
        if pdf_url:
            pdf_url = unquote(re.findall("\('(.*?)'", pdf_url[0])[0])
        else:
            annex_number = html.xpath('//div/a[@id="downloadFile"]/@param-click')
            annex_number = annex_number[0] if annex_number else ''
            pdf_url = self.get_pdf_url(annex_number)
        html_dict = {"Weight": weight, "Package": package, "AttributeList": params_list, "Pdf": pdf_url, 
                     "SourceUrl": f'https://item.szlcsc.com/{product_id}.html'}
        return html_dict

    async def get_pdf_url(self, annex_number):
        url = "https://so.szlcsc.com/product/showProductPDFAndPCBJsonp"
        params = {
            "annexNumber": annex_number,
            # "callback": "jQuery36008604012487045285_1657546152224",
            "_": str(int(time.time()*1000))
        }
        res_text = await self.send_async_request(url=url, params=params, method='get')
        file_list = res_text.get('fileList', [])
        base_url = 'https://atta.szlcsc.com'
        pdf_url = ''
        for file in file_list:
            pdf_ = file.get('annexUrl', '')
            url_sign = file.get('urlSign', '')
            pdf_url = base_url + pdf_ + url_sign
        return pdf_url

    @staticmethod
    async def save_to_mysql(result: dict):
        result = {key: str(value) for key, value in result.items()}
        try:
            with get_session() as s:
                s.bulk_insert_mappings(Electroncomponent, [result])
                s.commit()
            logger.info("save to mysql success!!!")
        except Exception as e:
            logger.error(f'save to mysql error: {e} --> {result}')

    @staticmethod
    def upload_to_server(result: dict):
        """
        上传服务器
        :param result:
        :return:
        """
        url = 'http://tool-api.qiancipai.com/api/task/addelectroncomponent'
        response = requests.post(url=url, json=result)
        res_json = json.loads(response.text)
        if res_json.get('code') != 0:
            logger.info(f"upload to server fail --> {result}")
        logger.info("upload to server success!!!")

    def record_product_id(self, pro_: dict, state: str = 'success'):
        save_path = self.config.get_save_path
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        result = json.dumps(pro_)
        save_file = os.path.join(save_path, f'{state}_product_id.json')
        with open(save_file, 'a', encoding='utf-8') as f:
            f.write(result + '\n')
        logger.info(f"save to {state}_json success!!!")

    async def deal_result(self, cate_p: dict):
        try:
            detail_dict = await self.get_product_detail(cate_p['product_id'], cate_p['cate_name'])
            html_dict = await self.get_html(cate_p['product_id'])
            detail_dict.update(html_dict)
            if not detail_dict:
                logger.error(f"get detail_dict fail --> {cate_p}")
                self.fail_num += 1
                logger.error(f"fail total num: {self.fail_num} --> {cate_p}")
                return
            if self.config.save_to_database:
                await LcscCrawler.save_to_mysql(detail_dict)
            elif self.config.upload_to_server:
                # LcscCrawler.upload_to_server(detail_dict)
                self.success_num += 1
                logger.info(f"success total num: {self.success_num} --> {cate_p}")
            else:
                self.fail_num += 1
                self.record_product_id(cate_p, state='fail')
                logger.error(f"fail total num: {self.fail_num} --> {cate_p}")
                logger.error(f"settings error --> {detail_dict}")
            await asyncio.sleep(random.uniform(self.request_time_sleep, self.request_time_sleep + 3))
            self.record_product_id(cate_p)
            return
        except Exception as e:
            self.fail_num += 1
            self.record_product_id(cate_p, state='fail')
            logger.error(f"fail total num: {self.fail_num} --> {cate_p}")
            logger.error(f"deal result error --> {e}")


def consumer():
    """消费者"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    save_path = os.path.abspath(config.get_save_path)
    save_file = os.path.join(save_path, 'lcsc_product_id.json')
    f = open(save_file, 'r', encoding='utf-8')
    try:
        line = f.readline()
        lc = LcscCrawler()
        while line:
            line_num = 0
            line_list = []
            while line_num < 20:
                line = line.replace('\n', '')
                line = json.loads(line, strict=False)
                line_list.append(line)
                line = f.readline()
                line_num += 1
                if not line:
                    break
            task_c = []
            for pro in line_list:
                task_c.append(asyncio.ensure_future(lc.deal_result(pro)))

            loop.run_until_complete(asyncio.gather(*task_c))
            if not line:
                break
        f.close()
    except Exception as e:
        logger.error(f"consumer error: {e}")
        f.close()
            # if self.q.empty():
            #     logger.info('queue is empty sleep 60s')
            #     time.sleep(60)

    # def run(self):
    #     """
    #     生产者获取元件id --> queue队列通信，set对元件id去重 --> 消费者获取数据上传
    #     :return:
    #     """
    #     if self.config.save_to_database:
    #         check_table_exist(Electroncomponent.__tablename__)
    #     logger.info("start crawl data!!!")
    #     p = Thread(target=self.producer)
    #     c = Thread(target=self.consumer)
    #     p.start()
    #     c.start()
    #     c.join()
    #     p.join()


# if __name__ == '__main__':
#     time_start = time.time()
#     consumer()
#     print(f'总耗时：{time.time() - time.time()} s')
