from datetime import datetime
from sqlalchemy import Sequence
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
JOBLIST_ID = Sequence('joblist_id_seq')
JOBLIST_TMP_ID = Sequence('joblist_tmp_id_seq')
JOBLIST_META_ID = Sequence('joblist_meta_id_seq')
JOBLIST_TAG_ID = Sequence('joblist_tag_id_seq')
JOBLIST_LOG_ID = Sequence('joblist_log_id_seq')


class JobList(Base):
    __tablename__ = 'joblist'
    joblist_id = Column(Integer,
                        JOBLIST_ID,
                        primary_key=True,
                        server_default=JOBLIST_ID.next_value())
    company_id = Column(BigInteger)
    company_page_link = Column(String)
    indcat_id = Column(Integer)
    # todo: to be record in another table
    indcat_name = Column(String)
    # todo: if it is adopted whildly, and a table must created
    job_area = Column(String)
    job_id = Column(Integer)
    job_page_link = Column(String)
    job_role = Column(Integer)
    # todo: there must be a source to record where the information is
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobListTmp(Base):
    __tablename__ = 'joblist_tmp'
    joblist_tmp_id = Column(Integer,
                            JOBLIST_TMP_ID,
                            primary_key=True,
                            server_default=JOBLIST_TMP_ID.next_value())
    job_id = Column(Integer)
    keyword = Column(String)
    candi_edu = Column(String)
    candi_exp = Column(String)
    job_hot = Column(String)
    job_name = Column(String)
    job_tags = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobListMeta(Base):
    __tablename__ = 'joblist_meta'
    joblist_meta_id = Column(Integer,
                             JOBLIST_META_ID,
                             primary_key=True,
                             server_default=JOBLIST_META_ID.next_value())
    joblist_id = Column(Integer)
    candi_edu = Column(String)
    candi_exp = Column(String)
    job_hot = Column(String)
    job_name = Column(String)
    job_pay = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobListTag(Base):
    __tablename__ = 'joblist_tag'
    joblist_tag_id = Column(Integer,
                            JOBLIST_TAG_ID,
                            primary_key=True,
                            server_default=JOBLIST_TAG_ID.next_value())
    joblist_id = Column(Integer)
    tag_name = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)
    update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobListLog(Base):
    __tablename__ = 'joblist_log'
    joblist_log_id = Column(Integer,
                            JOBLIST_LOG_ID,
                            primary_key=True,
                            server_default=JOBLIST_LOG_ID.next_value())
    joblist_id = Column(Integer)
    is_changed = Column(Integer)
    create_at = Column(DateTime, default=datetime.utcnow)
