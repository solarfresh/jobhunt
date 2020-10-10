from models.keyword import (Keyword, KeywordSearchRelation)
from hooks.sql_hook import SQLHook

jobhunt_hook = SQLHook(sql_conn_id='jobhunt_sql', models={
    'keyword': Keyword,
    'kw_search_relation': KeywordSearchRelation
})
