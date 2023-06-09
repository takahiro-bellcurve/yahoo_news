import re
import datetime
import os
import pathlib
import traceback

import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from yahoo_news_scraper.items import YahooNewsScraperItem


class YahooNewsSpider(CrawlSpider):
    name = "yahoo_news"
    allowed_domains = ["news.yahoo.co.jp"]
    start_urls = ["https://news.yahoo.co.jp/topics/top-picks"]
    spider_opened_date = None

    rules = (
        Rule(LinkExtractor(restrict_xpaths=(
            '//a[@class="newsFeed_item_link"]')), follow=True, callback='parse_item'),
        # Rule(LinkExtractor(restrict_xpaths=(
        #     '//a[contains(@class, "sc-imSsaf")]')), callback='parse_item', follow=False),
        Rule(LinkExtractor(restrict_xpaths=(
            '//li/a[text()="次へ"]')), follow=True),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YahooNewsSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened,
                                signal=scrapy.signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        self.spider_opened_date = datetime.date.today()
        error_log_file = pathlib.Path(
            f'./error_log/{self.spider_opened_date}.log')
        error_log_file.touch()

    def parse_item(self, response):
        loader = ItemLoader(item=YahooNewsScraperItem(), response=response)
        try:
            # href="https://news.yahoo.co.jp/articles/45c95a64146d9896e0c234344eb09188d59588e5/images/000"
            href_contain_id = response.xpath(
                '//p[contains(@class,"sc-fOwylK")]/a/@href')
            id = re.search(r'articles/(.*?)/', href_contain_id.get()).group(1)

            title = response.xpath(
                '//head/title/text()').get().replace(' - Yahoo!ニュース', '')
            body_excerpt = response.xpath(
                '//p[contains(@class,"highLightSearchTarget")]').get()
            if body_excerpt:
                extract_body = re.sub(r'<[^>]*?>', '', body_excerpt)
                formatted_body = re.sub(r'\s', '', extract_body)
            else:
                formatted_body = ''
            link = response.url
            comment_count = response.xpath(
                '//span[contains(@class, "sc-jaowzm")]/text()').get()
        except Exception as e:
            with open(f"./yahoo_news_scraper/error_log/{self.spider_opened_date}.log", mode='a') as f:
                f.write(f'{response.url}\n')
                f.write(f'message: {e}\n')
                f.write(f'{traceback.format_exc()}')

        loader.add_value('id', id)
        loader.add_value('title', title)
        loader.add_value('body', formatted_body)
        loader.add_value('link', link)
        loader.add_value('comment_count', comment_count)

        yield loader.load_item()
