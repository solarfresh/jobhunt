from hooks.sql_hook import SQLHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from models.joblist import (JobList, JobListLog, JobListMeta, JobListTag, JobListTmp)


class TransferJobLisBaseOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 sql_conn_id,
                 **kwargs):
        super(TransferJobLisBaseOperator, self).__init__(**kwargs)
        self.sql_conn_id = sql_conn_id
        self.session = None
        self.hook = None

    def execute(self, context):
        pass

    def get_hook(self):
        if not self.hook:
            self.hook = SQLHook(
                sql_conn_id=self.sql_conn_id,
                models={
                    'joblist': JobList,
                    'joblist_log': JobListLog,
                    'joblist_meta': JobListMeta,
                    'joblist_tag': JobListTag,
                    'joblist_tmp': JobListTmp
                }
            )
        return self.hook


class TransferJobLisMetaOperator(TransferJobLisBaseOperator):
    """
    1. to obtain joblist_id from job_id
    2. check the existence of records on joblist_meta
    """

    def execute(self, context):
        self.session = self.get_hook()
        joblist_tmp_df = \
            self.session\
            .query('joblist_tmp')\
                .join(self.session.models['joblist'],
                      self.session.models['joblist'].job_id == self.session.models['joblist_tmp'].job_id)\
                .with_entities(self.session.models['joblist'].joblist_id,
                               self.session.models['joblist_tmp'].candi_edu,
                               self.session.models['joblist_tmp'].candi_exp,
                               self.session.models['joblist_tmp'].job_hot,
                               self.session.models['joblist_tmp'].job_name,
                               self.session.models['joblist_tmp'].update_at)\
                .all().to_pandas()
        joblist_tmp_df = joblist_tmp_df.sort_values(by='update_at', ascending=False).drop_duplicates(['joblist_id'])
        for _, row in joblist_tmp_df.iterrows():
            query = self.session.query('joblist_meta').filter_by(joblist_id=row['joblist_id'])
            if query.scalar():
                instance = query.first()
                instance.update_at = row['update_at']
            else:
                instance = self.session.models['joblist_meta'](**row)
                self.session.session.add(instance)

        self.session.session.commit()


class TransferJobLisTagOperator(TransferJobLisBaseOperator):

    def execute(self, context):
        self.session = self.get_hook()
        joblist_tmp_df = \
            self.session\
            .query('joblist_tmp')\
                .join(self.session.models['joblist'],
                      self.session.models['joblist'].job_id == self.session.models['joblist_tmp'].job_id)\
                .with_entities(self.session.models['joblist'].joblist_id,
                               self.session.models['joblist_tmp'].job_tags,
                               self.session.models['joblist_tmp'].update_at)\
                .all().to_pandas()
        joblist_tmp_df = joblist_tmp_df\
            .sort_values(by='update_at', ascending=False)\
            .drop_duplicates(['joblist_id', 'job_tags'])
        for _, row in joblist_tmp_df.iterrows():
            tags = row['job_tags'].split(',')
            for tag in tags:
                query = self.session.query('joblist_tag').filter_by(joblist_id=row['joblist_id'], tag_name=tag)
                if query.scalar():
                    instance = query.first()
                    instance.update_at = row['update_at']
                else:
                    instance = self.session.models['joblist_tag'](joblist_id=row['joblist_id'],
                                                                  tag_name=tag,
                                                                  update_at=row['update_at'])
                    self.session.session.add(instance)

        self.session.session.commit()


class TransferJobLisLogOperator(TransferJobLisBaseOperator):

    def execute(self, context):
        self.session = self.get_hook()
        joblist_tmp_df = \
            self.session\
            .query('joblist_tmp')\
                .join(self.session.models['joblist'],
                      self.session.models['joblist'].job_id == self.session.models['joblist_tmp'].job_id)\
                .with_entities(self.session.models['joblist'].joblist_id,
                               self.session.models['joblist_tmp'].update_at)\
                .all().to_pandas()
        for _, row in joblist_tmp_df.iterrows():
            instance = self.session.models['joblist_tag'](joblist_id=row['joblist_id'],
                                                          # todo: to record joblist is modified or not
                                                          is_changed=0,
                                                          create_at=row['update_at'])
            self.session.session.add(instance)

        self.session.session.commit()


class DeleteJobLisTmpOperator(TransferJobLisBaseOperator):

    def execute(self, context):
        self.session = self.get_hook()
        self.session.query('joblist_tmp').all().delete()
        self.session.session.commit()
