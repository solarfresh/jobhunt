from models.joblist import (JobList, JobListLog, JobListMeta, JobListTag, JobListTmp)
from models.keyword import (Keyword, KeywordSearchRelation)
from models.relation import (JobListKeyword)
from hooks.sql_hook import SQLHook

jobhunt_hook = SQLHook(sql_conn_id='jobhunt_sql', models={
    'joblist': JobList,
    'joblist_log': JobListLog,
    'joblist_meta': JobListMeta,
    'joblist_tag': JobListTag,
    'joblist_tmp': JobListTmp,
    'joblist_keyword': JobListKeyword,
    'keyword': Keyword,
    'kw_search_relation': KeywordSearchRelation
})
