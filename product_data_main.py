

import time
from spiders.lcsc.get_product_data import consumer


if __name__ == '__main__':
    start_time = time.time()
    consumer()
    print(f'总耗时：{time.time() - time.time()} s')
