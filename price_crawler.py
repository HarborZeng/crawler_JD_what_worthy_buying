import urllib.request
import json
import time
import random
import pymysql as pymysql


def get_product_price(skuid, url="https://p.3.cn/prices/mgets?skuIds="):
    price_json = urllib.request.urlopen(url + str(skuid))
    data = json.load(price_json)
    price = data[0]['p']
    return price
