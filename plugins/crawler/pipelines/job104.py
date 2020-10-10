import pandas as pd
from itemadapter import ItemAdapter
from crawler.pipelines import BasePipeline
from models import jobhunt_hook


class Job104KeywordPipeline:
    def open_spider(self, spider):
        # keywords will be obtained from db
        keywords = ['演算法']
        spider.update_start_urls(keywords=keywords)
        # save to csv before integrating with db
        self.items = pd.DataFrame()

    def close_spider(self, spider):
        # todo: hard coding should be removed
        self.items.to_csv('/usr/local/airflow/job104keyword.csv', index=False)

    def process_item(self, item, spider):
        self.items = self.items.append(ItemAdapter(item).asdict(), ignore_index=True)
        return item


class Job104KeywordSearchRelatedPipeline(BasePipeline):
    def open_spider(self, spider):
        keywords = ['演算法']
        spider.update_start_urls(keywords=keywords)
        self.keywords = jobhunt_hook.query('keyword').all().cursors
        self.kw_search_relation = jobhunt_hook.query('kw_search_relation').all().cursors
        if not self.keywords:
            spider.update_start_urls(keywords=['演算法'])
        else:
            spider.update_start_urls(keywords=self.keywords)

    def close_spider(self, spider):
        jobhunt_hook.session.commit()

    def process_item(self, item, spider):
        if item['searched_keyword'] not in self.keywords:
            # self.session.add(self.models[table_name](**instance))
            jobhunt_hook.session.add(jobhunt_hook.models['keyword'](keyword=item['searched_keyword']))
        print(item)
