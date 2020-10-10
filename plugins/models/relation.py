from datetime import datetime
from sqlalchemy import Sequence
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
JOBLIST_KEYWORD_ID = Sequence('joblist_keyword_id_seq')


class JobListKeyword(Base):
    __tablename__ = 'joblist_keyword'
    joblist_keyword_id = Column(Integer,
                                JOBLIST_KEYWORD_ID,
                                primary_key=True,
                                server_default=JOBLIST_KEYWORD_ID.next_value())
    joblist_id = Column(Integer)
    keyword_id = Column(Integer)
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
