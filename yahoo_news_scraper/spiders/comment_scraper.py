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
    scrape_target_dict = []
    comment_dict_list = []
    reply_dict_list = []
    page_nation_memory = 0
    threshold = 360
    cookies = {
        'XB': "7mqccf9hq2tfe&b=3&s=3v",
        '_n': "cGqXa8MFQs3ITa7NVfN3SI_uPNOsj-OkAAq89Sw8WzB3djlqQuW7m01ihhrp0XJOtv6zutHGqeV1bSR7GIj_Of6iGdgOBqmtrOg_rAiTUxv2TVpTQy_-dojDQDCqTXhB2pZybSFd2Z5a9ZC5o3d0WFsFCQVaAgzV1FFeHMH6OevhwhGJKqsCWyG4FpT5QGUeSYU5M_GQxe5zFv4CQBU8olXKb2tVs3oc3DWM5mfpQMeFXRvX6EwIyQbEmlYMbUyefyrst5PZlq9tgM2gUkLgGWizZxPDNedwhzNSpzggqDuto6uvDtixmBMDC7G7W1hBlpSkUFDoN4UTZTe5Oygks50WuKspjMtpjzY8V9Q65dv8YUtNaMaQ_fwuZym8w32p6AEc8IDU_FlqbWRWgFFAXLPTj2kJQ2qiZyKCHgDOB9-k0nzl-Kn4oy1BYSvF81rwR9KwTB4nn-S8zPYRjXyOL--Mz2uTgoPVfhXpc6-KLyboGFqHTRGWDdQ1Ffd_1poscZuaoyjeWnrhuwKtvmWBO_0nMM5ADZ-Q0CE_0_JzrBwyBsSePcBJpJT2G3gnYu4raFPO7pgqwW-X6aCM1ty9X4-H0dMFoBVjdad3MI1-C6HhyCMhnaz2sv6MfZD-AzAaZuZ0J3qhhqZTcQFf-TYP9BhIafX6vccS524fjvmlRiTUqxmWBq_QRT60kYo0uacUeZXmGVucBwHui5TcjbAB9YhjYywEpe5HCBc9-qehaFYOipFZTQF3XlYKyVGJANw5FlpxdjDtblyoNB9MsSTrBmDzNdrbb-HQkXVh9xZYat4SN-cyRxYBfY1Dtl6ZmoWCIAhvmh7WQLec4DY-4XfNjc2S5DZ6ySCOQqOz8jXtYD_9TIsz435swHLh-L8_piodkCSQ9BsmRyXan0SFyR1KMRGrtYXUpYIruH3Mvt-RhduzN6eXBfwGqjWaZe69tZRZjiSFydar7wHJrk0jXqeWtJcnsQCS9vgPt4q3V-xsEHbJ-OqJ5m_lSODenY4h2_VoWutvZgSFNI11uQG6S9pjXt8oGxN-DkiovExKNF1StrRZ22Z6WGds7weARqLBYBtm0iymkn2EDH8JUv1qJtVX-5Rt-iJWq2hePH4yxb503K6YjCSj-IIIDuAQYprh4VZi.3",
        'T': ".4ZDkB.goMkBJeLgOnH1eOS&sk=DAAOLnow6pGdUB&ks=EAApNtfrxavZP5vJ8sJDIlm9w--&kt=EAAyqvRMdcXeWLgJYJ2LNKORA--&ku=FAAMEUCIB9lnDsYGzGRCUpYkQq4eXKsNu8bLdVtK1ZTP_fAbbazAiEA.CskZYLain.sZ7O98zo_8l_wrRtjQYYN8uyK935jaNM-~B&d=Y3MBAXRpcAFGQ2loMEQBYQFRQUUBZwFGSkxOR1NSRFNIQUo1U1VONEZQSk9aUzZWTQFzYwF5Y29ubmVjdHYyAXp6AS40WkRrQkEySg--",
        'SSL': "v=1&s=cgWDdkN7aM_Bcx2RYoMm_kcqRExE9OEzNuF95_q4U6tQZ5_PBDrAajhP52l0wyZC7w3d5QsH63FniZevzOEQiQ--&kv=0",
        'Y': "1&n=clv0a840abgpc&l=5kaak_rzzzrqsz/o&p=0000000000000000&r=v7&lg=ja-JP&intl=jp",
        'A': "7mqccf9hq2tfe&t=1671525870&u=1678614079&sd=B&sc=off&v=1&d=C08MKWPROjfMKsVM4lFIZnIAuBFORO2QAZtRTXpA7YWoM7uMXMJotGet6P1v8XBwpZ4NgpQmqQd1oHMDF4ZEKN7I6Me1WgFiYHEnRfj3L/ry0/CEdWbp/WO5WJq9JonNlGGzsDB8ls0OM69t/0",
        'XA': "7mqccf9hq2tfe&t=1671525870&u=1678614079&sd=B&sc=off&v=1&d=C08MKWPROjfMKsVM4lFIZnIAuBFORO2QAZtRTXpA7YWoM7uMXMJotGet6P1v8XBwpZ4NgpQmqQd1oHMDF4ZEKN7I6Me1WgFiYHEnRfj3L/ry0/CEdWbp/WO5WJq9JonNlGGzsDB8ls0OM69t/0",
        'JV': "A_KrK2QAAIIetE5FdCTCM3KYEKwscrUK0Hmbskn6TK_heFPnNonoi8bzJUT6njoLVaA6fjZoUR14bOqfoUls_IMjFLcjIo5qhlOA-adMJVYU_TCpx11sQdKy3sJNQ73SmF5cPezYb8qmrtxtB2xOYNXahWAYotGuuUMqMhYIL6RmNSaT7RpFqDVhPpu77xTlP6UWakYndPZEQPL4NmwC7E8QLU_z614zv-5dVFLiBS7d2Ded8_i3VUK9fsYOKGI9lOOnQoPIC63zQejkoXtNVwW9viiMScjrHKJEbw703dKCF1HVvOnU8agsUkGKObcCx4ShfLDxzD7Oun2Syh85MfbX_T1pdQ9ZE1uaihT-v62sATVnGKXkwKFvC3LfBa5y_e_8WhNy2uJR6ubUxPYzZy-I5PZ6BhRe6JmCiSWbKY58I0zx8OZO3Xy7z-yeM0A8NcfPyqU492lyAOo6cnCHaLY26NxX6jVYkHcv9lSev0RdgWU35YLkUECVL6ZAqr9HNFIMqNfGHBNuolP9GE5ZuDZ2n_MXLLFWt4K4wytLSRTy7PjTsbBnOKeajhpGjT8AOZtDySvxUAu2_oU2SS931MS4NiLFuFZw_v1IgweQ9ilnc0IJug&v=2"
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CommentScraperSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened,
                                signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed,
                                signal=scrapy.signals.spider_closed)
        return spider

    def spider_opened(self):
        try:
            df = pd.read_csv(
                f'./data/{datetime.date.today()}/article.csv')
            # comment_countとidを含むdfからidとcomment_countのdictを作成
            self.scrape_target_dict = df[['id', 'comment_count']].to_dict(
                orient='records')
        except FileNotFoundError:
            print("CSVファイルが存在しません。")
            exit()

    def spider_closed(self):
        print("spider_closed")
        comment_df = pd.DataFrame(self.comment_dict_list)
        reply_df = pd.DataFrame(self.reply_dict_list)
        comment_df.to_csv(
            f"./data/{datetime.date.today()}/comment.csv", index=False)
        reply_df.to_csv(
            f"./data/{datetime.date.today()}/reply.csv", index=False)

    def start_requests(self):
        for l in self.scrape_target_dict:
            id = l['id']
            comment_count = l['comment_count']
            print(f"scrape {id} {comment_count}件")
            for i in range(int(comment_count) // 10):
                self.page_nation_memory += 1
                scrape_url = f"https://news.yahoo.co.jp/articles/{id}/comments?page={i}"
                yield scrapy.Request(scrape_url, self.parse_comment)

    def parse_comment(self, response):
        # response内容を書き出す
        # with open(f'./data/{datetime.date.today()}/comment.html', 'wb') as f:
        #     f.write(response.body)
        print("parse_comment")

        article_id = response.url.split('/')[-2]

        comment_box = response.xpath(
            '//article[contains(@class, "sc-gJJlYn")]')

        for i, comment in enumerate(comment_box):
            # comment_info
            # data-cl-params="_cl_vmodule:cmt_usr;_cl_link:agbtncl;_cl_position:1;cmt_id:16854380253513.d46e.00043;"
            # href https://news.yahoo.co.jp/comment/violation/?pid=news_user&amp;tid=6687a741defb2a7511247e4125f3681cb25c1e38&amp;cid=16863155576955.7ea5.00047&amp;.done=https%3A%2F%2Fnews.yahoo.co.jp%2Farticles%2F6687a741defb2a7511247e4125f3681cb25c1e38%2Fcomments
            href_contain_comment_id = comment.xpath(
                './/li[contains(@class, "sc-cmEGac")][2]/a/@href').get()
            print(href_contain_comment_id)
            comment_id = re.search(
                r'cid=(.*?)&', href_contain_comment_id).group(1)

            content = comment.xpath('./div[2]/p/text()').get()
            if not content:
                content = comment.xpath('./div[2]/p/p/text()').get()

            reply_count = comment.xpath(
                './/span[contains(@class, "sc-jCwinE")]/text()').get()
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
            # print("/////////////////////////////////////////////////////////////")
            # cookies = response.request.headers.getlist('Cookie')
            # print(cookies)
            # print("/////////////////////////////////////////////////////////////")
            # header = {
            #     'referer': response.url,
            #     'usertoken': "6HeDZAAAAADTegq43ud6EdMo6KFOJV-iOoxCOCJvfJO8IR6SxO_3SG2h1lzAuvIlP_2m9npYmO4yoBylp8IC3CJNlOJ4ufdI"
            # }
            # reply_endpoint = f"https://news.yahoo.co.jp/api/comment/v2/articles/{article_id}/comments/{comment_id}/reply?start=1&results=10&sort=recommendation"
            # yield scrapy.Request(reply_endpoint, self.reply_request_handler, cookies=self.cookies, headers=header) if reply_count else None

    def reply_request_handler(self, response):
        totalResults = response.json()['totalResults']
        article_id = response.url.split('/')[-4]
        comment_id = response.url.split('/')[-2]
        # cookies = response.request.headers.getlist('Cookie')
        request_challenges = int(totalResults) // 10 - 1
        for i in range(request_challenges):
            header = {
                'referer': response.url,
                'usertoken': "6HeDZAAAAADTegq43ud6EdMo6KFOJV-iOoxCOCJvfJO8IR6SxO_3SG2h1lzAuvIlP_2m9npYmO4yoBylp8IC3CJNlOJ4ufdI"
            }
            start_num = i * 10 + 1
            reply_endpoint = f"https://news.yahoo.co.jp/api/comment/v2/articles/{article_id}/comments/{comment_id}/reply?start={start_num}&results=10&sort=recommendation"
            yield scrapy.Request(reply_endpoint, self.parse_reply, cookies=self.cookies, headers=header)

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
