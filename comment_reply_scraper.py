import datetime

import pandas as pd
import selenium
from selenium import webdriver


threshold = 360


def init_driver():
    driver = webdriver.Chrome()
    driver.get("https://news.yahoo.co.jp/")
    return driver


def read_comment_link():
    df = pd.read_csv(
        f'./data/{datetime.date.today()}/article.csv')
    news_info = df[['id', 'comment_count', 'link']].to_dict()
    return news_info


def __main__():
    driver = init_driver()
    news_info = read_comment_link()
    for l in news_info:
        if l['comment_count'] > threshold:
            driver.get(l['link'])
            # driver.find_element()


if __name__ == '__main__':
    __main__()
