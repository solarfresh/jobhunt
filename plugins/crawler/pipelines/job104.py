import logging
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
        self.kw_search_relation = []
        if keywords_df.empty:
            self.keywords = ['演算法']
        else:
            self.keywords = [kw for kw in keywords_df['keyword'].values]

        spider.update_start_urls(keywords=self.keywords)

    def close_spider(self, spider):
        # To update the table keyword to obtain indices
        jobhunt_hook.session.commit()

        # To convert keywords into indices
        keywords_df = jobhunt_hook.query('keyword').all().to_pandas()
        keyword_index_dict = {row['keyword']: row['keyword_id'] for _, row in keywords_df.iterrows()}

        # To check the existence
        indicing_kw_relation = [(keyword_index_dict[item['keyword']],
                                 keyword_index_dict[item['searched_keyword']])
                                for item in self.kw_search_relation]
        kw_search_relation_df = jobhunt_hook.query('kw_search_relation').all().to_pandas()
        if kw_search_relation_df.empty:
            kw_search_relation_df = pd.DataFrame(columns=['keyword_id', 'searched_keyword_id'])

        for kw_index, searched_kw_index in indicing_kw_relation:
            if kw_search_relation_df[(kw_search_relation_df['keyword_id'] == kw_index) &
                                     (kw_search_relation_df['searched_keyword_id'] == searched_kw_index)].empty:
                instance = jobhunt_hook.models['kw_search_relation'](keyword_id=kw_index,
                                                                     searched_keyword_id=searched_kw_index)
                jobhunt_hook.session.add(instance)

        jobhunt_hook.session.commit()

    def process_item(self, item, spider):
        logging.info('Searched relation pair is {}...'.format(item))
        self.kw_search_relation.append(item)
        # To collect new keywords
        if item['searched_keyword'] not in self.keywords:
            self.keywords.append(item['searched_keyword'])
            jobhunt_hook.session.add(jobhunt_hook.models['keyword'](keyword=item['searched_keyword']))
