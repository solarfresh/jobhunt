import pandas as pd
from airflow.hooks.base_hook import BaseHook
from sqlalchemy import (create_engine, event, inspect)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict

Base = declarative_base()


class SQLHook(BaseHook):
    cursors = None
    entities = None
    model_changes = {}
    model_query = None

    def __init__(self,
                 models: Dict[str, Base],
                 sql_conn_id: str):

        """
        self.models = {'table_name': ModelClass,}
        """
        self.models = models
        self.sql_conn_id = sql_conn_id
        self.session = sessionmaker(bind=self.get_sqlalchemy_engine())()

        event.listen(self.session, 'before_flush', self.record_ops)
        event.listen(self.session, 'before_commit', self.record_ops)
        event.listen(self.session, 'after_commit', self.after_commit)
        event.listen(self.session, 'after_rollback', self.after_rollback)

    def get_conn(self):
        """Returns a connection object
        """
        db = self.get_connection(self.sql_conn_id)
        return self.connector.connect(
            host=db.host,
            port=db.port,
            username=db.login,
            schema=db.schema)

    def get_uri(self):
        conn = self.get_connection(self.sql_conn_id)
        login = ''
        if conn.login:
            login = '{conn.login}:{conn.password}@'.format(conn=conn)
        host = conn.host
        if conn.port is not None:
            host += ':{port}'.format(port=conn.port)
        uri = '{conn.conn_type}://{login}{host}/'.format(
            conn=conn, login=login, host=host)
        if conn.schema:
            uri += conn.schema
        return uri

    def get_sqlalchemy_engine(self, engine_kwargs=None):
        if engine_kwargs is None:
            engine_kwargs = {}
        return create_engine(self.get_uri(), **engine_kwargs)

    ################################################################################################################
    # Customized functions which are not included by sqlalchemy
    ################################################################################################################

    def query_and_insert(self, table_name: str, filter_by: list):
        """
        filter_by is a list of dict including instances except id
        to check the existence. If entity does not exist, it will be inserted.
        """
        # todo: it takes lots of time, and we have to search a method to fine tune
        exists = []
        for instance in filter_by:
            query = self.query(table_name).filter_by(**instance)
            if not query.scalar():
                self.session.add(self.models[table_name](**instance))
            else:
                exists.append(query.first())

        self.session.commit()
        # changes = self.session_response if self.session_response else []
        # responses = exists + changes
        # return self.instance2pandas(responses)

    @staticmethod
    def instance2pandas(instances):
        if not instances:
            return pd.DataFrame([])

        data = [{col.name: getattr(instance, col.name) for col in instance.__table__.columns}
                for instance in instances]
        # data = [instance.__dict__ for instance in instances]
        df = pd.DataFrame(data)
        if '_sa_instance_state' in df.columns:
            df = df.drop('_sa_instance_state', axis=1)
        return df

    def to_pandas(self):
        if not self.cursors:
            return pd.DataFrame([])

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
        self.model_query = self.session.query(self.models[table_name])
        return self

    def all(self):
        self.cursors = self.model_query.all()
        return self

    def delete(self):
        self.model_query = self.model_query.delete()
        return self

    def filter(self, *args):
        self.model_query = self.model_query.filter(*args)
        return self

    def filter_by(self, **kwargs):
        self.model_query = self.model_query.filter_by(**kwargs)
        return self

    def first(self):
        return self.model_query.first()

    def group_by(self, *args):
        self.model_query = self.model_query.group_by(*args)
        return self

    def limit(self, *args):
        self.model_query = self.model_query.limit(*args)
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

    def scalar(self):
        return self.model_query.scalar()

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
