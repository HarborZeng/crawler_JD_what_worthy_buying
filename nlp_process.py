# coding=utf8
from numpy import unicode
from snownlp import SnowNLP
import pymysql as pymysql

from generate_wordcloud import draw_wordcloud


def read_data(skuid):
    # 获取数据库链接
    connection = pymysql.connect(host="localhost", user="root", passwd="123123", db="jd", port=3306,
                                 charset="utf8")
    try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建sql语句
            sql = "select * from jd.jd_items where jd.jd_items.skuid=%s"

            # 执行sql语句
            cursor.execute(sql, skuid)
            datas = cursor.fetchall()

            # 提交数据库
            connection.commit()
    finally:
        connection.close()
    return datas


def process(skuid):
    sum_sentiment = 0
    good_counter = 0
    just_so_so_counter = 0
    bad_counter = 0
    datas = read_data(skuid)

    comments_concat = ""
    for data in datas:
        # print(data[3])
        comments_concat += data[3].replace("hellip", "").replace("rdquo", "")
        sentiment = SnowNLP(data[3]).sentiments
        if sentiment > 0.8:
            good_counter += 1
        elif sentiment > 0.4:
            just_so_so_counter += 1
        else:
            bad_counter += 1
        sum_sentiment += sentiment
        # print(data[3])
        # print(sentiment)
    print("-----------------共计" + str(len(datas)) + "条评论------------------------")
    print("-----------------0.8以上" + str(good_counter) + "条评论------------------------")
    print("-----------------0.4-0.8  " + str(just_so_so_counter) + "条评论------------------------")
    print("-----------------0.4以下" + str(bad_counter) + "条评论------------------------")
    print("average sentiment is {}".format(sum_sentiment / len(datas)))

    draw_wordcloud(comments_concat)


process(7029545)
