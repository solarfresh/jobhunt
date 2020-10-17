import logging
import pandas as pd
from crawler.pipelines import BasePipeline
from datetime import datetime
from models import jobhunt_hook
from sqlalchemy.sql.expression import func


class Job104JobListPipeline(BasePipeline):
    def open_spider(self, spider):
        self.joblist_instance_list = []
        # select.order_by(func.random()) # for PostgreSQL, SQLite
        # select.order_by(func.rand()) # for MySQL
        # select.order_by('dbms_random.value') # For Oracle
        keywords_df = jobhunt_hook.query('keyword').order_by(func.random()).limit(250).all().to_pandas()
        if keywords_df.empty:
            self.keywords = ['演算法']
        else:
            self.keywords = [kw for kw in keywords_df['keyword'].values]

        spider.update_start_urls(keywords=self.keywords)

    def close_spider(self, spider):
        joblist_instance_set = set(self.joblist_instance_list)
        for instance in joblist_instance_set:
            # instance_dict = {col.name: getattr(instance, col.name) for col in instance.__table__.columns}
            # query = jobhunt_hook.query('joblist').filter_by(**instance_dict)
            query = jobhunt_hook.query('joblist').filter_by(job_id=instance.job_id)
            if query.scalar():
                instance = query.first()
                instance.update_at = datetime.utcnow()
            else:
                jobhunt_hook.session.add(instance)

        jobhunt_hook.session.commit()

    def process_item(self, item, spider):
        """
        The item is a dict with following key-value pairs
             {
                'keyword': query_params['keyword'],
                'update_at': update_at,
                'candi_exp': exp.css('li::text').get(),
                'candi_edu': edu.css('li::text').get(),
                'job_id': article_attrib['data-job-no'],
                'job_name': article_attrib['data-job-name'],
                'job_role': article_attrib['data-job-ro'],
                'job_area': area.css('li::text').get(),
                'job_hot': article.css('div.b-pos-relative a::text').get(),
                'job_tags': [tag for tag in article.css('div div.job-list-tag span::text').getall()],
                'job_page_link': article.css('div h2 a').attrib['href'].replace('//', 'https://'),
                'company_id': article_attrib['data-cust-no'],
                'company_name': article_attrib['data-cust-name'],
                'company_page_link': company_info['href'].replace('//', 'https://'),
                'indcat_id': article_attrib['data-indcat'],
                'indcat_name': article_attrib['data-indcat-desc']
            }
        """
        self._append_joblist_instance(item)
        self._append_joblist_tmp_instance(item)

    def _append_joblist_instance(self, item):
        instance_dict = {k: item[k] for k in ['company_id', 'company_page_link', 'indcat_id', 'indcat_name',
                                              'job_area', 'job_id', 'job_page_link', 'job_role']}
        instance = jobhunt_hook.models['joblist'](**instance_dict)
        self.joblist_instance_list.append(instance)

    @staticmethod
    def _append_joblist_tmp_instance(item):
        instance_dict = {k: item[k] for k in ['job_id', 'keyword', 'candi_edu', 'candi_exp',
                                              'job_hot', 'job_name', 'job_tags']}
        instance = jobhunt_hook.models['joblist_tmp'](**instance_dict)
        jobhunt_hook.session.add(instance)


class Job104KeywordSearchRelatedPipeline(BasePipeline):
    def open_spider(self, spider):
        keywords_df = jobhunt_hook.query('keyword').all().to_pandas()
        self.kw_search_relation = []
        if keywords_df.empty:
            self.keywords = ['演算法']
        else:
            self.keywords = [kw for kw in keywords_df['keyword'].sample(frac=1).values]

        spider.keywords = keywords_df['keyword'].values
        spider.update_start_urls(keywords=[self.keywords[0]])

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
            instance = jobhunt_hook.models['kw_search_relation'](keyword_id=kw_index,
                                                                 searched_keyword_id=searched_kw_index)

            query = jobhunt_hook.query('kw_search_relation').filter_by(keyword_id=instance.keyword_id,
                                                                       searched_keyword_id=instance.searched_keyword_id)
            if not query.scalar():
                jobhunt_hook.session.add(instance)

        jobhunt_hook.session.commit()

    def process_item(self, item, spider):
        logging.info('Searched relation pair is {}...'.format(item))
        self.kw_search_relation.append(item)
        # To collect new keywords
        if item['searched_keyword'] not in self.keywords:
            self.keywords.append(item['searched_keyword'])
            jobhunt_hook.session.add(jobhunt_hook.models['keyword'](keyword=item['searched_keyword']))
