from scrapy import (Request, Spider)
from typing import List
from urllib.parse import (parse_qsl, quote, urlencode, urlparse, urlunparse)


class Job104JobListSpider(Spider):
    name = "job104keywordspider"

    def __init__(self, keywords: List[str], *args, **kwargs):
        self.start_urls = [
            'https://www.104.com.tw/jobs/search/?ro=0' \
            '&keyword={0}' \
            '&isnew=30' \
            '&jobsource=2018indexpoc' \
            '&order=11' \
            '&asc=0' \
            '&page=1'.format(quote(kw))
            for kw in keywords]
        super(Job104JobListSpider).__init__(*args, **kwargs)

    def update_start_urls(self, keywords: List[str]):
        self.start_urls = self._build_urls(keywords)
        return self

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        item_nb = 0
        url_info = urlparse(response.url)
        query_params = dict(parse_qsl(url_info.query))
        for article in response.css('article'):
            update_at = article.css('div h2 span::text').get()
            if not update_at:
                continue

            item_nb += 1
            update_at = update_at.strip()
            # {'class': 'b-block--top-bord job-list-item b-clearfix js-job-item ', 'data-job-no': '10598582',
            #  'data-job-name': 'AI演算法工程師', 'data-job-ro': '1', 'data-cust-no': '22480876000',
            #  'data-cust-name': '大立光電股份有限公司', 'data-indcat': '1001004002', 'data-indcat-desc': '光學器材製造業',
            #  'data-is-save': '0', 'data-is-apply': '0', 'data-jobsource': '2018indexpoc'}
            article_attrib = article.attrib

            # todo: to obtain job name with article.css('div h2 a').get()
            # {'href': '//www.104.com.tw/company/agajo2o?jobsource=2018indexpoc', 'target': '_blank',
            #  'title': '公司名：Cino Group_偉斯股份有限公司\n公司住址：新北市汐止區新台五路一段100號18樓（東方科學園區，鄰宏碁總部）'}
            # company_title = company_info['title'].split('\n')
            # company_name = company_title[0].split('：')[-1] if company_title[0] else ''
            # company_address = company_title[1].split('：')[-1] if company_title[1] else ''
            company_info = article.css('div ul li a').attrib
            area, exp, edu = article.css('div ul.job-list-intro li')
            yield {
                'keyword': query_params['keyword'],
                'update_at': update_at,
                'candi_exp': exp.css('li::text').get(),
                'candi_edu': edu.css('li::text').get(),
                'job_id': article_attrib['data-job-no'],
                'job_name': article_attrib['data-job-name'],
                'job_role': article_attrib['data-job-ro'],
                'job_area': area.css('li::text').get(),
                'job_hot': article.css('div.b-pos-relative a::text').get(),
                'job_tags': ','.join([tag for tag in article.css('div div.job-list-tag span::text').getall()]),
                'job_page_link': article.css('div h2 a').attrib['href'].replace('//', 'https://'),
                'company_id': article_attrib['data-cust-no'],
                'company_name': article_attrib['data-cust-name'],
                'company_page_link': company_info['href'].replace('//', 'https://'),
                'indcat_id': article_attrib['data-indcat'] if article_attrib['data-indcat'] else None,
                'indcat_name': article_attrib['data-indcat-desc']
            }

        if item_nb:
            query_params['page'] = str(int(query_params['page']) + 1)
            url_info = url_info._replace(query=urlencode(query_params))
            next_url = urlunparse(url_info)
            yield Request(url=next_url, callback=self.parse)

    @staticmethod
    def _build_urls(keywords: List[str]):
        return [
            'https://www.104.com.tw/jobs/search/?ro=0' \
            '&keyword={0}' \
            '&jobsource=2018indexpoc' \
            '&order=11' \
            '&asc=0' \
            '&page=1'.format(quote(kw))
            for kw in keywords]


class Job104KeywordSearchRelatedSpider(Job104JobListSpider):
    name = "job104keywordsearchrelatedspider"

    def __init__(self, keywords: List[str], *args, **kwargs):
        self.keywords = keywords
        super(Job104KeywordSearchRelatedSpider, self).__init__(keywords, *args, **kwargs)

    def parse(self, response):
        next_query_keywords = []
        for rel_kw in response.css('div#search-relative p a::text'):
            url_info = urlparse(response.url)
            query_params = dict(parse_qsl(url_info.query))
            searched_keyword = rel_kw.get().strip()
            yield {'keyword': query_params['keyword'],
                   'searched_keyword': searched_keyword}

            if searched_keyword not in self.keywords:
                next_query_keywords.append(searched_keyword)
                self.keywords.append(searched_keyword)

        if next_query_keywords:
            for next_url in self._build_urls(next_query_keywords):
                yield Request(url=next_url, callback=self.parse)
