import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

today = datetime.date.today()

settings = get_project_settings()

settings.set('FEED_URI', f'./data/{today}/article.csv')
process = CrawlerProcess(settings)
process.crawl('yahoo_news')
process.start()

settings = get_project_settings()
process.crawl('comment_scraper')

process.start()
