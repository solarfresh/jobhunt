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
        keywords_df = jobhunt_hook.query('keyword').all().to_pandas()
        self.kw_search_relation = jobhunt_hook.query('kw_search_relation').all().to_pandas()
        if keywords_df.empty:
            self.keywords = ['演算法']
        else:
            self.keywords = [kw for kw in keywords_df['keyword'].values]

        spider.update_start_urls(keywords=self.keywords)

    def close_spider(self, spider):
        jobhunt_hook.session.commit()

    def process_item(self, item, spider):
        print(item)
        # To collect new keywords
        if item['searched_keyword'] not in self.keywords:
            self.keywords.append(item['searched_keyword'])
            jobhunt_hook.session.add(jobhunt_hook.models['keyword'](keyword=item['searched_keyword']))
