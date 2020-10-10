from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators.scrapy_operator import ScrapyOperator
from crawler.spiders.job104 import (Job104KeywordSpider, Job104KeywordSearchRelatedSpider)

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

# job104_keyword_crawler = ScrapyOperator(
#     task_id='job104_keyword_crawler',
#     pipelines={
#         'crawler.pipelines.job104.Job104KeywordPipeline': 300
#     },
#     spider=Job104KeywordSpider,
#     op_kwargs={'keywords': []}
# )

# Task dependencies

# Successful path
start_dag >> job104_keyword_crawler >> end_dag
# start_dag >> end_dag

# Fail path
