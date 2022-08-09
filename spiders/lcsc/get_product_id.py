

import re
import os
import math
import json
import time
from lxml import etree
from tqdm import tqdm
from spiders.base import Base
from read_config import ReadConfig

logger = ReadConfig().get_logging(obj='get_id_log', type_="RecordLogger")


class LcscProduct(Base):
    def __init__(self):
        super().__init__()
        self._set = set()

    def save_to_json(self, result: dict):
        save_path = self.config.get_save_path
        save_path = os.path.abspath(save_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_file = os.path.join(save_path, 'lcsc_product_id.json')
        result = json.dumps(result)
        with open(save_file, 'a', encoding='utf-8') as f:
            f.write(result + '\n')
        logger.info("save to json success!!!")

    def get_category(self):
        """
        获取类目
        :return: 返回类目列表 --> list
        """
        url = "https://www.szlcsc.com/"
        response_text = self.send_sync_request(url)
        html = etree.HTML(response_text)
        cate_list = []
        par_num = 0
        for ass in html.xpath('//div[contains(@class, "layout-catalogs")]/ul/li[@class="ass-list"]'):
            first_name = ass.xpath('a/text()')[0]
            cate_list.append({'cate_name': first_name, 'cate_id': 1, 'parent_id': 0})
            for sub in ass.xpath('div/dl/*'):
                cate_name = sub.xpath('a/text()')
                if not cate_name:
                    continue
                cate_name = cate_name[0].strip()
                href = sub.xpath('a/@href')
                cate_id = int(re.findall(r'/([0-9]+)\.html', href[0])[0]) if href else -1
                class_ = sub.xpath('a/@class')[0]
                if class_ == "two-catalog":
                    cate_list.append({'cate_name': cate_name, 'cate_id': cate_id, 'parent_id': 1})
                    par_num = cate_id
                elif class_ == "ellipsis":
                    cate_list.append({'cate_name': cate_name, 'cate_id': cate_id, 'parent_id': par_num})
                else:
                    continue
        save_file = os.path.join(self.config.get_save_path, 'category.json')
        with open(save_file, "w", encoding='utf-8') as f:
            json.dump(cate_list, f)
        return cate_list

    def get_product_id(self, cate_name: str, cate_id: str, page: int = 1):
        """
        获取商品id
        :param cate_name: 类目名称
        :param cate_id: 类目id
        :param page: 页码
        :return: (元件id, 类目名称)入队列 --> None|int
        """
        url = "https://list.szlcsc.com/products/list"
        data = {
            "catalogNodeId": cate_id,
            "pageNumber": str(page),
            "querySortBySign": "0",
            "showOutSockProduct": "1",
            "showDiscountProduct": "1",
            "queryBeginPrice": "",
            "queryEndPrice": "",
            "queryProductArrange": "",
            "queryProductGradePlateId": "",
            "queryProductTypeCode": "",
            "queryParameterValue": "",
            "queryProductStandard": "",
            "querySmtLabel": "",
            "queryReferenceEncap": "",
            "queryProductLabel": "",
            "lastParamName": "",
            "baseParameterCondition": "",
            "parameterCondition": ""
        }
        res_text = self.send_sync_request(url, data=data, method='post')
        cate_ = {'cate_id': cate_id, 'cate_name': cate_name, 'page': page}
        if not res_text:
            logger.error(f"get_product_id not exist res_text!! --> {cate_}")
            return
        if not isinstance(res_text, dict):
            logger.error(f'error request!! --> {cate_}')
            return
        product_list = res_text.get('productRecordList', [])
        for product in product_list:
            product_id = product.get('productId')
            if (product_id, cate_name) in self._set:
                pro = {'product_id': product_id, 'cate_name': cate_name}
                logger.error(f"exist product_id!! --> {pro}")
                continue
            product_dict = {"product_id": product_id, "cate_name": cate_name, "cate_id": cate_id}
            self.save_to_json(product_dict)
            self._set.add((product_id, cate_name))
            # self.q.put((product_id, cate_name))
            # if self.q.qsize() > 10000:
            #     time.sleep(600)

        if page == 1:
            total_count = res_text.get('totalCount', 0)
            page_num = math.ceil(int(total_count) / 30)
            return page_num
        return

    def producer(self):
        """生产者"""
        cate_list = self.get_category()
        cate_num = len(cate_list)
        for cate_index in tqdm(range(cate_num), desc="类目进度"):
            cate = cate_list[cate_index]
            if cate['cate_id'] <= 1:
                logger.info(f"first cate --> {cate}")
                continue
            elif cate['parent_id'] <= 1:
                logger.info(f"second cate --> {cate}")
                continue
            logger.info(f"start crawl {cate}")
            page_num = self.get_product_id(cate['cate_name'], cate['cate_id'])
            if not page_num:
                logger.error("get total page fail")
                continue
            logger.info(f"need crawl {page_num} page")
            for page in tqdm(range(2, page_num + 1), desc=f"总类目数 {cate_num} 现获取第 {cate_index + 1} 个类目 --> 页数进度"):
                self.get_product_id(cate['cate_name'], cate['cate_id'], page)
                time.sleep(0.2)

        return


# if __name__ == '__main__':
#     lp = LcscProduct()
#     lp.producer()
