from snownlp import SnowNLP
import pymysql as pymysql


def read_data():
    datas = []
    # 获取数据库链接
    connection = pymysql.connect(host="localhost", user="root", passwd="123123", db="jd", port=3306,
                                 charset="utf8")
    try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建sql语句
            sql = "select * from `jd_items` where jd.jd_items.skuid='7029545'"

            # 执行sql语句
            cursor.execute(sql)
            datas = cursor.fetchall()

            # 提交数据库
            connection.commit()
    finally:
        connection.close()
    return datas


def process():
    sum_sentiment = 0
    datas = read_data()
    for data in datas:
        sentiment = SnowNLP(data[3]).sentiments
        sum_sentiment += sentiment
        print(data[3])
        print(sentiment)
        print("-----------------------------------------")
    print("average sentiment is {}".format(sum_sentiment / len(datas)))


process()
