import re
import datetime
import os
import pathlib
import traceback

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule



class YahooNewsSpider(CrawlSpider):
    name = "yahoo_news"
    allowed_domains = ["news.yahoo.co.jp"]
    start_urls = ["https://news.yahoo.co.jp/topics/top-picks"]
    spider_opened_time = None

    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//a[@class="newsFeed_item_link"]')), follow=True),
        Rule(LinkExtractor(restrict_xpaths=('//a[contains(@class, "sc-imSsaf")]')), callback='parse_item', follow=False),
        Rule(LinkExtractor(restrict_xpaths=('//li/a[text()="次へ"]')), follow=True),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YahooNewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        return spider
    
    def spider_opened(self, spider):
        self.spider_opened_time = datetime.datetime.now()
        error_log_file = pathlib.Path(f'./yahoo_news_scraper/error_log/{self.spider_opened_time}.log')
        error_log_file.touch()

    def parse_item(self, response):
        try:
            title = response.xpath('//head/title/text()').get().replace(' - Yahoo!ニュース', '')
            body_excerpt = response.xpath('//p[contains(@class,"highLightSearchTarget")]').get()
            if body_excerpt:
                extract_body = re.sub(r'<[^>]*?>', '', body_excerpt)
                formatted_body = re.sub(r'\s', '', extract_body)
            else:
                formatted_body = ''
            link = response.url
            comment_count = response.xpath('//span[contains(@class, "sc-gpEJdM")]/text()').get()
        except Exception as e:
            with open(f"./yahoo_news_scraper/error_log/{self.spider_opened_time}.log", mode='a') as f:
                f.write(f'{response.url}\n')
                f.write(f'message: {e}\n')
                f.write(f'{traceback.format_exc()}')

        yield {
            'title': title,
            'body': formatted_body,
            'link': link,
            'comment_count': comment_count,
        }
# comment
# https://news.yahoo.co.jp/api/public/comment-digest/8c00198b44b8668290298ba7725ceff254ceb1a7

# //a[contains(@class, "sc-imSsaf")]/@href