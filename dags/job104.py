from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators.scrapy_operator import ScrapyOperator
from operators.jobhunt_operator import (TransferJobLisMetaOperator,
                                        TransferJobLisTagOperator,
                                        TransferJobLisLogOperator,
                                        DeleteJobLisTmpOperator)
from crawler.spiders.job104 import (Job104JobListSpider, Job104KeywordSearchRelatedSpider)

# Configuration of DAG

dag_id = "job104"
schedule_interval = None

default_args = {
    'owner': 'scott',
    'depends_on_past': False,
    'email': ['shangyuhuang@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    dag_id,
    start_date=datetime(2020, 10, 9),
    schedule_interval=schedule_interval,
    default_args=default_args)

# Definition of tasks

start_dag = DummyOperator(task_id='start_dag', dag=dag)
end_dag = DummyOperator(task_id='end_dag', dag=dag)

job104_keyword_crawler = ScrapyOperator(
    task_id='job104_keyword_crawler',
    pipelines={
        'crawler.pipelines.job104.Job104KeywordSearchRelatedPipeline': 300
    },
    spider=Job104KeywordSearchRelatedSpider,
    op_kwargs={'keywords': []}
)

job104_joblist_crawler = ScrapyOperator(
    task_id='job104_joblist_crawler',
    pipelines={
        'crawler.pipelines.job104.Job104JobListPipeline': 300
    },
    spider=Job104JobListSpider,
    op_kwargs={'keywords': []}
)

transfer_to_joblist_meta = TransferJobLisMetaOperator(
    task_id='transfer_to_joblist_meta',
    sql_conn_id='jobhunt_sql'
)

transfer_to_joblist_tag = TransferJobLisTagOperator(
    task_id='transfer_to_joblist_tag',
    sql_conn_id='jobhunt_sql'
)

transfer_to_joblist_log = TransferJobLisLogOperator(
    task_id='transfer_to_joblist_log',
    sql_conn_id='jobhunt_sql'
)

delete_joblist_tmp = DeleteJobLisTmpOperator(
    task_id='delete_joblist_tmp',
    sql_conn_id='jobhunt_sql'
)


# Task dependencies

# Successful path
start_dag >> job104_keyword_crawler >> job104_joblist_crawler
job104_joblist_crawler >> (transfer_to_joblist_meta,
                           transfer_to_joblist_tag,
                           transfer_to_joblist_log) >> delete_joblist_tmp
delete_joblist_tmp >> end_dag
# start_dag >> end_dag

# Fail path
