# 引入相关模块
import time

import requests
from bs4 import BeautifulSoup

import pymysql as pymysql


def get_cellphones_list(page):
    header = {'Connection': 'close',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'}
    url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=" + str(
        page) + "&s=1&click=0"
    # 请求腾讯新闻的URL，获取其text文本
    wbdata = requests.get(url, headers=header).text
    # 对获取到的文本进行解析
    soup = BeautifulSoup(wbdata, 'lxml')
    # 从解析文件中通过select选择器定位指定的元素，返回一个列表
    cellphones = soup.select("li.gl-item > div.gl-i-wrap > div.p-img > a")
    cell_id = soup.find_all("li", class_="gl-item")

    ret_list = []
    # 对返回的列表进行遍历
    for (a_tags, li_tags) in zip(cellphones, cell_id):
        # 提取出标题和链接信息
        skuid = li_tags.get("data-sku")
        link = a_tags.get("href")
        url = "https://item.jd.com/" + str(skuid) + ".html"
        try:
            html = requests.get(url, headers=header).text
        except:
            print(time.asctime(time.localtime(time.time())) + ": Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print(time.asctime(time.localtime(time.time())) + ": Was a nice sleep, now let me continue...")
            continue
        product_name_whole_html = BeautifulSoup(html, 'lxml')
        # 从解析文件中通过select选择器定位指定的元素，返回一个列表
        product_name_html = product_name_whole_html.select("div.p-name > a")
        product_name = product_name_html[0].get_text()

        data = {
            'skuid': skuid,
            'product_name': product_name,
            'link': link
        }
        ret_list.append(data)
    return ret_list


def get_cellphone_list_whole_jd():
    i = 0
    while i < 200:
        list_data = get_cellphones_list(i)
        for p in list_data:
            # 获取数据库链接
            connection = pymysql.connect(host="localhost", user="root", passwd="123123", db="jd", port=3306,
                                         charset="utf8")
            try:
                # 获取会话指针
                with connection.cursor() as cursor:
                    # 创建sql语句
                    sql = "insert into jd.jd_product (`skuid`, `product_name`,`link`) values (%s,%s,%s)"

                    # 执行sql语句
                    cursor.execute(sql, (p["skuid"], p["product_name"], p["link"]))

                    # 提交数据库
                    connection.commit()
            finally:
                connection.close()
        print(time.asctime(time.localtime(time.time())) + ": 手机信息第" + str(i + 1) + "页已存入数据库")
        i += 1


def get_cellphone_list_from_db():
    datas = []
    # 获取数据库链接
    connection = pymysql.connect(host="localhost", user="root", passwd="123123", db="jd", port=3306,
                                 charset="utf8")
    try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建sql语句
            sql = "select * from jd.jd_product"

            # 执行sql语句
            cursor.execute(sql)
            datas = cursor.fetchall()

            # 提交数据库
            connection.commit()
    finally:
        connection.close()

    return datas
