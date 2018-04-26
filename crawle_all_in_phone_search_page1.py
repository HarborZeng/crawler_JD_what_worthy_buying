import time

from comments_crawler import crawl_main
from price_crawler import get_product_price
from product_crawler import get_cellphone_list_from_db

cellphones_list = get_cellphone_list_from_db()
for cellphone in cellphones_list:
    print("-----------------------------------------------------------")
    print(time.asctime(time.localtime(time.time())) + ": " + cellphone[1])
    print("price: {}".format(get_product_price(cellphone[0])))
    crawl_main(cellphone[0])
