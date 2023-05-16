import scrapy


class CommentScraperSpider(scrapy.Spider):
    name = "comment_scraper"
    allowed_domains = ["news.yahoo.co.jp"]
    start_urls = ["https://news.yahoo.co.jp"]

    def parse(self, response):
        pass
