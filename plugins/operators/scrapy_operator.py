from typing import Dict, List, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from scrapy.crawler import CrawlerProcess


class ScrapyOperator(BaseOperator):
    ui_color = '#ffefeb'

    @apply_defaults
    def __init__(self,
                 pipelines: Dict,
                 spider,
                 op_args: Optional[List] = None,
                 op_kwargs: Optional[Dict] = None,
                 **kwargs) -> None:
        self.item_pipelines = pipelines
        self.spider = spider
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        super(ScrapyOperator, self).__init__(**kwargs)

    def execute(self, context: Dict) -> None:
        process = CrawlerProcess(settings={
            'DOWNLOAD_DELAY': .25,
            'ITEM_PIPELINES': self.item_pipelines
        })
        process.crawl(self.spider, *self.op_args, **self.op_kwargs)
        process.start()
