import os
import re
import datetime
import pathlib

import scrapy
import pandas as pd


class CommentScraperSpider(scrapy.Spider):
    name = "comment_scraper"
    allowed_domains = ["news.yahoo.co.jp"]
    spider_opened_time = None
    scrape_list = []
    comment_dict_list = []
    reply_dict_list = []
    threshold = 360

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CommentScraperSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened,
                                signal=scrapy.signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        try:
            df = pd.read_csv(
                f'./data/{datetime.date.today()}/article.csv')
            self.scrape_list = df["link"][df["comment_count"]
                                          >= self.threshold].tolist()
        except FileNotFoundError:
            print("CSVファイルが存在しません。")
            exit()

    def spider_closed(self, spider):
        comment_df = pd.DataFrame(self.comment_dict_list)
        reply_df = pd.DataFrame(self.reply_dict_list)
        comment_df.to_csv(f"./data/{datetime.date.today()}/comment.csv")
        reply_df.to_csv(f"./data/{datetime.date.today()}/reply.csv")

    def start_requests(self):
        for link in self.scrape_list:
            yield scrapy.Request(f"{link}/comments", self.parse_comment)

    def parse_comment(self, response):
        article_id = response.url.split('/')[-2]

        comment_box = response.xpath(
            '//div[@class="viewableWrap"]//li//article')

        for i, comment in enumerate(comment_box):
            # comment_info
            # data-cl-params="_cl_vmodule:cmt_usr;_cl_link:agbtncl;_cl_position:1;cmt_id:16854380253513.d46e.00043;"
            comment_info = comment.xpath(
                './div[2]//ul[contains(@class, "ThumbsUpThumbsDownButton__Wrapper-bSFbTC")]/li[1]/button[1]/@data-cl-params').get()
            print(comment_info)
            comment_id = re.search(r'cmt_id:(.*?);', comment_info).group(1)

            content = comment.xpath('./div[2]/p/text()').get()
            if not content:
                content = comment.xpath('./div[2]/p/p/text()').get()

            reply_count = comment.xpath(
                './div[2]/div[2]/div[1]/div[1]/div[1]/span/text()').get()
            if not reply_count:
                reply_count = 0

            # save comment
            self.comment_dict_list.append({
                'comment_id': comment_id,
                'content': content,
                'reply_count': reply_count,
                'article_id': article_id,
            })

            # parse reply
            cookies = response.request.headers.getlist('Cookie')
            reply_endpoint = f"https://news.yahoo.co.jp/api/comment/v2/articles/{article_id}/comments/{comment_id}/reply?start=1&results=10&sort=recommendation"
            yield scrapy.Request(reply_endpoint, self.reply_request_handler, cookies=cookies)

    def reply_request_handler(self, response):
        totalResults = response.json()['totalResults']
        article_id = response.url.split('/')[-4]
        comment_id = response.url.split('/')[-2]
        cookies = response.request.headers.getlist('Cookie')
        request_challenges = int(totalResults) // 10 - 1
        for i in range(request_challenges):
            start_num = i * 10 + 1
            reply_endpoint = f"https://news.yahoo.co.jp/api/comment/v2/articles/{article_id}/comments/{comment_id}/reply?start={start_num}&results=10&sort=recommendation"
            yield scrapy.Request(reply_endpoint, self.parse_reply, cookies=cookies)

    def parse_reply(self, response):
        article_id = response.url.split('/')[-4]
        comment_id = response.url.split('/')[-2]
        reply_box = response.json()['comments']
        for reply in reply_box:
            reply_id = reply['ppid']
            content = reply['text']

            self.reply_dict_list.append({
                'reply_id': reply_id,
                'content': content,
                'article_id': article_id,
                'comment_id': comment_id,
            })
