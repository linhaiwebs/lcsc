

import time
from spiders.lcsc.get_product_id import LcscProduct


if __name__ == '__main__':
    start_time = time.time()
    crawler = LcscProduct()
    crawler.producer()
    print(f'总耗时：{time.time() - time.time()} s')
