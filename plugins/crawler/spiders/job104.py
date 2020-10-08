from datetime import datetime
from scrapy import (Request, Spider)
from scrapy.crawler import CrawlerProcess
from typing import List
from urllib.parse import quote


class Job104KeywordSpider(Spider):
    name = "job104"

    def __init__(self, keywords: List[str], *args, **kwargs):
        year = datetime.now().year - 2
        self.start_urls = [
            'https://www.104.com.tw/jobs/search/?ro=0&keyword={0}&jobsource={1}indexpoc'.format(quote(kw), year)
            for kw in keywords]
        super(Job104KeywordSpider).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        for article in response.css('article'):
            # {'class': 'b-block--top-bord job-list-item b-clearfix js-job-item ', 'data-job-no': '10598582',
            #  'data-job-name': 'AI演算法工程師', 'data-job-ro': '1', 'data-cust-no': '22480876000',
            #  'data-cust-name': '大立光電股份有限公司', 'data-indcat': '1001004002', 'data-indcat-desc': '光學器材製造業',
            #  'data-is-save': '0', 'data-is-apply': '0', 'data-jobsource': '2018indexpoc'}
            attrib = article.attrib
            # print(article.css('div.b-block__left'))
            job_link = article.css('div h2 a').attrib['href'].replace('//', 'https://')
            # todo: to obtain job name with article.css('div h2 a').get()
            company_info = article.css('div ul li a').attrib
            area, exp, edu = article.css('div ul.job-list-intro li')
            print(area.css('li::text').get())
            print(exp.css('li::text').get())
            print(edu.css('li::text').get())
            # tags
            print([tag for tag in article.css('div div.job-list-tag span::text').getall()])
            print(article.css('div.b-pos-relative a::text').get())
            # todo: should prepare item objects


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(Job104KeywordSpider, keywords=['演算法'])
    process.start()
