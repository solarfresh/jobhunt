# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict
from sqlalchemy import (create_engine, event, inspect)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class SQLConnect(object):
    def __init__(self,
                 models: Dict[str, Base],
                 dialect='postgresql',
                 user='',
                 passwd='',
                 host='',
                 port='',
                 db=''):
        db_url = {
            'mysql': 'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}',
            'hive': 'hive://{0}:{1}@{2}:{3}/{4}',
            'postgresql': 'postgresql://{0}:{1}@{2}:{3}/{4}',
        }
        db_url = db_url[dialect].format(user, passwd, host, port, db)
        self.engine = create_engine(db_url)
        self.session = sessionmaker(bind=self.engine)()

        """
        self.models = {'table_name': ModelClass,}
        """
        self.models = models

        self.cursors = None
        self.entities = None
        self.model_query = None
        self.session_response = None

        self.model_changes = {}
        event.listen(self.session, 'before_flush', self.record_ops)
        event.listen(self.session, 'before_commit', self.record_ops)
        event.listen(self.session, 'after_commit', self.after_commit)
        event.listen(self.session, 'after_rollback', self.after_rollback)

    ################################################################################################################
    # Customized functions which are not included by sqlalchemy
    ################################################################################################################

    @staticmethod
    def instance2pandas(instances):
        data = [{col.name: getattr(instance, col.name) for col in instance.__table__.columns}
                for instance in instances]
        # data = [instance.__dict__ for instance in instances]
        df = pd.DataFrame(data)
        if '_sa_instance_state' in df.columns:
            df = df.drop('_sa_instance_state', axis=1)
        return df

    def query_and_insert(self, table_name: str, filter_by: list):
        """
        filter_by is a list of dict including instances except id
        to check the existence. If entity does not exist, it will be inserted.
        """
        # todo: it takes lots of time, and we have to search a method to fine tune
        exists = []
        for instance in filter_by:
            query = self.models[table_name].query.filter_by(**instance)
            if not query.scalar():
                self.session.add(self.models[table_name](**instance))
            else:
                exists.append(query.first())

        self.session.commit()
        changes = self.session_response if self.session_response else []
        responses = exists + changes
        return self.instance2pandas(responses)

    def to_pandas(self):
        if self.entities is not None:
            df = pd.DataFrame(columns=self.entities, data=self.cursors)
            self.entities = None
        else:
            df = self.instance2pandas(self.cursors)
        return df

    ################################################################################################################
    # Functions compatible to sqlalchemy
    ################################################################################################################

    def query(self, table_name: str):
        self.model_query = self.models[table_name].query
        return self

    def all(self):
        self.cursors = self.model_query.all()
        return self

    def filter(self, *args):
        self.model_query = self.model_query.filter(*args)
        return self

    def filter_by(self, **kwargs):
        self.model_query = self.model_query.filter_by(**kwargs)
        return self

    def group_by(self, *args):
        self.model_query = self.model_query.group_by(*args)
        return self

    def join(self, *args):
        self.model_query = self.model_query.join(*args)
        return self

    def order_by(self, *args):
        self.model_query = self.model_query.order_by(*args)
        return self

    def outerjoin(self, *args):
        self.model_query = self.model_query.outerjoin(*args)
        return self

    def paginate(self, *args, **kwargs):
        self.model_query = self.model_query.paginate(*args, **kwargs)
        return self

    def update(self, *args):
        self.model_query = self.model_query.update(*args)
        return self

    def with_entities(self, *args, entities=None):
        # There would be a fail once element applies any function
        # In this condition, entities must be assigned
        if entities is not None:
            self.entities = entities
        else:
            self.entities = [arg.property.key for arg in args]
        self.model_query = self.model_query.with_entities(*args)
        return self

    ################################################################################################################
    # Functions compatible to sqlalchemy's mapper events
    # https://docs.sqlalchemy.org/en/13/orm/events.html#mapper-events
    ################################################################################################################

    def record_ops(self, session, flush_context=None, instances=None):
        for targets, operation in ((session.new, 'insert'), (session.dirty, 'update'), (session.deleted, 'delete')):
            for target in targets:
                state = inspect(target)
                key = state.identity_key if state.has_identity else id(target)
                self.model_changes[key] = (target, operation)

    def after_commit(self, session):
        if self.model_changes:
            changes = [target for target, _ in self.model_changes.values()]
            self.session_response = changes
            self.model_changes.clear()

    def after_rollback(self, session):
        self.model_changes.clear()
