# 问题陈述

近年来，网上购物已经越来越流行，人们对于评论一个商品的行为习惯也多多少少受到商家的影响。

![好评请求](https://ws1.sinaimg.cn/large/bd61005egy1g0cw5pteqej20qt0b0n5t.jpg)

类似于这样的好评请求，好心的消费者由于见惯了，渐渐的就形成了好评的习惯。一味好评，会拉高商品的好评率，但是这对于新客户来说是非常具有误导性的，可能会让他们买了不好的产品。
京东的评价机制，没有评价的话，默认好评，结果不显示。

![默认好评](https://ws1.sinaimg.cn/large/bd61005egy1g0cw5zipsgj20ad04bglh.jpg)

有些顾客即使说出了差评，但是在打分上还是会给5星好评。

![评分评价不一致](https://ws1.sinaimg.cn/large/bd61005egy1g0cw69547vj20da043weh.jpg)

我们迫切的需要一款可以查明真实评价的渠道。

# 需要的信息

京东商品爬取，需要以下信息，①商品的名称；②商品的价格；③商品的评论；④商品的好评率、中评率和差评率。

接口描述 | URL | 格式 | 备注
------- | ------- | ------- | -------
抓取价格 | <https://p.3.cn/prices/mgets?skuIds={skuid}> | json | skuid是商品的id，也就是<https://item.jd.com/7029545.html> 商品网址的数字部分 
抓取名称 | <https://item.jd.com/{skuid}.html> | html | skuid是商品的id，也就是<https://item.jd.com/7029545.html> 商品网址的数字部分 
抓取评论 | <https://club.jd.com/comment/productPageComments.action?productId={skuid}&score=0&sortType=6&page={i}&pageSize=10&isShadowSku=0&fold=1> | json | skuid是商品的id，也就是<https://item.jd.com/7029545.html> 商品网址的数字部分;i是评论的页数，从零开始递增 

# 爬虫实现

## 爬取所有商品的基本信息

按照关键字搜索特定商品，或直接爬取https://www.jd.com/allSort.aspx 

```python
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
```

![爬取所有商品的基本信息的流程图](https://ws1.sinaimg.cn/large/bd61005egy1g0cw7n6vkij20x00wimxw.jpg){% asset_img mysql数据库.png mysql数据库 %}

![](https://ws1.sinaimg.cn/large/bd61005egy1g0cw8a849vj214v0szq6b.jpg)

## 爬取某商品所有评论

![爬取某商品所有评论的流程图](https://ws1.sinaimg.cn/large/bd61005egy1g0cw8j3y5nj20p60w1jrz.jpg)

为保证爬取顺利，开启三个ip进行爬取：

```python
domains = ["http://jdapi.tellyouwhat.cn", "https://club.jd.com","http://jdapi2.tellyouwhat.cn"]
```

每次从中任取一个域名进行组合

```python
def crawlProductComment(url, skuid):
    # 读取原始数据(注意选择gbk编码方式)
    try:
        html = urllib.request.urlopen(url).read().decode('gbk', 'ignore')
    except Exception:
        return -1

    data = json.loads(html)

    if len(data['comments']) == 0:
        print(time.asctime(time.localtime(time.time())) + "\nSeems no more data to crawl")
        return -1

    for comment in data['comments']:
        product_name = comment['referenceName']
        comment_time = comment['creationTime']
        content = comment['content']
        # 数据库操作
        # 获取数据库链接
        connection = pymysql.connect(host="localhost", user="root", passwd="123123", db="jd", port=3306, charset="utf8")
        try:
            # 获取会话指针
            with connection.cursor() as cursor:
                # 创建sql语句
                sql = "insert into jd.jd_items (`skuid`, `productName`,`commentTime`,`content`) values (%s,%s,%s,%s)"
                # 执行sql语句
                cursor.execute(sql, (skuid, product_name, comment_time, content))

                # 提交数据库
                connection.commit()
        finally:
            connection.close()
    return 1
```

![爬评论的过程](https://ws1.sinaimg.cn/large/bd61005egy1g0cw92xygfj20pf0hnmy7.jpg)
![爬评论的结果](https://ws1.sinaimg.cn/large/bd61005egy1g0cw936648j21c30ix44r.jpg)

## 爬取某商品的价格

```python
def get_product_price(skuid, url="https://p.3.cn/prices/mgets?skuIds="):
    price_json = urllib.request.urlopen(url + str(skuid))
    data = json.load(price_json)
    price = data[0]['p']
    return price
```

## 对评论进行情感分析

```python
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
```

评论性质 | 情感分析得分区间
-----|---------
好评 | 0.8~1.0
中评 | 0.4~0.8
差评 | 0~0.4

![情感分析结果](https://ws1.sinaimg.cn/large/bd61005egy1g0cw9hdsfsj20us0l9mym.jpg)

官网好评达到**99%**，然而我们利用情感分析得出的结果是**76%**。

## 绘制词云

```python
def draw_wordcloud(text):
    font_path = "‪C:\\Windows\\Fonts\\1.ttf"
    weight = 1000
    height = 1000
    bg_img = imread("jdlogo.png")
    wordcloud = WordCloud(font_path=font_path,
                          width=weight,
                          height=height,
                          mask=bg_img).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
```

![坚果 3手机jd评论词云](https://ws1.sinaimg.cn/large/bd61005egy1g0cw9qfa43j20hs0dcq5a.jpg)

# 结论

对京东商品的评论分析效果还是很不错的，能找出某商品是否值得购买，对好评率会不会有误导性能提出较为明确的判断依据。

改进建议：引入多线程和异步HttpGet，以提升爬虫效率和稳定性，进一步一体化程序，使之成为一项webservice，可以通过网页直接查询该商品是否值得买。

# 完整博客内容

https://tellyouwhat.cn/p/use-python-to-write-a-crawler-crawl-jingdong-commodity-reviews-analyze-emotional-sentiment-and-draw-word-cloud/
