import pandas as pd
from itemadapter import ItemAdapter


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
