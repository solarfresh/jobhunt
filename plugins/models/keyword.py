from datetime import datetime
from sqlalchemy import Sequence
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
KEYWORD_ID = Sequence('kw_id_seq')
KEYWORD_SEARCH_RELATION_ID = Sequence('kw_search_relation_id_seq')


class Keyword(Base):
    __tablename__ = 'keyword'
    keyword_id = Column(Integer,
                        KEYWORD_ID,
                        primary_key=True,
                        server_default=KEYWORD_ID.next_value())
    keyword = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)


class KeywordSearchRelation(Base):
    __tablename__ = 'kw_search_relation'
    kw_search_relation_id = Column(Integer,
                                   KEYWORD_SEARCH_RELATION_ID,
                                   primary_key=True,
                                   server_default=KEYWORD_SEARCH_RELATION_ID.next_value())
    keyword_id = Column(Integer)
    searched_keyword_id = Column(Integer)
    create_at = Column(DateTime, default=datetime.utcnow)
