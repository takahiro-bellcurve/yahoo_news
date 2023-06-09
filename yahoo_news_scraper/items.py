# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YahooNewsScraperItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    link = scrapy.Field()
    comment_count = scrapy.Field()
