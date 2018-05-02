# encoding=utf8
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from scipy.misc import imread


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
